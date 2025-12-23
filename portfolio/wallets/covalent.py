import os
import logging
import requests
from typing import List
from portfolio.models import Holding

logger = logging.getLogger(__name__)

COVALENT_API_KEY = os.getenv("COVALENT_API_KEY")
BASE_URL = "https://api.covalenthq.com/v1"


def fetch_covalent_erc20_holdings(
    wallet_address: str,
    chain_id: int,
    chain_symbol: str,
) -> List[Holding]:
    if not COVALENT_API_KEY:
        return []

    url = f"{BASE_URL}/{chain_id}/address/{wallet_address}/balances_v2/"
    params = {
        "key": COVALENT_API_KEY,
        "nft": False,
        "no-nft-fetch": True,
    }

    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        items = data.get("data", {}).get("items", [])
        holdings: List[Holding] = []

        for item in items:
            if not item.get("contract_address"):
                continue

            if item.get("contract_decimals") is None:
                continue

            balance_raw = int(item.get("balance", 0))
            if balance_raw == 0:
                continue

            decimals = int(item["contract_decimals"])
            amount = balance_raw / (10**decimals)

            holdings.append(
                Holding(
                    symbol=item.get("contract_ticker_symbol") or "UNKNOWN",
                    amount=float(amount),
                    cost_basis=0.0,
                    is_erc20=True,
                    chain=chain_symbol,
                    contract_address=item["contract_address"].lower(),
                )
            )

        logger.info(
            "Covalent returned %d ERC-20 holdings",
            len(holdings),
        )
        return holdings

    except Exception:
        logger.exception("Covalent ERC-20 fetch failed")
        return []
