from flask import Flask, render_template
import logging

from logger import setup_logger

from portfolio.wallets.evm import fetch_eth_balance
from portfolio.wallets.utils import eth_balance_to_holding
from portfolio.wallets.erc20 import fetch_erc20_holdings

from portfolio.storage import load_holdings
from portfolio.prices import fetch_native_prices, fetch_erc20_prices
from portfolio.calculator import calculate_position

from config import HOLDINGS_FILE, BASE_CURRENCY

setup_logger()
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/")
def dashboard():
    try:
        holdings = load_holdings(HOLDINGS_FILE)

        wallet_address = "0x2b09197141080f9dcfd2976cfdcf4e2a7d9cf483"

        if wallet_address:
            try:
                eth_balance = fetch_eth_balance(wallet_address)
                holdings.append(eth_balance_to_holding(eth_balance))

                erc20_holdings = fetch_erc20_holdings(wallet_address)
                holdings.extend(erc20_holdings)
            except Exception:
                logger.exception("Failed to fetch wallet balances")

        native_symbols = []
        erc20_contracts = []

        for h in holdings:
            if getattr(h, "is_erc20", False):
                erc20_contracts.append(h.contract_address)
            else:
                native_symbols.append(h.symbol)

        native_prices = fetch_native_prices(native_symbols)
        erc20_prices = fetch_erc20_prices(erc20_contracts)

        portfolio = []
        total_value = 0.0
        total_invested = 0.0

        for h in holdings:
            try:
                if h.is_erc20:
                    price = erc20_prices[h.contract_address][BASE_CURRENCY]
                else:
                    price = native_prices[h.symbol][BASE_CURRENCY]
            except KeyError:
                logger.warning("No price data for token: %s", h.symbol)
                continue

            position = calculate_position(h, price)
            if not position:
                continue
            portfolio.append(position)
            total_value += position["current_value"]
            total_invested += position["invested"]

        logger.info("Dashboard rendered successfully")

        return render_template(
            "dashboard.html",
            portfolio=portfolio,
            total_value=total_value,
            total_pnl=total_value - total_invested,
        )

    except Exception:
        logger.exception("Dashboard rendering failed")
        return "Internal Server Error", 500


if __name__ == "__main__":
    app.run(debug=True)
