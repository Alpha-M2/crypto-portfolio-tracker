import logging
import requests
from portfolio.models import Holding
from portfolio.cache.token_metadata import load_token_cache, save_token_cache

logger = logging.getLogger(__name__)

ALCHEMY_URL = "https://eth-mainnet.g.alchemy.com/v2/" + (
    __import__("os").getenv("ALCHEMY_API_KEY") or ""
)


def fetch_eth_erc20_balances(wallet: str) -> list[Holding]:
    if not ALCHEMY_URL:
        return []

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "alchemy_getTokenBalances",
        "params": [wallet],
    }

    try:
        r = requests.post(ALCHEMY_URL, json=payload, timeout=15)
        r.raise_for_status()
        tokens = r.json().get("result", {}).get("tokenBalances", [])
    except Exception:
        logger.exception("Alchemy ERC20 fetch failed")
        return []

    cache = load_token_cache()
    holdings = []

    for t in tokens:
        raw = int(t.get("tokenBalance", "0"), 16)
        if raw == 0:
            continue

        addr = t["contractAddress"].lower()
        meta = cache.get(addr, {"symbol": "ERC20", "decimals": 18})

        holdings.append(
            Holding(
                symbol=meta["symbol"],
                amount=raw / (10 ** meta["decimals"]),
                chain="ethereum",
                contract_address=addr,
                is_erc20=True,
            )
        )

    save_token_cache(cache)
    return holdings
