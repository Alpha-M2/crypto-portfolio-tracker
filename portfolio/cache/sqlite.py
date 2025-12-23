import sqlite3
import json
import os
import time
from typing import Optional, List

from portfolio.models import Holding

DB_PATH = "data/cache.db"


def _get_conn():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS holdings_cache (
            wallet TEXT NOT NULL,
            chain TEXT NOT NULL,
            asset_key TEXT NOT NULL,
            payload TEXT NOT NULL,
            updated_at INTEGER NOT NULL,
            PRIMARY KEY (wallet, chain, asset_key)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS prices_cache (
            asset_key TEXT NOT NULL,
            currency TEXT NOT NULL,
            price REAL NOT NULL,
            updated_at INTEGER NOT NULL,
            PRIMARY KEY (asset_key, currency)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS portfolio_cache (
            wallet TEXT NOT NULL,
            payload TEXT NOT NULL,
            updated_at INTEGER NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()


# -------------------------
# Holdings cache
# -------------------------


def _holding_key(h: Holding) -> str:
    if h.is_erc20:
        return f"{h.chain}:{h.contract_address}"
    return f"{h.chain}:{h.symbol}"


def get_cached_holdings(
    wallet: str, chain: str, max_age_seconds: int
) -> Optional[List[Holding]]:
    conn = _get_conn()
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
    conn.close()

    if not rows:
        return None

    holdings = []
    for (payload,) in rows:
        data = json.loads(payload)
        holdings.append(Holding(**data))

    return holdings


def set_cached_holdings(wallet: str, chain: str, holdings: List[Holding]):
    conn = _get_conn()
    cur = conn.cursor()
    now = int(time.time())

    for h in holdings:
        key = _holding_key(h)
        cur.execute(
            """
            INSERT OR REPLACE INTO holdings_cache
            (wallet, chain, asset_key, payload, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                wallet,
                chain,
                key,
                json.dumps(h.__dict__),
                now,
            ),
        )

    conn.commit()
    conn.close()
