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
                        quantity=float(row["quantity"]),
                        avg_buy_price=float(row["avg_buy_price"]),
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
