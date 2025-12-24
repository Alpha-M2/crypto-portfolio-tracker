from collections import defaultdict
from typing import Dict, List, Union

from portfolio.models import Holding


def _get(h, attr, default=0.0):
    if isinstance(h, dict):
        return h.get(attr, default)
    return getattr(h, attr, default)


def calculate_total_value(holdings: List[Union[Holding, dict]]) -> float:
    total = 0.0
    for h in holdings:
        amount = _get(h, "amount", 0.0)
        price = _get(h, "price", 0.0)
        total += amount * price
    return total


def allocation_by_asset(holdings: List[Union[Holding, dict]]) -> Dict[str, float]:
    totals = defaultdict(float)
    portfolio_value = calculate_total_value(holdings)

    if portfolio_value == 0:
        return {}

    for h in holdings:
        symbol = _get(h, "symbol", "UNKNOWN")
        amount = _get(h, "amount", 0.0)
        price = _get(h, "price", 0.0)
        totals[symbol] += amount * price

    return {
        symbol: round((value / portfolio_value) * 100, 2)
        for symbol, value in totals.items()
    }


def allocation_by_chain(holdings: List[Union[Holding, dict]]) -> Dict[str, float]:
    totals = defaultdict(float)
    portfolio_value = calculate_total_value(holdings)

    if portfolio_value == 0:
        return {}

    for h in holdings:
        chain = _get(h, "chain", "UNKNOWN")
        amount = _get(h, "amount", 0.0)
        price = _get(h, "price", 0.0)
        totals[chain] += amount * price

    return {
        chain: round((value / portfolio_value) * 100, 2)
        for chain, value in totals.items()
    }
