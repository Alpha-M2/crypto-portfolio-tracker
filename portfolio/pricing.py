import logging
import requests
import time
from typing import Dict, List

log = logging.getLogger(__name__)

GECKOTERMINAL_BASE = "https://api.geckoterminal.com/api/v2"
COINGECKO_SIMPLE = "https://api.coingecko.com/api/v3/simple/price"

NETWORK_SLUGS = {
    "ethereum": "eth",
    "arbitrum": "arbitrum",
    "polygon": "polygon_pos",
    "optimism": "optimism",
    "base": "base",
    "bsc": "bsc",
}

ETH_CHAINS = {"ethereum", "arbitrum", "optimism", "base"}

NATIVE_SYMBOLS = {
    "ethereum": "ETH",
    "arbitrum": "ETH",
    "optimism": "ETH",
    "base": "ETH",
    "polygon": "POL",
    "bsc": "BNB",
}

STABLECOIN_SYMBOLS = {
    "USDC",
    "USDT",
    "DAI",
    "BUSD",
    "TUSD",
    "USDP",
    "GUSD",
    "FRAX",
    "USDD",
    "PYUSD",
    "EURS",
}

# Cached prices from CoinGecko
_cached_eth_price: float | None = None
_cached_bnb_price: float | None = None


def _fetch_coingecko_price(coin_id: str) -> float | None:
    try:
        r = requests.get(
            COINGECKO_SIMPLE,
            params={"ids": coin_id, "vs_currencies": "usd"},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        price = data.get(coin_id, {}).get("usd")
        if price and price > 0:
            return float(price)
    except Exception as e:
        log.error("CoinGecko %s price fetch failed: %s", coin_id, e)
    return None


def _fetch_eth_price() -> float | None:
    global _cached_eth_price
    if _cached_eth_price is not None:
        return _cached_eth_price

    price = _fetch_coingecko_price("ethereum")
    if price:
        _cached_eth_price = price
        log.info("CoinGecko ETH price: $%.2f", price)
    return price


def _fetch_bnb_price() -> float | None:
    global _cached_bnb_price
    if _cached_bnb_price is not None:
        return _cached_bnb_price

    price = _fetch_coingecko_price("binancecoin")
    if price:
        _cached_bnb_price = price
        log.info("CoinGecko BNB price: $%.2f", price)
    return price


def get_native_prices(chains: List[str]) -> Dict[str, float]:
    prices = {}

    # ETH chains (mainnet + L2s)
    eth_price = _fetch_eth_price()
    if eth_price:
        for chain in chains:
            if chain in ETH_CHAINS:
                prices[chain] = eth_price

    # BNB
    if "bsc" in chains:
        bnb_price = _fetch_bnb_price()
        if bnb_price:
            prices["bsc"] = bnb_price
        else:
            log.warning("BNB price fetch failed - using $0")

    # POL
    if "polygon" in chains:
        slug = NETWORK_SLUGS["polygon"]
        try:
            url = f"{GECKOTERMINAL_BASE}/simple/networks/{slug}/token_price/POL"
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            data = r.json()
            usd_str = (
                data.get("data", {})
                .get("attributes", {})
                .get("token_prices", {})
                .get("POL")
            )
            if usd_str:
                price = float(usd_str)
                if price > 0:
                    prices["polygon"] = price
        except Exception as e:
            log.warning("POL price fetch failed: %s", e)

        time.sleep(1)

    return prices


def get_erc20_prices(chain: str, contracts: List[str]) -> Dict[str, float]:
    if not contracts:
        return {}

    slug = NETWORK_SLUGS.get(chain)
    if not slug:
        return {}

    contracts = list(set(c.lower() for c in contracts if c))
    prices: Dict[str, float] = {}
    batch_size = 30

    for i in range(0, len(contracts), batch_size):
        batch = contracts[i : i + batch_size]
        addresses = ",".join(batch)

        try:
            url = f"{GECKOTERMINAL_BASE}/simple/networks/{slug}/token_price/{addresses}"
            r = requests.get(url, timeout=20)
            if r.status_code == 429:
                time.sleep(15)
                continue
            r.raise_for_status()
            data = r.json()
            token_prices = (
                data.get("data", {}).get("attributes", {}).get("token_prices", {})
            )

            for addr, usd_str in token_prices.items():
                try:
                    price = float(usd_str)
                    if 0 < price < 1e9:
                        prices[addr.lower()] = price
                except:
                    continue
        except Exception as e:
            log.error("ERC20 batch failed: %s", e)

        time.sleep(2)

    return prices


def get_price_with_stable_fallback(symbol: str, chain_price: float | None) -> float:
    if chain_price is not None and chain_price > 0:
        return chain_price

    if symbol.upper() in STABLECOIN_SYMBOLS:
        return 1.00

    return 0.0
