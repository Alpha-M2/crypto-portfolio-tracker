from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Chain:
    name: str
    symbol: str
    rpc_env_var: str
    coingecko_id: str


# Add your RPC environment variable names here
CHAINS = [
    Chain(
        name="Ethereum",
        symbol="ETH",
        rpc_env_var="ALCHEMY_ETH_RPC_URL",
        coingecko_id="ethereum",
    ),
    Chain(
        name="Arbitrum",
        symbol="ARB",
        rpc_env_var="ALCHEMY_ARB_RPC_URL",
        coingecko_id="arbitrum-one",
    ),
    Chain(
        name="Binance Smart Chain",
        symbol="BSC",
        rpc_env_var="BSC_RPC_URL",
        coingecko_id="binance-smart-chain",
    ),
    Chain(
        name="Polygon",
        symbol="MATIC",
        rpc_env_var="POLYGON_RPC_URL",
        coingecko_id="polygon",
    ),
]


def get_chain_by_symbol(symbol: str):
    for c in CHAINS:
        if c.symbol.lower() == symbol.lower():
            return c
    return None
