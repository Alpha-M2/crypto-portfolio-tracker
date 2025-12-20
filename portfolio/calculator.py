import logging

logger = logging.getLogger(__name__)


def calculate_position(holding, current_price: float | None) -> dict:
    if holding.amount <= 0:
        logger.warning("Skipping asset %s due to zero amount", holding.symbol)
        return None

    if current_price is None:
        return {
            "symbol": holding.symbol,
            "amount": holding.amount,
            "price_available": False,
            "reason": "Price unavailable from provider",
        }

    invested = holding.amount * holding.cost_basis
    current_value = holding.amount * current_price

    pnl_pct = ((current_value - invested) / invested * 100) if invested != 0 else 0

    return {
        "symbol": holding.symbol,
        "amount": holding.amount,
        "invested": invested,
        "current_value": current_value,
        "pnl": current_value - invested,
        "pnl_pct": pnl_pct,
        "price_available": True,
    }
