from collections import defaultdict
from typing import Dict


def asset_class_exposure(positions: list[dict]) -> Dict[str, float]:
    totals = defaultdict(float)
    total_value = 0.0

    for p in positions:
        value = p.get("current_value", 0)
        total_value += value

        if not p.get("is_erc20"):
            totals["native"] += value
        elif p.get("symbol", "").upper() in {"USDC", "USDT", "DAI"}:
            totals["stablecoin"] += value
        else:
            totals["erc20"] += value

    if total_value == 0:
        return {}

    return {k: round(v / total_value * 100, 2) for k, v in totals.items()}
