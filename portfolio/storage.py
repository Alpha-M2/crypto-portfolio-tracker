import csv
import logging
from portfolio.models import Holding

logger = logging.getLogger(__name__)


def load_holdings(filepath: str) -> list[Holding]:
    holdings = []

    try:
        with open(filepath, newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                holdings.append(
                    Holding(
                        symbol=row["symbol"],
                        amount=float(row["amount"]),
                        cost_basis=float(row["cost_basis"]),
                    )
                )

        logger.info("Loaded %d holdings from %s", len(holdings), filepath)

    except FileNotFoundError:
        logger.error("Holdings file not found: %s", filepath)
        raise

    except Exception as e:
        logger.exception("Failed to load holdings: %s", e)
        raise

    return holdings
