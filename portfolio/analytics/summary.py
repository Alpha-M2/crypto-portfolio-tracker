from typing import Dict, List

from portfolio.analytics.allocation import (
    allocation_by_asset,
    allocation_by_chain,
)
from portfolio.analytics.exposure import asset_class_exposure
from portfolio.analytics.provenance import infer_provenance


def build_portfolio_summary(positions: List[dict]) -> Dict:
    return {
        "allocation": {
            "by_asset": allocation_by_asset(positions),
            "by_chain": allocation_by_chain(positions),
        },
        "exposure": asset_class_exposure(positions),
        "provenance": {
            f"{p.get('chain', 'unknown')}:{p.get('symbol', 'unknown')}": infer_provenance(
                p
            )
            for p in positions
        },
    }
