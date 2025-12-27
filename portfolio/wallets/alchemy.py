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

    for attempt in range(5):
        try:
            r = requests.post(url, json=payload, timeout=30)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                logger.error(
                    "Alchemy 400 Bad Request on %s: %s", chain, e.response.text
                )
            else:
                logger.warning(
                    "Alchemy request failed (attempt %d): %s", attempt + 1, e
                )
            if attempt == 4:
                raise
            time.sleep(2**attempt + random.random())
        except Exception as e:
            logger.warning("Alchemy request failed (attempt %d): %s", attempt + 1, e)
            if attempt == 4:
                raise
            time.sleep(2**attempt + random.random())


def _get_token_metadata(chain: str, contract: str, cache: dict) -> dict:
    contract_lower = contract.lower()
    if contract_lower in cache:
        return cache[contract_lower]

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
        logger.warning("Failed to fetch metadata for token %s on %s", contract, chain)
        symbol = "UNKNOWN"
        decimals = 18

    meta = {"symbol": symbol, "decimals": decimals}
    cache[contract_lower] = meta
    return meta


def fetch_erc20_holdings(wallet: str, chain: str) -> List[Holding]:
    if not ALCHEMY_KEY:
        logger.warning("ALCHEMY_API_KEY not set — skipping ERC20 fetch on %s", chain)
        return []

    logger.info(
        "Fetching all ERC20 holdings for %s... on %s via Alchemy", wallet[:10], chain
    )

    holdings: List[Holding] = []
    cache = load_token_cache()
    page_key: str | None = None

    try:
        while True:
            params = [wallet, "erc20"]
            if page_key:
                params.append({"pageKey": page_key})

            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "alchemy_getTokenBalances",
                "params": params,
            }

            response = _alchemy_post(chain, payload)
            result = response.get("result", {})

            balances = result.get("tokenBalances", [])
            logger.info(
                "Received %d token balances on %s (pageKey: %s)",
                len(balances),
                chain,
                page_key or "none",
            )

            for token in balances:
                contract = token.get("contractAddress")
                if not contract:
                    continue

                raw_hex = token.get("tokenBalance", "0x0")
                try:
                    raw = int(raw_hex, 16)
                except ValueError:
                    continue

                if raw == 0:
                    continue  # Skip zero balances

                contract_lower = contract.lower()
                meta = _get_token_metadata(chain, contract, cache)

                amount = raw / (10 ** meta["decimals"])

                if amount > 0:
                    holdings.append(
                        Holding(
                            symbol=meta["symbol"],
                            amount=amount,
                            chain=chain,
                            is_erc20=True,
                            contract_address=contract_lower,
                            decimals=meta["decimals"],
                        )
                    )

            page_key = result.get("pageKey")
            if not page_key:
                break

        logger.info(
            "Successfully fetched %d non-zero ERC20 holdings on %s",
            len(holdings),
            chain,
        )

    except Exception as e:
        logger.error("Failed to fetch ERC20 holdings on %s: %s", chain, str(e))
        holdings = []  # Graceful fallback

    save_token_cache(cache)
    return holdings
