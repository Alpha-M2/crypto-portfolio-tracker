import logging
from portfolio.chains.registry import CHAINS

logger = logging.getLogger(__name__)


def build_holdings_for_wallet(wallet_address: str):
    holdings = []

    for chain in CHAINS:
        if not chain.is_enabled():
            continue

        try:
            chain_holdings = chain.fetch_holdings(wallet_address)
            holdings.extend(chain_holdings)
        except Exception:
            logger.exception("Chain failed: %s", chain.name)

    return holdings
