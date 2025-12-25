import logging
import requests
from typing import Dict, List

from config import BASE_CURRENCY

logger = logging.getLogger(__name__)

COINGECKO_API = "https://api.coingecko.com/api/v3"

CHAIN_TO_PLATFORM = {
    "ethereum": "ethereum",
    "polygon": "polygon-pos",
    "arbitrum": "arbitrum-one",
    "optimism": "optimistic-ethereum",
    "base": "base",
}


def fetch_native_prices(symbols: List[str]) -> Dict[str, Dict[str, float]]:
    if not symbols:
        return {}

    symbol_to_id = {
        "ETH": "ethereum",
        "BNB": "binancecoin",
        "MATIC": "polygon",
        "AVAX": "avalanche-2",
        "WETH": "ethereum",
    }

    ids = [symbol_to_id[s] for s in symbols if s in symbol_to_id]
    if not ids:
        return {}

    try:
        r = requests.get(
            f"{COINGECKO_API}/simple/price",
            params={"ids": ",".join(ids), "vs_currencies": BASE_CURRENCY},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
    except Exception:
        logger.exception("Failed to fetch native prices")
        return {}

    return {
        sym: data.get(symbol_to_id[sym], {}) for sym in symbols if sym in symbol_to_id
    }


def fetch_erc20_prices(
    chain: str, contract_addresses: List[str]
) -> Dict[str, Dict[str, float]]:
    if not contract_addresses:
        return {}

    platform = CHAIN_TO_PLATFORM.get(chain)
    if not platform:
        return {}

    prices: Dict[str, Dict[str, float]] = {}

    for i in range(0, len(contract_addresses), 50):
        batch = contract_addresses[i : i + 50]
        try:
            r = requests.get(
                f"{COINGECKO_API}/simple/token_price/{platform}",
                params={
                    "contract_addresses": ",".join(batch),
                    "vs_currencies": BASE_CURRENCY,
                },
                timeout=10,
            )
            r.raise_for_status()
            prices.update(r.json())
        except Exception:
            logger.warning("ERC-20 price batch failed for %s", batch)

    return prices
