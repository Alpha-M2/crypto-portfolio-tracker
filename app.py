from flask import (
    Flask,
    request,
    render_template,
    send_file,
    make_response,
    redirect,
    url_for,
)
import os
import logging

from logger import setup_logger

from portfolio.wallets.evm import fetch_native_balance, fetch_erc20_holdings
from portfolio.wallets.utils import eth_balance_to_holding
from portfolio.storage import save_snapshot, list_snapshots
from portfolio.prices import fetch_native_prices, fetch_erc20_prices
from portfolio.calculator import calculate_position
from portfolio.filters.scam import is_scam_token
from portfolio.filters.stablecoins import is_stablecoin
from portfolio.chains.registry import CHAINS, get_chain_by_symbol

from config import BASE_CURRENCY

setup_logger()
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def dashboard():
    try:
        wallet_address = (
            request.args.get("wallet")
            or request.form.get("wallet")
            or request.cookies.get("wallet")
        )
        chain_symbol = request.args.get("chain") or request.form.get("chain") or "ETH"

        chain = get_chain_by_symbol(chain_symbol)
        if not chain:
            return f"Unsupported chain: {chain_symbol}", 400

        if not wallet_address:
            return render_template("wallet_input.html", chains=CHAINS)

        holdings = []

        try:
            native_balance = fetch_native_balance(wallet_address, chain_symbol)
            holdings.append(eth_balance_to_holding(native_balance))

            erc20_holdings = fetch_erc20_holdings(wallet_address, chain_symbol)
            holdings.extend(erc20_holdings)
        except Exception:
            logger.exception(
                "Failed to fetch wallet balances for %s on %s",
                wallet_address,
                chain_symbol,
            )

        native_symbols = []
        erc20_contracts = []
        filtered_holdings = []

        # Scam token filtering
        for h in holdings:
            is_scam, reason = is_scam_token(h)
            if is_scam:
                logger.warning(
                    "Suppressed scam token: %s (reason=%s)", h.symbol, reason
                )
                continue
            filtered_holdings.append(h)
            if getattr(h, "is_erc20", False):
                erc20_contracts.append(h.contract_address)
            else:
                native_symbols.append(h.symbol)

        native_prices = fetch_native_prices(native_symbols)
        erc20_prices = fetch_erc20_prices(erc20_contracts)

        portfolio = []
        total_value = 0.0
        total_invested = 0.0

        for h in filtered_holdings:
            price = None

            if is_stablecoin(h.symbol):
                price = 1.0
            elif getattr(h, "is_erc20", False):
                price_data = erc20_prices.get(h.contract_address)
                if price_data:
                    price = price_data.get(BASE_CURRENCY)
            else:
                price_data = native_prices.get(h.symbol)
                if price_data:
                    price = price_data.get(BASE_CURRENCY)

            if price is None:
                logger.warning("No price data for token: %s", h.symbol)
                continue

            position = calculate_position(h, price)
            if not position:
                continue

            portfolio.append(position)
            total_value += position["current_value"]
            total_invested += position["invested"]

        # Save snapshot ONLY on explicit user action
        if request.method == "POST":
            save_snapshot(wallet_address, portfolio)
            logger.info(
                "Snapshot saved for wallet %s on chain %s", wallet_address, chain_symbol
            )

        response = make_response(
            render_template(
                "dashboard.html",
                portfolio=portfolio,
                total_value=total_value,
                total_pnl=total_value - total_invested,
                wallet=wallet_address,
                chains=CHAINS,
                selected_chain=chain_symbol,
            )
        )

        response.set_cookie(
            "wallet",
            wallet_address,
            max_age=60 * 60 * 24 * 30,
            httponly=True,
            samesite="Lax",
        )

        return response

    except Exception:
        logger.exception("Dashboard rendering failed")
        return "Internal Server Error", 500


@app.route("/export/<filename>")
def export_snapshot(filename):
    snapshot_path = f"data/snapshots/{filename}"
    if not os.path.exists(snapshot_path):
        return "Snapshot not found", 404
    return send_file(snapshot_path, as_attachment=True)


@app.route("/snapshots")
def snapshot_history():
    wallet_address = request.args.get("wallet")
    if not wallet_address:
        return "Wallet required", 400

    snapshots = list_snapshots(wallet_address)
    return render_template(
        "snapshots.html",
        wallet=wallet_address,
        snapshots=snapshots,
    )


@app.route("/change-wallet")
def change_wallet():
    response = redirect("/")
    response.delete_cookie("wallet")
    return response


@app.route("/reset-wallet")
def reset_wallet():
    response = make_response(redirect(url_for("dashboard")))
    response.delete_cookie("wallet")
    return response


if __name__ == "__main__":
    app.run(debug=True)
