import logging
from typing import Dict

from portfolio.chains.registry import get_enabled_chains
from portfolio.filters.scam import is_scam_token
from portfolio.pricing import get_native_prices, get_erc20_prices
from portfolio.wallets.normalize import normalize_evm_address
from portfolio.merge.deduplicate import deduplicate_positions
from portfolio.calculator import calculate_position
from portfolio.analytics.summary import build_portfolio_summary
from portfolio.cache.sqlite import persist_portfolio_snapshot

logger = logging.getLogger(__name__)


def fetch_multi_chain_portfolio(wallet_address: str) -> dict:
    if not wallet_address:
        raise ValueError("Wallet address is required")

    wallet_address = normalize_evm_address(wallet_address)

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
        }

    # Filter only obvious scam tokens
    filtered = []
    native_chains = set()
    erc20_by_chain: dict[str, set[str]] = {}

    for h in all_holdings:
        is_scam, reason = is_scam_token(h)
        if is_scam:
            logger.info("Skipped scam-like token: %s (%s)", h.symbol, reason)
            continue

        filtered.append(h)

        if h.is_erc20 and h.contract_address:
            erc20_by_chain.setdefault(h.chain, set()).add(h.contract_address.lower())
        else:
            native_chains.add(h.chain)

    logger.info("Holdings after scam filter: %d → %d", len(all_holdings), len(filtered))

    # Fetch prices
    native_prices = get_native_prices(list(native_chains))
    erc20_prices: Dict[str, Dict[str, float]] = {
        chain: get_erc20_prices(chain, list(contracts))
        for chain, contracts in erc20_by_chain.items()
    }

    # Calculate positions — ALWAYS include, even if price is None
    positions = []
    priced_count = 0

    for h in filtered:
        try:
            price = None
            if h.is_erc20:
                price = erc20_prices.get(h.chain, {}).get(
                    h.contract_address.lower() if h.contract_address else ""
                )
            else:
                price = native_prices.get(h.chain)

            pos = calculate_position(h, price)
            if pos:
                pos["chain"] = h.chain
                positions.append(pos)
                if pos.get("price_available", False):
                    priced_count += 1
        except Exception:
            logger.exception("Error processing %s on %s", h.symbol, h.chain)

    logger.info(
        "Positions created: %d total, %d with known price", len(positions), priced_count
    )

    merged = deduplicate_positions(positions)

    summary = build_portfolio_summary(merged)

    try:
        persist_portfolio_snapshot(wallet_address, summary, merged)
    except Exception:
        logger.exception("Snapshot save failed")

    return {
        "portfolio": merged,
        "total_value": summary.get("total_value", 0.0),
        "total_pnl": summary.get("total_pnl", 0.0),
    }
