def canonical_symbol(symbol: str) -> str:
    """
    Only minimal normalization.
    We do NOT merge WETH → ETH anymore.
    Users want to see them separately.
    """
    if not symbol:
        return "UNKNOWN"
    return symbol.strip().upper()


def asset_key(position: dict) -> tuple:
    """
    Unique key = (canonical_symbol, chain, contract_address or 'native')
    This ensures:
    - Native ETH on different chains remain separate
    - WETH and ETH never merge
    - Same token on different chains stay separate
    """
    symbol = canonical_symbol(position.get("symbol", ""))
    chain = position.get("chain", "unknown")

    # For native tokens, use 'native' as pseudo-address
    if not position.get("is_erc20", False):
        contract = "native"
    else:
        contract = position.get("contract_address", "unknown").lower()

    return (symbol, chain, contract)
