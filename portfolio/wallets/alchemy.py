import os
import logging
import time
import random
import requests
from typing import List

from portfolio.models import Holding
from portfolio.cache.token_metadata import load_token_cache, save_token_cache

logger = logging.getLogger(__name__)

ALCHEMY_KEY = os.getenv("ALCHEMY_API_KEY")

CHAIN_URLS = {
    "ethereum": "https://eth-mainnet.g.alchemy.com/v2/",
    "polygon": "https://polygon-mainnet.g.alchemy.com/v2/",
    "arbitrum": "https://arb-mainnet.g.alchemy.com/v2/",
    "optimism": "https://opt-mainnet.g.alchemy.com/v2/",
    "base": "https://base-mainnet.g.alchemy.com/v2/",
}


def _alchemy_post(chain: str, payload: dict) -> dict:
    if not ALCHEMY_KEY:
        raise RuntimeError("ALCHEMY_API_KEY not set")

    url = f"{CHAIN_URLS[chain]}{ALCHEMY_KEY}"

    for attempt in range(3):
        try:
            r = requests.post(url, json=payload, timeout=20)
            r.raise_for_status()
            return r.json()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2**attempt + random.random())


def _get_token_metadata(chain: str, contract: str, cache: dict) -> dict:
    if contract in cache:
        return cache[contract]

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "alchemy_getTokenMetadata",
        "params": [contract],
    }

    try:
        data = _alchemy_post(chain, payload)
        result = data.get("result", {})
        symbol = result.get("symbol") or "UNKNOWN"
        decimals = int(result.get("decimals", 18))
    except Exception:
        symbol = "UNKNOWN"
        decimals = 18

    meta = {"symbol": symbol, "decimals": decimals}
    cache[contract] = meta
    return meta


def fetch_erc20_holdings(wallet: str, chain: str) -> List[Holding]:
    if not ALCHEMY_KEY:
        logger.warning("ALCHEMY_API_KEY not set")
        return []

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "alchemy_getTokenBalances",
        "params": [wallet],
    }

    try:
        response = _alchemy_post(chain, payload)
    except Exception:
        logger.exception("Failed fetching ERC20 balances")
        return []

    balances = response.get("result", {}).get("tokenBalances", [])
    if not balances:
        return []

    cache = load_token_cache()
    holdings: List[Holding] = []

    for token in balances:
        raw_hex = token.get("tokenBalance", "0x0")

        try:
            raw = int(raw_hex, 16)
        except ValueError:
            continue

        if raw == 0:
            continue

        contract = token["contractAddress"].lower()
        meta = _get_token_metadata(chain, contract, cache)

        amount = raw / (10 ** meta["decimals"])

        holdings.append(
            Holding(
                symbol=meta["symbol"],
                amount=amount,
                chain=chain,
                is_erc20=True,
                contract_address=contract,
            )
        )

    save_token_cache(cache)
    return holdings
