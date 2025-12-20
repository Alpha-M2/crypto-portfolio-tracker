STABLECOINS = {
    "USDT",
    "USDC",
    "DAI",
    "BUSD",
    "TUSD",
    "USDP",
    "GUSD",
    "FRAX",
    "USD1",
}


def is_stablecoin(symbol: str) -> bool:
    return symbol.upper() in STABLECOINS
