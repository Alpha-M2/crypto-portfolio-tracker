import logging

logger = logging.getLogger(__name__)


def calculate_position(holding, current_price: float | None) -> dict | None:
    if holding.amount <= 0:
        logger.debug("Skipping zero amount: %s", holding.symbol)
        return None

    invested = holding.amount * holding.cost_basis  # Usually 0.0

    if current_price is None or current_price <= 0:
        logger.info(
            "No price for %s on %s — value shown as $0", holding.symbol, holding.chain
        )
        current_value = 0.0
        pnl = -invested
        pnl_pct = 0.0 if invested == 0 else -100.0
        price_available = False
    else:
        current_value = holding.amount * current_price
        pnl = current_value - invested
        pnl_pct = (pnl / invested * 100) if invested > 0 else 0.0
        price_available = True

    return {
        "symbol": holding.symbol,
        "amount": holding.amount,
        "invested": round(invested, 2),
        "current_value": round(current_value, 2),
        "pnl": round(pnl, 2),
        "pnl_pct": round(pnl_pct, 2),
        "price_available": price_available,
        "chain": holding.chain,
    }
