import os
from typing import List, Optional

from portfolio.chains.evm import EVMChain


CHAINS: List[EVMChain] = [
    EVMChain(
        name="Ethereum",
        symbol="ethereum",
        rpc_env_key="ETH_RPC_URL",
        native_symbol="ETH",
        chain_id=1,
    ),
    EVMChain(
        name="Arbitrum",
        symbol="arbitrum",
        rpc_env_key="ARB_RPC_URL",
        native_symbol="ETH",
        chain_id=42161,
    ),
    EVMChain(
        name="Binance Smart Chain",
        symbol="bsc",
        rpc_env_key="BSC_RPC_URL",
        native_symbol="BNB",
        chain_id=56,
    ),
    EVMChain(
        name="Polygon",
        symbol="polygon",
        rpc_env_key="POLYGON_RPC_URL",
        native_symbol="MATIC",
        chain_id=137,
    ),
    EVMChain(
        name="Optimism",
        symbol="optimism",
        rpc_env_key="OPTIMISM_RPC_URL",
        native_symbol="ETH",
        chain_id=10,
    ),
    EVMChain(
        name="Base",
        symbol="base",
        rpc_env_key="BASE_RPC_URL",
        native_symbol="ETH",
        chain_id=8453,
    ),
    EVMChain(
        name="Sonic",
        symbol="sonic",
        rpc_env_key="SONIC_RPC_URL",
        native_symbol="S",
        chain_id=146,
    ),
    EVMChain(
        name="Avalanche",
        symbol="avalanche",
        rpc_env_key="AVALANCHE_RPC_URL",
        native_symbol="AVAX",
        chain_id=43114,
    ),
]


def get_enabled_chains() -> List[EVMChain]:
    enabled = os.getenv("ENABLED_CHAINS")

    if not enabled:
        return [chain for chain in CHAINS if chain.is_enabled()]

    enabled_names = {name.strip().lower() for name in enabled.split(",")}

    return [
        chain
        for chain in CHAINS
        if chain.name.lower() in enabled_names and chain.is_enabled()
    ]


def get_chain_by_symbol(symbol: str) -> Optional[EVMChain]:
    symbol = symbol.lower()
    for chain in CHAINS:
        if chain.symbol == symbol:
            return chain
    return None
