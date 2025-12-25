import os
import logging
import requests
from typing import List

from portfolio.models import Holding

logger = logging.getLogger(__name__)

ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY")

CHAIN_TO_URL = {
    "ethereum": "https://eth-mainnet.g.alchemy.com/v2/",
    "polygon": "https://polygon-mainnet.g.alchemy.com/v2/",
    "arbitrum": "https://arb-mainnet.g.alchemy.com/v2/",
    "optimism": "https://opt-mainnet.g.alchemy.com/v2/",
    "base": "https://base-mainnet.g.alchemy.com/v2/",
}


def fetch_erc20_holdings(wallet_address: str, chain: str) -> List[Holding]:
    if not ALCHEMY_API_KEY:
        logger.warning("ALCHEMY_API_KEY not set")
        return []

    base_url = CHAIN_TO_URL.get(chain)
    if not base_url:
        logger.warning("Alchemy unsupported chain: %s", chain)
        return []

    url = f"{base_url}{ALCHEMY_API_KEY}"

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "alchemy_getTokenBalances",
        "params": [wallet_address],
    }

    try:
        r = requests.post(url, json=payload, timeout=20)
        r.raise_for_status()
        data = r.json()
    except Exception:
        logger.exception("Alchemy request failed")
        return []

    balances = data.get("result", {}).get("tokenBalances", [])
    holdings: List[Holding] = []

    for token in balances:
        raw = int(token.get("tokenBalance", "0"), 16)
        if raw == 0:
            continue

        holdings.append(
            Holding(
                symbol=None,  # resolved later
                amount=raw,
                chain=chain,
                is_erc20=True,
                contract_address=token["contractAddress"],
                source="alchemy",
            )
        )

    return holdings
