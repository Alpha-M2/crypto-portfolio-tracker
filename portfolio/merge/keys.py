def canonical_symbol(symbol: str) -> str:
    symbol = symbol.upper()

    if symbol in {"WETH", "ETH"}:
        return "ETH"

    return symbol


def asset_key(position: dict) -> str:
    symbol = canonical_symbol(position["symbol"])
    return symbol
