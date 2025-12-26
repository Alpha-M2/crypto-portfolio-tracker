import logging
from typing import Dict

from portfolio.chains.registry import get_enabled_chains
from portfolio.filters.scam import is_scam_token
from portfolio.pricing import get_native_prices, get_erc20_prices
from portfolio.wallets.normalize import normalize_evm_address
from portfolio.merge.deduplicate import deduplicate_positions
from portfolio.calculator import calculate_position
from portfolio.analytics.summary import build_portfolio_summary
from portfolio.analytics.performance import (
    get_portfolio_history,
    compute_performance_metrics,
)
from portfolio.cache.sqlite import persist_portfolio_snapshot

logger = logging.getLogger(__name__)


def fetch_multi_chain_portfolio(wallet_address: str) -> dict:
    if not wallet_address:
        raise ValueError("Wallet address is required")

    wallet_address = normalize_evm_address(wallet_address)

    # Fetch holdings from all enabled chains
    all_holdings = []

    for chain in get_enabled_chains():
        try:
            logger.info("Fetching holdings for %s on %s", wallet_address, chain.name)
            holdings = chain.fetch_holdings(wallet_address)
            if holdings:
                all_holdings.extend(holdings)
        except Exception:
            logger.exception("Failed fetching holdings for chain %s", chain.name)

    if not all_holdings:
        return {
            "portfolio": [],
            "total_value": 0.0,
            "total_pnl": 0.0,
            "summary": {},
            "performance": {},
        }

    # Filter scam tokens
    filtered = []
    native_chains = set()
    erc20_by_chain: dict[str, set[str]] = {}

    for h in all_holdings:
        if is_scam_token(h):
            continue

        filtered.append(h)

        if h.is_erc20:
            erc20_by_chain.setdefault(h.chain, set()).add(h.contract_address.lower())
        else:
            native_chains.add(h.chain)

    if not filtered:
        return {
            "portfolio": [],
            "total_value": 0.0,
            "total_pnl": 0.0,
            "summary": {},
            "performance": {},
        }

    # Fetch prices (native + ERC20)
    native_prices = get_native_prices(list(native_chains))

    erc20_prices: Dict[str, Dict[str, float]] = {}
    for chain, contracts in erc20_by_chain.items():
        erc20_prices[chain] = get_erc20_prices(chain, list(contracts))

    # Compute positions
    positions = []

    for h in filtered:
        try:
            if h.is_erc20:
                price = erc20_prices.get(h.chain, {}).get(h.contract_address.lower())
            else:
                price = native_prices.get(h.chain)

            if price is None:
                continue

            position = calculate_position(h, price)
            positions.append(position)

        except Exception:
            logger.exception("Failed calculating position for %s", h.symbol)

    # Aggregate
    merged = deduplicate_positions(positions)

    try:
        summary = build_portfolio_summary(merged)
    except Exception:
        logger.exception("Summary computation failed")
        summary = {}

    try:
        persist_portfolio_snapshot(wallet_address, summary, merged)
    except Exception:
        logger.exception("Snapshot persistence failed")

    try:
        history = get_portfolio_history(wallet_address)
        performance = compute_performance_metrics(history) if history else {}
    except Exception:
        performance = {}

    return {
        "portfolio": merged,
        "total_value": summary.get("total_value", 0.0),
        "total_pnl": summary.get("total_pnl", 0.0),
        "summary": summary,
        "performance": performance,
    }
