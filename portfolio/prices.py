import requests
import logging
from typing import Dict, List

from config import BASE_CURRENCY

logger = logging.getLogger(__name__)

COINGECKO_API_URL = "https://api.coingecko.com/api/v3"


NATIVE_SYMBOL_TO_COINGECKO_ID = {
    "ETH": "ethereum",
    "WETH": "ethereum",
    "BNB": "bnb",
    "MNT": "mantle",
    "CRO": "crypto-com-chain",
    "BERA": "berachain-bera",
    "POL": "polygon-ecosystem-token",
    "AVAX": "avalanche-2",
    "S": "sonic",
}


def fetch_native_prices(symbols: List[str]) -> Dict[str, Dict[str, float]]:
    if not symbols:
        return {}

    # Deduplicate and normalize
    symbols = list({s.upper() for s in symbols})

    ids = []
    symbol_to_id = {}

    for symbol in symbols:
        cg_id = NATIVE_SYMBOL_TO_COINGECKO_ID.get(symbol)
        if not cg_id:
            logger.warning("No CoinGecko ID mapping for symbol: %s", symbol)
            continue

        symbol_to_id[symbol] = cg_id
        ids.append(cg_id)

    if not ids:
        return {}

    url = f"{COINGECKO_API_URL}/simple/price"
    params = {
        "ids": ",".join(sorted(set(ids))),
        "vs_currencies": BASE_CURRENCY,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    prices: Dict[str, Dict[str, float]] = {}

    for symbol, cg_id in symbol_to_id.items():
        price_data = data.get(cg_id)
        if price_data and BASE_CURRENCY in price_data:
            prices[symbol] = price_data
        else:
            logger.warning("No price data returned for symbol: %s", symbol)

    logger.info("Fetched native prices for %d assets", len(prices))
    return prices


def fetch_erc20_prices(contracts: List[str]) -> Dict[str, Dict[str, float]]:
    if not contracts:
        return {}

    prices: Dict[str, Dict[str, float]] = {}
    CHUNK_SIZE = 25

    for i in range(0, len(contracts), CHUNK_SIZE):
        chunk = contracts[i : i + CHUNK_SIZE]

        params = {
            "contract_addresses": ",".join(chunk),
            "vs_currencies": BASE_CURRENCY,
        }

        url = f"{COINGECKO_API_URL}/simple/token_price/ethereum"

        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            logger.warning(
                "Failed ERC-20 price fetch for chunk %d–%d (status %s)",
                i,
                i + CHUNK_SIZE,
                response.status_code,
            )
            continue

        data = response.json()
        prices.update(data)

    logger.info("Fetched ERC-20 prices for %d tokens", len(prices))
    return prices
