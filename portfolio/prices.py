import requests
import logging
from config import COINGECKO_API_URL, BASE_CURRENCY

logger = logging.getLogger(__name__)


def fetch_prices(symbols: list[str]) -> dict:
    try:
        response = requests.get(
            COINGECKO_API_URL,
            params={"ids": ",".join(symbols), "vs_currencies": BASE_CURRENCY},
            timeout=10,
        )
        response.raise_for_status()
        logger.info("Fetched prices for %d assets", len(symbols))
        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error("Price API request failed: %s", e)
        raise
