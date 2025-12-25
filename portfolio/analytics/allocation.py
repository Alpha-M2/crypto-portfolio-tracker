from collections import defaultdict
from typing import Dict, List, Union

from portfolio.models import Holding


def _get(h, attr, default=0.0):
    return h.get(attr, default) if isinstance(h, dict) else getattr(h, attr, default)


def calculate_total_value(holdings: List[Union[Holding, dict]]) -> float:
    return sum(_get(h, "amount", 0.0) * _get(h, "price", 0.0) for h in holdings)


def allocation_by_asset(holdings: List[Union[Holding, dict]]) -> Dict[str, float]:
    totals = defaultdict(float)
    total_value = calculate_total_value(holdings)

    if total_value == 0:
        return {}

    for h in holdings:
        symbol = _get(h, "symbol", "UNKNOWN")
        totals[symbol] += _get(h, "amount", 0) * _get(h, "price", 0)

    return {k: round(v / total_value * 100, 2) for k, v in totals.items()}


def allocation_by_chain(holdings: List[Union[Holding, dict]]) -> Dict[str, float]:
    totals = defaultdict(float)
    total_value = calculate_total_value(holdings)

    if total_value == 0:
        return {}

    for h in holdings:
        chain = _get(h, "chain", "unknown")
        totals[chain] += _get(h, "amount", 0) * _get(h, "price", 0)

    return {k: round(v / total_value * 100, 2) for k, v in totals.items()}
