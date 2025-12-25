def infer_provenance(position: dict):
    if not position.get("is_erc20"):
        return {"source": "native", "confidence": "high"}

    if position.get("cost_basis", 0) == 0:
        return {"source": "airdrop_or_transfer", "confidence": "medium"}

    return {"source": "swap", "confidence": "high"}
