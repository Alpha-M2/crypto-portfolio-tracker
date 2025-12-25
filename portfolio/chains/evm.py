import os
import logging
from typing import List

from portfolio.wallets.alchemy import fetch_erc20_holdings
from portfolio.wallets.evm import fetch_eth_balance
from portfolio.models import Holding
from portfolio.cache.sqlite import init_db, get_cached_holdings, set_cached_holdings

logger = logging.getLogger(__name__)
CACHE_TTL_SECONDS = 300


class EVMChain:
    def __init__(self, name, symbol, rpc_env_key, native_symbol, chain_id):
        self.name = name
        self.symbol = symbol
        self.rpc_env_key = rpc_env_key
        self.native_symbol = native_symbol
        self.chain_id = chain_id
        init_db()

    def is_enabled(self):
        return bool(os.getenv(self.rpc_env_key))

    def fetch_holdings(self, wallet_address: str) -> List[Holding]:
        cached = get_cached_holdings(wallet_address, self.symbol, CACHE_TTL_SECONDS)
        if cached:
            return cached

        holdings: List[Holding] = []

        # Native balance
        try:
            native_amount = fetch_eth_balance(wallet_address, self.symbol)
            if native_amount > 0:
                holdings.append(
                    Holding(
                        symbol=self.native_symbol,
                        amount=native_amount,
                        chain=self.symbol,
                        is_erc20=False,
                    )
                )
        except Exception:
            logger.exception("Native balance fetch failed")

        # ERC-20 tokens
        try:
            erc20s = fetch_erc20_holdings(wallet_address, self.symbol)
            holdings.extend(erc20s)
        except Exception:
            logger.exception("ERC20 fetch failed")

        set_cached_holdings(wallet_address, self.symbol, holdings)
        return holdings
