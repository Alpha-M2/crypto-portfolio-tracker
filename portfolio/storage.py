from datetime import datetime
import os
import csv
import logging
from portfolio.models import Holding

logger = logging.getLogger(__name__)


def load_holdings(filepath: str) -> list[Holding]:
    holdings = []

    try:
        with open(filepath, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                holdings.append(
                    Holding(
                        symbol=row.get("symbol", ""),
                        amount=float(row.get("amount", 0)),
                        cost_basis=float(row.get("cost_basis", 0)),
                    )
                )
        logger.info("Loaded %d holdings from %s", len(holdings), filepath)

    except FileNotFoundError:
        logger.info(
            "Holdings file not found: %s, starting with empty holdings", filepath
        )

    except Exception as e:
        logger.exception("Failed to load holdings: %s", e)

    return holdings


def save_snapshot(wallet_address: str, positions: list[dict]):
    snapshot_dir = "data/snapshots"
    os.makedirs(snapshot_dir, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{snapshot_dir}/{wallet_address}_{timestamp}.csv"

    fieldnames = [
        "symbol",
        "amount",
        "invested",
        "current_value",
        "pnl",
        "pnl_pct",
    ]

    try:
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for pos in positions:
                writer.writerow({key: pos.get(key) for key in fieldnames})

        logger.info("Saved portfolio snapshot: %s", filename)

    except Exception:
        logger.exception("Failed to save snapshot")
