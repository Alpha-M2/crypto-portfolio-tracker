import logging

from portfolio.chains.registry import get_enabled_chains
from portfolio.filters.scam import is_scam_token
from portfolio.filters.stablecoins import is_stablecoin
from portfolio.prices import fetch_native_prices, fetch_erc20_prices
from portfolio.wallets.normalize import normalize_evm_address
from portfolio.merge.deduplicate import deduplicate_positions
from portfolio.calculator import calculate_position
from config import BASE_CURRENCY

logger = logging.getLogger(__name__)


def fetch_multi_chain_portfolio(wallet_address: str) -> dict:
    wallet_address = normalize_evm_address(wallet_address)

    all_holdings = []

    # Fetch holdings from each enabled chain
    for chain in get_enabled_chains():
        try:
            logger.info(
                "Fetching holdings for wallet %s on chain %s",
                wallet_address,
                chain.name,
            )
            holdings = chain.fetch_holdings(wallet_address)
            all_holdings.extend(holdings)
        except Exception:
            logger.exception("Failed fetching holdings for chain %s", chain.name)

    # Scam filtering
    native_symbols = set()
    erc20_contracts = set()
    filtered = []

    for h in all_holdings:
        is_scam, reason = is_scam_token(h)
        if is_scam:
            logger.warning(
                "Suppressed scam token: %s (reason=%s)",
                h.symbol,
                reason,
            )
            continue

        filtered.append(h)

        if h.is_erc20 and h.contract_address:
            erc20_contracts.add(h.contract_address)
        else:
            native_symbols.add(h.symbol)

    native_prices = fetch_native_prices(list(native_symbols))
    erc20_prices = fetch_erc20_prices(list(erc20_contracts))

    positions = []

    for h in filtered:
        price = None

        if is_stablecoin(h.symbol):
            price_data = (
                erc20_prices.get(h.contract_address)
                if h.is_erc20
                else native_prices.get(h.symbol)
            )

            if price_data and BASE_CURRENCY in price_data:
                raw_price = price_data[BASE_CURRENCY]
                price = max(0.996, min(1.003, raw_price))
            else:
                price = 1.0

        elif h.is_erc20:
            price_data = erc20_prices.get(h.contract_address)
            if price_data:
                price = price_data.get(BASE_CURRENCY)

        else:
            price_data = native_prices.get(h.symbol)
            if price_data:
                price = price_data.get(BASE_CURRENCY)

        if price is None:
            logger.warning(
                "No price data for token %s on %s — using price=0",
                h.symbol,
                h.chain,
            )
            price = 0.0

        position = calculate_position(h, price)
        if position:
            positions.append(position)

    merged = deduplicate_positions(positions)

    total_value = sum(p["current_value"] for p in merged)
    total_invested = sum(p["invested"] for p in merged)
    total_pnl = total_value - total_invested

    return {
        "portfolio": merged,
        "total_value": total_value,
        "total_pnl": total_pnl,
    }
