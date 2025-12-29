import logging
import requests
import time
from typing import Dict, List

log = logging.getLogger(__name__)

GECKOTERMINAL_BASE = "https://api.geckoterminal.com/api/v2"

NETWORK_SLUGS = {
    "ethereum": "eth",
    "arbitrum": "arbitrum",
    "polygon": "polygon_pos",
    "optimism": "optimism",
    "base": "base",
    "bsc": "bsc",
}

# Chains that use ETH as native
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

# Single source of truth for ETH price
_eth_price: float | None = None


def _fetch_eth_price() -> float | None:
    """Fetch ETH price from mainnet - used for ALL ETH chains"""
    global _eth_price
    if _eth_price is not None:
        return _eth_price

    try:
        url = f"{GECKOTERMINAL_BASE}/simple/networks/eth/token_price/ETH"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        usd_str = (
            data.get("data", {})
            .get("attributes", {})
            .get("token_prices", {})
            .get("ETH")
        )
        if usd_str:
            price = float(usd_str)
            if 2000 < price < 10000:  # Realistic range
                _eth_price = price
                log.info(
                    "Fetched ETH price (mainnet): $%.2f - applied to all ETH chains",
                    price,
                )
                return price
    except Exception as e:
        log.error("ETH price fetch failed: %s", e)

    return None


def get_native_prices(chains: List[str]) -> Dict[str, float]:
    prices = {}

    # Get ETH price for all ETH chains
    eth_price = _fetch_eth_price()
    if eth_price:
        for chain in chains:
            if chain in ETH_CHAINS:
                prices[chain] = eth_price

    # Fetch non-ETH natives individually
    for chain in chains:
        if chain in ETH_CHAINS:
            continue  # Already handled

        slug = NETWORK_SLUGS.get(chain)
        symbol = NATIVE_SYMBOLS.get(chain)
        if not slug or not symbol:
            continue

        try:
            url = f"{GECKOTERMINAL_BASE}/simple/networks/{slug}/token_price/{symbol}"
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            data = r.json()
            usd_str = (
                data.get("data", {})
                .get("attributes", {})
                .get("token_prices", {})
                .get(symbol.upper())
            )
            if usd_str:
                price = float(usd_str)
                if price > 0:
                    prices[chain] = price
                    log.info("Native %s on %s: $%.2f", symbol, chain, price)
        except Exception as e:
            log.warning("Failed native price for %s: %s", chain, e)

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
