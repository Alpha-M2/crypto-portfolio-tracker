from fastapi import APIRouter, Query
from portfolio.multi_chain import fetch_multi_chain_portfolio

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/")
def get_portfolio(wallet: str):
    """
    Returns full portfolio snapshot including:
    - holdings
    - valuation
    - allocation
    - performance
    """
    return fetch_multi_chain_portfolio(wallet)


@router.get("/summary")
def get_portfolio_summary(wallet: str):
    data = fetch_multi_chain_portfolio(wallet)
    return {
        "summary": data.get("summary"),
        "total_value": data.get("total_value"),
        "total_pnl": data.get("total_pnl"),
    }
