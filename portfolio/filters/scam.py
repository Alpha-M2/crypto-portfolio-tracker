from typing import Tuple
from portfolio.models import Holding

SCAM_KEYWORDS = {
    "claim",
    "airdrop",
    "reward",
    "visit",
    "verify",
    "http",
    ".com",
    ".net",
    ".io",
}


def is_scam_token(token: Holding) -> tuple[bool, str]:
    symbol = getattr(token, "symbol", None)
    if not symbol:
        return True, "missing_symbol"

    sym = symbol.lower()

    for k in SCAM_KEYWORDS:
        if k in sym:
            return True, f"keyword:{k}"

    if not symbol.isalnum():
        return True, "non_alphanumeric"

    return False, ""
