from typing import Dict, List


def calculate_total_value(positions: List[dict]) -> float:
    return sum(p.get("current_value", 0.0) for p in positions)


def calculate_total_pnl(positions: List[dict]) -> float:
    return sum(p.get("pnl", 0.0) for p in positions)


def build_portfolio_summary(positions: List[dict]) -> Dict:
    total_value = calculate_total_value(positions)
    total_pnl = calculate_total_pnl(positions)

    return {
        "total_value": round(total_value, 2),
        "total_pnl": round(total_pnl, 2),
    }
