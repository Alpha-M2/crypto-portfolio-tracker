import os
import logging
import requests
from typing import List

from portfolio.models import Holding

logger = logging.getLogger(__name__)


def fetch_alchemy_erc20_holdings(
    wallet_address: str,
    chain: str,
) -> List[Holding]:
    api_key = os.getenv("ALCHEMY_API_KEY")
    if not api_key:
        logger.warning("Alchemy API key not set")
        return []

    base_urls = {
        "ethereum": f"https://eth-mainnet.g.alchemy.com/v2/{api_key}",
        "polygon": f"https://polygon-mainnet.g.alchemy.com/v2/{api_key}",
        "arbitrum": f"https://arb-mainnet.g.alchemy.com/v2/{api_key}",
        "optimism": f"https://opt-mainnet.g.alchemy.com/v2/{api_key}",
        "base": f"https://base-mainnet.g.alchemy.com/v2/{api_key}",
    }

    url = base_urls.get(chain.lower())
    if not url:
        return []

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "alchemy_getTokenBalances",
        "params": [wallet_address],
    }

    try:
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        logger.exception("Alchemy request failed for %s", chain)
        return []

    balances = data.get("result", {}).get("tokenBalances", [])
    holdings: List[Holding] = []

    for item in balances:
        raw_balance = int(item.get("tokenBalance", "0"), 16)
        if raw_balance == 0:
            continue

        holdings.append(
            Holding(
                symbol=None,
                amount=raw_balance,
                cost_basis=0.0,
                is_erc20=True,
                chain=chain,
                contract_address=item.get("contractAddress"),
                source="alchemy",
            )
        )

    return holdings
