import logging
from typing import Dict, List, Any

from portfolio.chains.registry import get_enabled_chains
from portfolio.filters.scam import is_scam_token
from portfolio.filters.stablecoins import is_stablecoin
from portfolio.prices import fetch_native_prices, fetch_erc20_prices
from portfolio.wallets.normalize import normalize_evm_address
from portfolio.merge.deduplicate import deduplicate_positions
from portfolio.calculator import calculate_position
from portfolio.analytics.summary import build_portfolio_summary
from portfolio.analytics.performance import (
    get_portfolio_history,
    compute_performance_metrics,
)
from portfolio.cache.sqlite import persist_portfolio_snapshot
from config import BASE_CURRENCY

logger = logging.getLogger(__name__)


def _safe_position(position: Dict[str, Any]) -> Dict[str, Any]:
    position.setdefault("chain", "unknown")
    position.setdefault("symbol", "UNKNOWN")
    position.setdefault("amount", 0.0)
    position.setdefault("invested", 0.0)
    position.setdefault("current_value", 0.0)
    return position


def fetch_multi_chain_portfolio(wallet_address: str) -> dict:
    if not wallet_address:
        raise ValueError("Wallet address is required")

    wallet_address = normalize_evm_address(wallet_address)

    all_holdings = []

    # Fetch holdings from all enabled chains
    for chain in get_enabled_chains():
        try:
            logger.info("Fetching holdings for %s on %s", wallet_address, chain.name)
            holdings = chain.fetch_holdings(wallet_address)
            if holdings:
                all_holdings.extend(holdings)
        except Exception:
            logger.exception("Failed fetching holdings for chain %s", chain.name)

    if not all_holdings:
        logger.warning("No holdings found for wallet %s", wallet_address)
        return {
            "portfolio": [],
            "total_value": 0.0,
            "total_pnl": 0.0,
            "summary": {},
            "performance": {},
        }

    # Filter scams & collect pricing inputs
    filtered = []
    native_symbols = set()
    erc20_by_chain: dict[str, set[str]] = {}

    for h in all_holdings:
        is_scam, _ = is_scam_token(h)
        if is_scam:
            continue

        filtered.append(h)

        if h.is_erc20:
            erc20_by_chain.setdefault(h.chain, set()).add(h.contract_address)
        else:
            native_symbols.add(h.symbol)

    if not filtered:
        return {
            "portfolio": [],
            "total_value": 0.0,
            "total_pnl": 0.0,
            "summary": {},
            "performance": {},
        }

    # Fetch prices
    native_prices = fetch_native_prices(list(native_symbols))

    erc20_prices: dict[str, dict] = {}
    for chain, contracts in erc20_by_chain.items():
        try:
            prices = fetch_erc20_prices(chain, list(contracts))
            erc20_prices.update(prices)
        except Exception:
            logger.exception("Failed ERC-20 pricing for chain %s", chain)

    positions = []

    for h in filtered:
        price = 0.0

        try:
            if is_stablecoin(h.symbol):
                price = 1.0

            elif h.is_erc20:
                price = erc20_prices.get(h.contract_address, {}).get(BASE_CURRENCY, 0.0)

            else:
                price = native_prices.get(h.symbol, {}).get(BASE_CURRENCY, 0.0)

        except Exception:
            logger.exception("Price resolution failed for %s", h.symbol)
            price = 0.0

        position = calculate_position(h, price)
        if position:
            positions.append(_safe_position(position))

    if not positions:
        return {
            "portfolio": [],
            "total_value": 0.0,
            "total_pnl": 0.0,
            "summary": {},
            "performance": {},
        }

    merged = [_safe_position(p) for p in deduplicate_positions(positions)]

    try:
        summary = build_portfolio_summary(merged)
    except Exception:
        logger.exception("Summary calculation failed")
        summary = {}

    try:
        persist_portfolio_snapshot(wallet_address, summary, merged)
    except Exception:
        logger.exception("Snapshot persistence failed")

    try:
        history = get_portfolio_history(wallet_address)
        performance = compute_performance_metrics(history) if history else {}
    except Exception:
        logger.exception("Performance calculation failed")
        performance = {}

    total_value = summary.get(
        "total_value",
        sum(p.get("current_value", 0.0) for p in merged),
    )

    total_pnl = summary.get(
        "total_pnl",
        sum(p.get("current_value", 0.0) - p.get("invested", 0.0) for p in merged),
    )

    return {
        "portfolio": merged,
        "total_value": total_value,
        "total_pnl": total_pnl,
        "summary": summary,
        "performance": performance,
    }
