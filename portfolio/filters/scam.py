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


def is_scam_token(token: Holding) -> Tuple[bool, str]:
    symbol = getattr(token, "symbol", None)
    if not symbol:
        return True, "missing_symbol"

    sym = symbol.lower()

    # Extra protection against known ETH dust scams
    if sym in {"xeth", "ethg", "ethe", "etth", "ethx"}:
        return True, "known_scam_symbol"

    for k in SCAM_KEYWORDS:
        if k in sym:
            return True, f"keyword:{k}"

    if not symbol.isalnum():
        return True, "non_alphanumeric"

    # Never mark native tokens as scam
    if not token.is_erc20:
        return False, ""

    return False, ""
