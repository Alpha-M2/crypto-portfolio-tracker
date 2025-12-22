from collections import defaultdict
from portfolio.merge.keys import asset_key


def deduplicate_positions(positions: list[dict]) -> list[dict]:
    merged = defaultdict(
        lambda: {
            "symbol": None,
            "amount": 0.0,
            "invested": 0.0,
            "current_value": 0.0,
        }
    )

    for pos in positions:
        key = asset_key(pos)
        bucket = merged[key]

        bucket["symbol"] = key
        bucket["amount"] += pos["amount"]
        bucket["invested"] += pos["invested"]
        bucket["current_value"] += pos["current_value"]

    result = []

    for asset in merged.values():
        invested = asset["invested"]
        value = asset["current_value"]

        pnl = value - invested
        pnl_pct = (pnl / invested * 100) if invested > 0 else 0.0

        asset["pnl"] = pnl
        asset["pnl_pct"] = pnl_pct

        result.append(asset)

    return result
