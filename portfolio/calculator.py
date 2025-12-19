import logging

logger = logging.getLogger(__name__)


def calculate_position(holding, current_price: float) -> dict:
    if holding.quantity <= 0:
        logger.warning("Skipping asset %s due to zero quantity", holding.symbol)

    invested = holding.quantity * holding.avg_buy_price
    current_value = holding.quantity * current_price

    if invested == 0:
        pnl_pct = 0
    else:
        pnl_pct = ((current_value - invested) / invested) * 100

    return {
        "symbol": holding.symbol,
        "quantity": holding.quantity,
        "invested": invested,
        "current_value": current_value,
        "pnl": current_value - invested,
        "pnl_pct": pnl_pct,
    }
