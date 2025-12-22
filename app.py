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
from portfolio.multi_chain import fetch_multi_chain_portfolio
from portfolio.storage import save_snapshot, list_snapshots

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

        if not wallet_address:
            return render_template("wallet_input.html")

        # Multi-chain portfolio assembly
        result = fetch_multi_chain_portfolio(wallet_address)

        portfolio = result["portfolio"]
        total_value = result["total_value"]
        total_pnl = result["total_pnl"]

        # Save snapshot ONLY on explicit user action
        if request.method == "POST":
            save_snapshot(wallet_address, portfolio)
            logger.info("Snapshot saved for wallet %s", wallet_address)

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

        logger.info("Dashboard rendered successfully")
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
