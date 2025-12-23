import os
import logging
from typing import List

from portfolio.wallets.evm import fetch_eth_balance
from portfolio.wallets.evm_tokens import fetch_erc20_holdings
from portfolio.wallets.erc20_discovery import discover_erc20_contracts
from portfolio.wallets.covalent import fetch_covalent_erc20_holdings
from portfolio.wallets.alchemy import fetch_alchemy_erc20_holdings
from portfolio.models import Holding
from portfolio.cache.sqlite import (
    init_db,
    get_cached_holdings,
    set_cached_holdings,
)

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 300


class EVMChain:
    def __init__(
        self,
        symbol: str,
        name: str,
        rpc_env_key: str,
        native_symbol: str,
        chain_id: int,
    ):
        self.symbol = symbol
        self.name = name
        self.rpc_env_key = rpc_env_key
        self.native_symbol = native_symbol
        self.chain_id = chain_id

        init_db()

    def is_enabled(self) -> bool:
        return bool(os.getenv(self.rpc_env_key))

    @property
    def rpc_url(self) -> str:
        return os.getenv(self.rpc_env_key)

    def fetch_holdings(self, wallet_address: str) -> List[Holding]:
        cached = get_cached_holdings(
            wallet=wallet_address,
            chain=self.symbol,
            max_age_seconds=CACHE_TTL_SECONDS,
        )

        if cached is not None:
            logger.info(
                "Using cached holdings for %s on %s",
                wallet_address,
                self.name,
            )
            return cached

        holdings: List[Holding] = []

        try:
            native_balance = fetch_eth_balance(wallet_address, self.rpc_url)
            if native_balance > 0:
                holdings.append(
                    Holding(
                        symbol=self.native_symbol,
                        amount=float(native_balance),
                        cost_basis=0.0,
                        is_erc20=False,
                        chain=self.symbol,
                    )
                )
        except Exception:
            logger.exception(
                "Failed fetching native balance on %s",
                self.symbol,
            )

        # Covalent (primary)
        erc20_holdings = fetch_covalent_erc20_holdings(
            wallet_address=wallet_address,
            chain_id=self.chain_id,
            chain_symbol=self.symbol,
        )

        # Alchemy (secondary)
        if not erc20_holdings:
            erc20_holdings = fetch_alchemy_erc20_holdings(
                wallet_address=wallet_address,
                chain=self.name,
            )

        # RPC logs (last resort)
        if not erc20_holdings:
            try:
                token_contracts = discover_erc20_contracts(
                    wallet_address=wallet_address,
                    rpc_url=self.rpc_url,
                    chain_id=self.chain_id,
                )
            except Exception:
                logger.exception(
                    "ERC-20 discovery failed on %s",
                    self.symbol,
                )
                token_contracts = []

            erc20_holdings = fetch_erc20_holdings(
                wallet_address=wallet_address,
                rpc_url=self.rpc_url,
                token_contracts=token_contracts,
                chain_symbol=self.symbol,
            )

        holdings.extend(erc20_holdings)

        set_cached_holdings(
            wallet=wallet_address,
            chain=self.symbol,
            holdings=holdings,
        )

        return holdings
