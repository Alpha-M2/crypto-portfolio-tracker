import logging

logger = logging.getLogger(__name__)


def calculate_position(holding, current_price: float) -> dict:
    if holding.amount <= 0:
        logger.warning("Skipping asset %s due to zero amount", holding.symbol)
        return None

    invested = holding.amount * holding.cost_basis
    current_value = holding.amount * current_price

    if invested == 0:
        pnl_pct = 0
    else:
        pnl_pct = ((current_value - invested) / invested) * 100

    return {
        "symbol": holding.symbol,
        "amount": holding.amount,
        "invested": invested,
        "current_value": current_value,
        "pnl": current_value - invested,
        "pnl_pct": pnl_pct,
    }
