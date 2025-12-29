import logging

logger = logging.getLogger(__name__)

MAX_REASONABLE_VALUE = 100_000_000  # $100M cap
MIN_DISPLAY_VALUE = 1.0  # Hide holdings worth <$1


def calculate_position(holding, current_price: float) -> dict | None:
    if holding.amount <= 0:
        return None

    invested = holding.amount * holding.cost_basis

    raw_value = holding.amount * current_price

    # Cap insane values from bad price data
    if raw_value > MAX_REASONABLE_VALUE:
        logger.warning(
            "Capped value for %s: $%.2f → $%.2f",
            holding.symbol,
            raw_value,
            MAX_REASONABLE_VALUE,
        )
        current_value = MAX_REASONABLE_VALUE
        note = "Value capped (scam/bad price)"
    else:
        current_value = raw_value
        note = None

    # Hide tiny dust (<$1)
    if current_value < MIN_DISPLAY_VALUE:
        logger.debug("Hid dust holding %s: $%.2f", holding.symbol, current_value)
        return None

    pnl = current_value - invested
    pnl_pct = (pnl / invested * 100) if invested > 0 else 0.0

    result = {
        "symbol": holding.symbol,
        "amount": holding.amount,
        "invested": round(invested, 2),
        "current_value": round(current_value, 2),
        "pnl": round(pnl, 2),
        "pnl_pct": round(pnl_pct, 2),
        "price_available": current_price > 0,
        "chain": holding.chain,
    }

    if note:
        result["symbol"] += " ⚠️"
        result["note"] = note

    return result
