from portfolio.models import Holding


def eth_balance_to_holding(balance: float) -> Holding:
    return Holding(symbol="eth", amount=balance, cost_basis=0.0)
