import os
from typing import List, Optional
from portfolio.chains.evm import EVMChain

CHAINS: List[EVMChain] = [
    EVMChain(
        name="Ethereum",
        symbol="ethereum",
        rpc_env_key="ETH_RPC_URL",
        native_symbol="ETH",
    ),
    EVMChain(
        name="Arbitrum",
        symbol="arbitrum",
        rpc_env_key="ARB_RPC_URL",
        native_symbol="ETH",
    ),
    EVMChain(
        name="Binance Smart Chain",
        symbol="bsc",
        rpc_env_key="BSC_RPC_URL",
        native_symbol="BNB",
    ),
    EVMChain(
        name="Polygon",
        symbol="polygon",
        rpc_env_key="POLYGON_RPC_URL",
        native_symbol="MATIC",
    ),
    EVMChain(
        name="Optimism",
        symbol="optimism",
        rpc_env_key="OPTIMISM_RPC_URL",
        native_symbol="ETH",
    ),
    EVMChain(
        name="Base",
        symbol="base",
        rpc_env_key="BASE_RPC_URL",
        native_symbol="ETH",
    ),
    EVMChain(
        name="Sonic",
        symbol="sonic",
        rpc_env_key="SONIC_RPC_URL",
        native_symbol="S",
    ),
    EVMChain(
        name="Avalanche",
        symbol="avalanche",
        rpc_env_key="AVALANCHE_RPC_URL",
        native_symbol="AVAX",
    ),
]


def get_enabled_chains():
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
