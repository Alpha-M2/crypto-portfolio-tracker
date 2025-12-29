import os
from typing import List
from portfolio.chains.evm import EVMChain

CHAINS: List[EVMChain] = [
    EVMChain("Ethereum", "ethereum", "ETH_RPC_URL", 1),
    EVMChain("Arbitrum", "arbitrum", "ARB_RPC_URL", 42161),
    EVMChain("Polygon", "polygon", "POLYGON_RPC_URL", 137),
    EVMChain("Optimism", "optimism", "OPTIMISM_RPC_URL", 10),
    EVMChain("Base", "base", "BASE_RPC_URL", 8453),
    EVMChain("BSC", "bsc", "BSC_RPC_URL", 56),
]


def get_enabled_chains() -> List[EVMChain]:
    enabled = os.getenv("ENABLED_CHAINS")
    if not enabled:
        return [c for c in CHAINS if c.is_enabled()]

    allowed = {x.strip().lower() for x in enabled.split(",")}
    return [c for c in CHAINS if c.symbol in allowed and c.is_enabled()]
