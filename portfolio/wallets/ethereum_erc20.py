import os
import logging
import requests
from typing import List

from portfolio.models import Holding

logger = logging.getLogger(__name__)

ALCHEMY_RPC_URL = os.getenv("ALCHEMY_ETH_RPC")


def fetch_eth_erc20_balances(wallet_address: str) -> List[Holding]:
    if not ALCHEMY_RPC_URL:
        logger.warning("ALCHEMY_ETH_RPC not configured")
        return []

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "alchemy_getTokenBalances",
        "params": [wallet_address],
    }

    try:
        resp = requests.post(ALCHEMY_RPC_URL, json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        logger.exception("Failed to fetch token balances from Alchemy")
        return []

    tokens = data.get("result", {}).get("tokenBalances", [])
    if not tokens:
        return []

    holdings: List[Holding] = []

    for token in tokens:
        try:
            raw_balance = int(token.get("tokenBalance", "0x0"), 16)
            if raw_balance == 0:
                continue

            contract = token["contractAddress"]

            meta = _fetch_token_metadata(contract)
            if not meta:
                continue

            decimals = meta["decimals"]
            symbol = meta["symbol"]

            amount = raw_balance / (10**decimals)

            holdings.append(
                Holding(
                    symbol=symbol,
                    amount=float(amount),
                    cost_basis=0.0,
                    is_erc20=True,
                    chain="ethereum",
                    contract_address=contract,
                    source="alchemy",
                )
            )

        except Exception:
            logger.exception("Failed processing ERC-20 token")

    return holdings


def _fetch_token_metadata(contract_address: str) -> dict | None:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "alchemy_getTokenMetadata",
        "params": [contract_address],
    }

    try:
        r = requests.post(ALCHEMY_RPC_URL, json=payload, timeout=15)
        r.raise_for_status()
        result = r.json().get("result")
        if not result:
            return None

        return {
            "symbol": result.get("symbol"),
            "decimals": int(result.get("decimals", 0)),
        }

    except Exception:
        logger.exception("Failed to fetch token metadata")
        return None
