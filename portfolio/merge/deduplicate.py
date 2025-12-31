from collections import defaultdict


def deduplicate_positions(positions: list[dict]) -> list[dict]:
    """
    Aggregate only identical positions: same symbol + same chain + same contract (for ERC20)
    Never merge across chains.
    """
    merged = defaultdict(
        lambda: {
            "symbol": "",
            "chain": "",
            "amount": 0.0,
            "current_value": 0.0,
            "invested": 0.0,
        }
    )

    for pos in positions:
        if not pos:
            continue

        if pos.get("is_erc20", True):
            key = (pos["symbol"], pos["chain"], "erc20")
        else:
            key = (pos["symbol"], pos["chain"], "native")

        bucket = merged[key]
        if not bucket["symbol"]:
            bucket["symbol"] = pos["symbol"]
            bucket["chain"] = pos["chain"]

        bucket["amount"] += pos["amount"]
        bucket["current_value"] += pos["current_value"]
        bucket["invested"] += pos.get("invested", 0.0)

    result = []
    for bucket in merged.values():
        result.append(
            {
                "symbol": bucket["symbol"],
                "chain": bucket["chain"],
                "amount": bucket["amount"],
                "current_value": round(bucket["current_value"], 2),
                "invested": round(bucket["invested"], 2),
            }
        )

    result.sort(key=lambda x: x["current_value"], reverse=True)
    return result
