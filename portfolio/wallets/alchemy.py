import os
import logging
import time
import random
import requests
from typing import List

from portfolio.models import Holding

logger = logging.getLogger(__name__)

ALCHEMY_KEY = os.getenv("ALCHEMY_API_KEY")

CHAIN_URLS = {
    "ethereum": "https://eth-mainnet.g.alchemy.com/v2/",
    "polygon": "https://polygon-mainnet.g.alchemy.com/v2/",
    "arbitrum": "https://arb-mainnet.g.alchemy.com/v2/",
    "optimism": "https://opt-mainnet.g.alchemy.com/v2/",
    "base": "https://base-mainnet.g.alchemy.com/v2/",
}


def fetch_erc20_holdings(wallet: str, chain: str) -> List[Holding]:
    if not ALCHEMY_KEY:
        logger.warning("ALCHEMY_API_KEY not set")
        return []

    base = CHAIN_URLS.get(chain)
    if not base:
        return []

    url = f"{base}{ALCHEMY_KEY}"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "alchemy_getTokenBalances",
        "params": [wallet],
    }

    for attempt in range(3):
        try:
            r = requests.post(url, json=payload, timeout=20)
            r.raise_for_status()
            data = r.json()
            break
        except Exception as e:
            if attempt == 2:
                logger.exception("Alchemy request failed")
                return []
            time.sleep(2**attempt + random.random())

    balances = data.get("result", {}).get("tokenBalances", [])
    results = []

    for token in balances:
        raw = int(token.get("tokenBalance", "0"), 16)
        if raw == 0:
            continue

        results.append(
            Holding(
                symbol=None,
                amount=raw,
                chain=chain,
                is_erc20=True,
                contract_address=token["contractAddress"],
            )
        )

    return results
