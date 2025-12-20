import logging

logger = logging.getLogger(__name__)


def calculate_position(holding, current_price: float) -> dict:
    if holding.amount <= 0:
        logger.warning("Skipping asset %s due to zero amount", holding.symbol)

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
    }
