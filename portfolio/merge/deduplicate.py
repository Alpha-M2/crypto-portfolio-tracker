from collections import defaultdict
from portfolio.merge.keys import asset_key


def deduplicate_positions(positions: list[dict]) -> list[dict]:
    """
    Aggregate only truly identical positions:
    - Same symbol
    - Same chain
    - Same contract (or both native)
    """
    merged = defaultdict(
        lambda: {
            "symbol": "",
            "chain": "",
            "amount": 0.0,
            "invested": 0.0,
            "current_value": 0.0,
            "contract_address": "",  # preserved for debugging
        }
    )

    for pos in positions:
        if not pos:
            continue

        key = asset_key(pos)
        bucket = merged[key]

        # First position sets metadata
        if not bucket["symbol"]:
            bucket["symbol"] = pos["symbol"]
            bucket["chain"] = pos["chain"]
            if pos.get("contract_address"):
                bucket["contract_address"] = pos["contract_address"]

        bucket["amount"] += pos.get("amount", 0.0)
        bucket["invested"] += pos.get("invested", 0.0)
        bucket["current_value"] += pos.get("current_value", 0.0)

    # Build final list
    result = []
    for bucket in merged.values():
        invested = bucket["invested"]
        value = bucket["current_value"]
        pnl = value - invested
        pnl_pct = (pnl / invested * 100) if invested > 0 else 0.0

        result.append(
            {
                "symbol": bucket["symbol"],
                "chain": bucket["chain"],
                "amount": round(bucket["amount"], 8),
                "invested": round(invested, 2),
                "current_value": round(value, 2),
                "pnl": round(pnl, 2),
                "pnl_pct": round(pnl_pct, 2),
            }
        )

    # Sort by value descending
    result.sort(key=lambda x: x["current_value"], reverse=True)
    return result
