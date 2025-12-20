import re

SCAM_KEYWORDS = [
    "claim",
    "visit",
    "reward",
    "airdrop",
    "verify",
    "http",
    ".com",
    ".net",
    ".io",
]


def is_scam_token(holding) -> tuple[bool, str | None]:
    symbol = (holding.symbol or "").lower()

    # Keyword-based detection
    for kw in SCAM_KEYWORDS:
        if kw in symbol:
            return True, f"keyword:{kw}"

    if len(symbol) > 25:
        return True, "symbol_length"

    # Zero-value dust tokens
    if holding.amount == 0 and holding.cost_basis == 0:
        return True, "zero_value"

    if not re.match(r"^[a-z0-9\-_.]+$", symbol):
        return True, "non_alphanumeric"

    return False, None
