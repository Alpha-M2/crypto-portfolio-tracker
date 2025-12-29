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
from dotenv import load_dotenv
import logging
import io
import csv

from portfolio.multi_chain import fetch_multi_chain_portfolio
from portfolio.storage import save_snapshot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def dashboard():
    try:
        wallet_address = (
            request.args.get("wallet")
            or request.form.get("wallet")
            or request.cookies.get("wallet")
        )

        if not wallet_address:
            return render_template("wallet_input.html")

        result = fetch_multi_chain_portfolio(wallet_address)

        portfolio = result["portfolio"]
        total_value = result["total_value"]
        total_pnl = result["total_pnl"]

        if request.method == "POST":
            save_snapshot(wallet_address, portfolio)

        response = make_response(
            render_template(
                "dashboard.html",
                portfolio=portfolio,
                total_value=total_value,
                total_pnl=total_pnl,
                wallet=wallet_address,
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


@app.route("/export-csv")
def export_csv():
    wallet = request.args.get("wallet")
    if not wallet:
        return "No wallet specified", 400

    result = fetch_multi_chain_portfolio(wallet)
    portfolio = result["portfolio"]

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(
        [
            "Asset",
            "Chain",
            "Quantity",
            "Value (USD)",
            "Invested (USD)",
            "P/L (USD)",
            "P/L (%)",
        ]
    )

    for item in portfolio:
        writer.writerow(
            [
                item["symbol"],
                item["chain"].capitalize(),
                f"{item['amount']:.8g}",
                f"{item['current_value']:.2f}",
                f"{item['invested']:.2f}",
                f"{item['pnl']:.2f}",
                f"{item['pnl_pct']:.2f}",
            ]
        )

    writer.writerow([])
    writer.writerow(["Total Portfolio Value", f"{result['total_value']:.2f}"])

    output.seek(0)

    response = make_response(output.getvalue())
    response.headers["Content-Type"] = "text/csv"
    response.headers["Content-Disposition"] = (
        f"attachment; filename=portfolio_{wallet[:10]}.csv"
    )

    return response


@app.route("/change-wallet")
def change_wallet():
    response = redirect("/")
    response.delete_cookie("wallet")
    return response


if __name__ == "__main__":
    app.run(debug=True)
