import re
from typing import Tuple, Optional
from portfolio.models import Holding

SCAM_KEYWORDS = [
    "claim",
    "visit",
    "reward",
    "airdrop",
    "scam",
    "verify",
    "test",
    "fake",
    "http",
    ".com",
    ".net",
    ".io",
]


def is_scam_token(holding: Holding) -> Tuple[bool, Optional[str]]:
    symbol = (holding.symbol or "").lower()
    amount = holding.amount or 0

    for kw in SCAM_KEYWORDS:
        if kw in symbol:
            return True, f"keyword:{kw}"

    if len(symbol) > 25:
        return True, "symbol_length"

    # Only suppress zero-amount tokens
    if amount == 0:
        return True, "zero_amount"

    if not re.match(r"^[a-z0-9\-_.]+$", symbol):
        return True, "non_alphanumeric"

    return False, None
