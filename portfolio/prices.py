import requests
import logging

from config import BASE_CURRENCY

logger = logging.getLogger(__name__)

COINGECKO_API_URL = "https://api.coingecko.com/api/v3"


def fetch_native_prices(symbols: list[str]) -> dict:
    if not symbols:
        return {}

    symbol_to_id = {
        "eth": "ethereum",
        "btc": "bitcoin",
        "ethereum": "ethereum",
        "bitcoin": "bitcoin",
    }

    ids = []
    for s in symbols:
        s = s.lower()

        if s == "solana":
            logger.info("Skipping non-EVM native asset: solana")
            continue

        cg_id = symbol_to_id.get(s)
        if cg_id:
            ids.append(cg_id)
        else:
            logger.warning("No CoinGecko ID mapping for symbol: %s", s)

    if not ids:
        return {}

    url = f"{COINGECKO_API_URL}/simple/price"
    params = {
        "ids": ",".join(ids),
        "vs_currencies": BASE_CURRENCY,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    prices = {}
    for symbol, cg_id in symbol_to_id.items():
        if cg_id in data:
            prices[symbol] = data[cg_id]

    logger.info("Fetched native prices for %d assets", len(prices))
    return prices


def fetch_erc20_prices(contracts: list[str]) -> dict:
    if not contracts:
        return {}

    prices = {}
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
