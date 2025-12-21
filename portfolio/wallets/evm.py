from portfolio.chains.registry import get_chain_by_symbol
from portfolio.chains.provider import AbstractChainProvider
from portfolio.wallets.utils import eth_balance_to_holding


def fetch_native_balance(wallet_address: str, chain_symbol: str = "ETH"):
    chain = get_chain_by_symbol(chain_symbol)
    if not chain:
        raise ValueError(f"Unsupported chain: {chain_symbol}")
    provider = AbstractChainProvider(chain)
    return provider.fetch_native_balance(wallet_address)


def fetch_erc20_holdings(wallet_address: str, chain_symbol: str = "ETH"):
    chain = get_chain_by_symbol(chain_symbol)
    if not chain:
        raise ValueError(f"Unsupported chain: {chain_symbol}")
    provider = AbstractChainProvider(chain)
    return provider.fetch_erc20_holdings(wallet_address)
