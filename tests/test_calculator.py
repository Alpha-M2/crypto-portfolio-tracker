import pytest
from portfolio.models import Holding
from portfolio.calculator import calculate_position


def test_calculate_position_profit():
    holding = Holding(symbol="bitcoin", quantity=1, avg_buy_price=20000)

    result = calculate_position(holding, current_price=30000)

    assert result["invested"] == 20000
    assert result["current_value"] == 30000
    assert result["pnl"] == 10000
    assert result["pnl_pct"] == 50.0


def test_calculate_position_loss():
    holding = Holding(symbol="ethereum", quantity=2, avg_buy_price=2500)

    result = calculate_position(holding, current_price=2000)

    assert result["invested"] == 5000
    assert result["current_value"] == 4000
    assert result["pnl"] == -1000
    assert result["pnl_pct"] == -20.0


def test_calculate_position_zero_investment():
    holding = Holding(symbol="solana", quantity=0, avg_buy_price=1000)

    result = calculate_position(holding, current_price=500)

    assert result["invested"] == 0
    assert result["current_value"] == 0
    assert result["pnl"] == 0
    assert result["pnl_pct"] == 0
