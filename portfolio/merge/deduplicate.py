from collections import defaultdict
from portfolio.merge.keys import asset_key


def deduplicate_positions(positions: list[dict]) -> list[dict]:
    merged = defaultdict(
        lambda: {
            "symbol": None,
            "amount": 0.0,
            "invested": 0.0,
            "current_value": 0.0,
            "chain": "multi",
        }
    )

    for pos in positions:
        if pos is None:
            continue
        key = asset_key(pos)
        bucket = merged[key]

        bucket["symbol"] = key
        bucket["amount"] += pos.get("amount", 0.0)
        bucket["invested"] += pos.get("invested", 0.0)
        bucket["current_value"] += pos.get("current_value", 0.0)

    result = []
    for asset in merged.values():
        invested = asset["invested"]
        value = asset["current_value"]
        pnl = value - invested
        pnl_pct = (pnl / invested * 100) if invested > 0 else 0.0

        asset.update(
            {
                "pnl": round(pnl, 2),
                "pnl_pct": round(pnl_pct, 2),
            }
        )
        result.append(asset)

    # Sort by value descending
    result.sort(key=lambda x: x["current_value"], reverse=True)
    return result
