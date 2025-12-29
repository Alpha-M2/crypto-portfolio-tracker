import logging

logger = logging.getLogger(__name__)

MAX_REASONABLE_VALUE = 100_000_000  # $100M cap
# Remove MIN_DISPLAY_VALUE - show all holdings, even $0


def calculate_position(holding, current_price: float) -> dict | None:
    if holding.amount <= 0:
        return None

    invested = holding.amount * holding.cost_basis

    raw_value = holding.amount * current_price

    # Cap insane values
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

    # Always show native tokens, even if price unavailable
    if current_value == 0 and not holding.is_erc20:
        note = "Price unavailable (using $0)"

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
        result["note"] = note

    return result
