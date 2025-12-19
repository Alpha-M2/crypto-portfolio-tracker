from portfolio.models import Holding


def eth_balance_to_holding(balance: float) -> Holding:
    return Holding(symbol="ethereum", quantity=balance, avg_buy_price=0.0)
