import sqlite3
import json
import os
import time
from typing import Optional, List
from contextlib import closing

from portfolio.models import Holding

DB_PATH = "data/cache.db"


def _get_conn():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    with _get_conn() as conn:
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS holdings_cache (
            wallet TEXT NOT NULL,
            chain TEXT NOT NULL,
            asset_key TEXT NOT NULL,
            payload TEXT NOT NULL,
            updated_at INTEGER NOT NULL,
            PRIMARY KEY (wallet, chain, asset_key)
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS prices_cache (
            asset_key TEXT NOT NULL,
            currency TEXT NOT NULL,
            price REAL NOT NULL,
            updated_at INTEGER NOT NULL,
            PRIMARY KEY (asset_key, currency)
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS portfolio_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wallet_address TEXT NOT NULL,
            total_value REAL,
            total_pnl REAL,
            created_at INTEGER DEFAULT (strftime('%s','now'))
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS portfolio_positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_id INTEGER NOT NULL,
            symbol TEXT,
            chain TEXT,
            amount REAL,
            cost_basis REAL,
            current_value REAL
        )
        """)


def _holding_key(h: Holding) -> str:
    return f"{h.chain}:{h.contract_address or h.symbol}"


def get_cached_holdings(wallet: str, chain: str, max_age_seconds: int):
    with _get_conn() as conn:
        cur = conn.cursor()
        cutoff = int(time.time()) - max_age_seconds

        cur.execute(
            """
            SELECT payload FROM holdings_cache
            WHERE wallet=? AND chain=? AND updated_at >= ?
            """,
            (wallet, chain, cutoff),
        )

        rows = cur.fetchall()

    if not rows:
        return None

    return [Holding(**json.loads(r[0])) for r in rows]


def set_cached_holdings(wallet: str, chain: str, holdings: List[Holding]):
    now = int(time.time())
    with _get_conn() as conn:
        cur = conn.cursor()
        for h in holdings:
            cur.execute(
                """
                INSERT OR REPLACE INTO holdings_cache
                (wallet, chain, asset_key, payload, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    wallet,
                    chain,
                    _holding_key(h),
                    json.dumps(h.__dict__),
                    now,
                ),
            )


def persist_portfolio_snapshot(
    wallet_address: str, summary: dict, positions: list[dict]
):
    with _get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO portfolio_snapshots(wallet_address, total_value, total_pnl)
            VALUES (?, ?, ?)
            """,
            (
                wallet_address,
                summary.get("total_value", 0.0),
                summary.get("total_pnl", 0.0),
            ),
        )
        snapshot_id = cur.lastrowid

        for p in positions:
            cur.execute(
                """
                INSERT INTO portfolio_positions
                (snapshot_id, symbol, chain, amount, cost_basis, current_value)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_id,
                    p.get("symbol"),
                    p.get("chain"),
                    p.get("amount"),
                    p.get("invested"),
                    p.get("current_value"),
                ),
            )

        return snapshot_id
