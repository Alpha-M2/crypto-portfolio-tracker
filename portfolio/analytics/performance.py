from typing import List, Dict
from datetime import datetime
import sqlite3

from portfolio.cache.sqlite import DB_PATH


def get_portfolio_history(wallet_address: str) -> List[Dict]:
    """
    Fetch historical portfolio snapshots for a wallet.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, snapshot_time, total_value, total_pnl
        FROM portfolio_snapshots
        WHERE wallet_address = ?
        ORDER BY snapshot_time ASC
        """,
        (wallet_address,),
    )

    rows = cur.fetchall()
    history = []

    for snap_id, snap_time, total_value, total_pnl in rows:
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
                "snapshot_time": snap_time,
                "total_value": total_value,
                "total_pnl": total_pnl,
                "positions": positions,
            }
        )

    conn.close()
    return history


def compute_performance_metrics(history: List[Dict]) -> Dict:
    """
    This function is intentionally lightweight and defensive.
    It exists to keep backward compatibility with earlier pipeline stages.
    """

    if not history:
        return {}

    initial_value = history[0].get("total_value") or 1.0
    latest = history[-1]

    performance_timeline = []

    for h in history:
        total_value = h.get("total_value", 0.0)
        pnl = h.get("total_pnl", 0.0)
        roi = (total_value - initial_value) / initial_value if initial_value else 0.0

        performance_timeline.append(
            {
                "snapshot_time": h.get("snapshot_time"),
                "total_value": total_value,
                "total_pnl": pnl,
                "roi": roi,
            }
        )

    return {
        "initial_value": initial_value,
        "latest_value": latest.get("total_value", 0.0),
        "total_pnl": latest.get("total_pnl", 0.0),
        "history": performance_timeline,
    }
