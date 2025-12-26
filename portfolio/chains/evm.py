import os
import logging
from typing import List

from portfolio.wallets.alchemy import fetch_erc20_holdings
from portfolio.wallets.evm import fetch_eth_balance
from portfolio.models import Holding
from portfolio.cache.sqlite import init_db, get_cached_holdings, set_cached_holdings

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 300

FALLBACK_RPCS = {
    "ethereum": "https://rpc.ankr.com/eth",
    "arbitrum": "https://rpc.ankr.com/arbitrum",
    "polygon": "https://rpc.ankr.com/polygon",
    "optimism": "https://rpc.ankr.com/optimism",
    "base": "https://rpc.ankr.com/base",
}

ALCHEMY_BASE = {
    "ethereum": "https://eth-mainnet.g.alchemy.com/v2/",
    "arbitrum": "https://arb-mainnet.g.alchemy.com/v2/",
    "polygon": "https://polygon-mainnet.g.alchemy.com/v2/",
    "optimism": "https://opt-mainnet.g.alchemy.com/v2/",
    "base": "https://base-mainnet.g.alchemy.com/v2/",
}


class EVMChain:
    def __init__(self, name, symbol, rpc_env_key, native_symbol, chain_id):
        self.name = name
        self.symbol = symbol
        self.rpc_env_key = rpc_env_key
        self.native_symbol = native_symbol
        self.chain_id = chain_id
        init_db()

    def is_enabled(self) -> bool:
        return bool(
            os.getenv(self.rpc_env_key)
            or os.getenv("ALCHEMY_API_KEY")
            or self.symbol in FALLBACK_RPCS
        )

    def _get_rpc_url(self) -> str | None:
        if os.getenv(self.rpc_env_key):
            return os.getenv(self.rpc_env_key)

        # Alchemy
        alchemy_key = os.getenv("ALCHEMY_API_KEY")
        if alchemy_key and self.symbol in ALCHEMY_BASE:
            return f"{ALCHEMY_BASE[self.symbol]}{alchemy_key}"

        # Public fallback
        return FALLBACK_RPCS.get(self.symbol)

    def fetch_holdings(self, wallet_address: str) -> List[Holding]:
        cached = get_cached_holdings(
            wallet_address,
            self.symbol,
            CACHE_TTL_SECONDS,
        )
        if cached:
            return cached

        holdings: List[Holding] = []

        rpc_url = self._get_rpc_url()
        if not rpc_url:
            logger.error("No RPC available for %s", self.symbol)
            return holdings

        # Native token
        try:
            native_amount = fetch_eth_balance(wallet_address, rpc_url)
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
            logger.exception("Native balance fetch failed for %s", self.symbol)

        # ERC-20 tokens
        try:
            erc20s = fetch_erc20_holdings(wallet_address, self.symbol)
            holdings.extend(erc20s)
        except Exception:
            logger.exception("ERC20 fetch failed for %s", self.symbol)

        set_cached_holdings(wallet_address, self.symbol, holdings)
        return holdings
