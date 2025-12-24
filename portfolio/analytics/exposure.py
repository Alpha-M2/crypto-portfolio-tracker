from collections import defaultdict
from typing import Dict, List

from portfolio.filters.stablecoins import is_stablecoin


def asset_class_exposure(positions: List[dict]) -> Dict[str, float]:
    totals = defaultdict(float)
    portfolio_value = 0.0

    for p in positions:
        value = p["current_value"]
        portfolio_value += value

        if not p.get("is_erc20"):
            totals["native"] += value
        elif is_stablecoin(p["symbol"]):
            totals["stablecoin"] += value
        else:
            totals["erc20"] += value

    if portfolio_value == 0:
        return {}

    return {
        cls: round((value / portfolio_value) * 100, 2) for cls, value in totals.items()
    }
