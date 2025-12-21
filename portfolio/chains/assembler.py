import logging
import os

from portfolio.wallets.evm import fetch_eth_balance
from portfolio.wallets.erc20 import fetch_erc20_holdings
from portfolio.wallets.utils import eth_balance_to_holding
from portfolio.chains.registry import CHAINS

logger = logging.getLogger(__name__)


def build_holdings_for_wallet(wallet_address: str) -> list:
    """
    Build holdings across all configured chains.
    """
    holdings = []

    for chain in CHAINS:
        rpc_url = os.getenv(chain.rpc_url)
        if not rpc_url:
            logger.warning("RPC not configured for chain %s", chain.name)
            continue

        try:
            # Native asset
            native_balance = fetch_eth_balance(
                wallet_address,
                rpc_url=rpc_url,
            )
            native_holding = eth_balance_to_holding(native_balance)
            native_holding.symbol = chain.symbol
            holdings.append(native_holding)

            # ERC-20s
            erc20s = fetch_erc20_holdings(
                wallet_address,
                rpc_url=rpc_url,
            )
            holdings.extend(erc20s)

            logger.info(
                "Fetched holdings for %s",
                chain.name,
            )

        except Exception:
            logger.exception(
                "Failed fetching holdings for chain %s",
                chain.name,
            )

    return holdings
