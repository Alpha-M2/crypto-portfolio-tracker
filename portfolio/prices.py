"""
DEPRECATED MODULE — DO NOT USE DIRECTLY

This file exists for backward compatibility only.

All pricing logic has been migrated to:
    portfolio/pricing.py

Any new code MUST import from `portfolio.pricing`.
"""

import warnings
from typing import Dict, List

from portfolio.pricing import get_native_prices, get_erc20_prices

warnings.warn(
    "portfolio.prices is deprecated. Use portfolio.pricing instead.",
    DeprecationWarning,
    stacklevel=2,
)


def fetch_native_prices(symbols: List[str]) -> Dict[str, Dict[str, float]]:
    """
    Backward-compatible wrapper.

    OLD behavior:
        symbols = ["ETH", "POL"]

    NEW behavior:
        We infer chains from symbols where possible.
    """

    # Minimal compatibility mapping
    symbol_to_chain = {
        "ETH": "ethereum",
        "POL": "polygon",
        "BNB": "bsc",
        "AVAX": "avalanche",
    }

    chains = [symbol_to_chain[s] for s in symbols if s in symbol_to_chain]
    prices = get_native_prices(chains)

    # Re-shape into old format
    return {
        sym: {"usd": prices.get(chain)}
        for sym, chain in symbol_to_chain.items()
        if sym in symbols
    }


def fetch_erc20_prices(
    chain: str, contract_addresses: List[str]
) -> Dict[str, Dict[str, float]]:
    """
    Backward-compatible ERC-20 pricing wrapper.
    """
    prices = get_erc20_prices(chain, contract_addresses)
    return {addr: {"usd": price} for addr, price in prices.items()}
