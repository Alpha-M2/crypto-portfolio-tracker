import logging
import requests
from typing import Dict, List

log = logging.getLogger(__name__)

COINGECKO = "https://api.coingecko.com/api/v3"

CHAIN_TO_PLATFORM = {
    "ethereum": "ethereum",
    "arbitrum": "arbitrum-one",
    "optimism": "optimistic-ethereum",
    "polygon": "polygon-pos",
    "base": "base",
}

NATIVE_COINGECKO_ID = {
    "ethereum": "ethereum",
    "arbitrum": "ethereum",
    "optimism": "ethereum",
    "base": "ethereum",
    "polygon": "polygon",
}


def get_native_prices(chains: List[str]) -> Dict[str, float]:
    """
    Returns: { chain_name: usd_price }
    """
    platforms = [CHAIN_TO_PLATFORM[c] for c in chains if c in CHAIN_TO_PLATFORM]

    if not platforms:
        return {}

    try:
        r = requests.get(
            f"{COINGECKO}/simple/price",
            params={
                "ids": ",".join(set(platforms)),
                "vs_currencies": "usd",
            },
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        log.error("Failed to fetch native prices: %s", e)
        return {}

    prices = {}
    for chain, platform in CHAIN_TO_PLATFORM.items():
        if platform in data:
            prices[chain] = data[platform].get("usd")

    return prices


def get_erc20_prices(chain: str, contracts: List[str]) -> Dict[str, float]:
    """
    Returns: {contract_address: usd_price}
    """
    if not contracts:
        return {}

    platform = CHAIN_TO_PLATFORM.get(chain)
    if not platform:
        return {}

    prices: Dict[str, float] = {}

    for i in range(0, len(contracts), 50):
        batch = contracts[i : i + 50]
        try:
            r = requests.get(
                f"{COINGECKO}/simple/token_price/{platform}",
                params={
                    "contract_addresses": ",".join(batch),
                    "vs_currencies": "usd",
                },
                timeout=10,
            )
            r.raise_for_status()
            data = r.json()
            for addr, info in data.items():
                prices[addr.lower()] = info.get("usd")
        except Exception as e:
            log.warning("ERC20 pricing failed: %s", e)

    return prices
