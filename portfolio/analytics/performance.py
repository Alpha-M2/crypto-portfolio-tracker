import sqlite3
from datetime import datetime
from typing import List, Dict
from portfolio.cache.sqlite import DB_PATH


def get_portfolio_history(wallet_address: str) -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Fetch snapshots
    cur.execute(
        """
        SELECT id, snapshot_time, total_value, total_pnl
        FROM portfolio_snapshots
        WHERE wallet_address = ?
        ORDER BY snapshot_time ASC
    """,
        (wallet_address,),
    )
    snapshots = cur.fetchall()

    history = []
    for snap_id, snap_time, total_value, total_pnl in snapshots:
        cur.execute(
            """
            SELECT symbol, chain, amount, cost_basis, current_value
            FROM portfolio_positions
            WHERE snapshot_id = ?
        """,
            (snap_id,),
        )
        positions = [
            {
                "symbol": r[0],
                "chain": r[1],
                "amount": r[2],
                "cost_basis": r[3],
                "current_value": r[4],
            }
            for r in cur.fetchall()
        ]

        history.append(
            {
                "snapshot_time": datetime.fromisoformat(snap_time),
                "total_value": total_value,
                "total_pnl": total_pnl,
                "positions": positions,
            }
        )

    conn.close()
    return history


def compute_performance_metrics(history: List[Dict]) -> Dict:
    if not history:
        return {}

    metrics = []
    initial_value = history[0]["total_value"] or 1.0

    for h in history:
        total_value = h["total_value"]
        total_pnl = h["total_pnl"]
        roi = (total_value - initial_value) / initial_value
        metrics.append(
            {
                "snapshot_time": h["snapshot_time"],
                "total_value": total_value,
                "total_pnl": total_pnl,
                "roi": roi,
            }
        )

    return {
        "initial_value": initial_value,
        "latest_value": history[-1]["total_value"],
        "total_pnl": history[-1]["total_pnl"],
        "history": metrics,
    }


def print_performance_summary(performance: Dict):
    if not performance:
        print("No performance data available.")
        return

    print(f"Initial Value: {performance['initial_value']:.2f}")
    print(f"Latest Value: {performance['latest_value']:.2f}")
    print(f"Total PnL: {performance['total_pnl']:.2f}")
    print("Time-series snapshots:")
    for h in performance["history"]:
        time_str = h["snapshot_time"].strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"{time_str} | Value: {h['total_value']:.2f} | PnL: {h['total_pnl']:.2f} | ROI: {h['roi']:.2%}"
        )
