import requests
import logging
from config import ALCHEMY_ETH_RPC_URL
from portfolio.models import Holding

logger = logging.getLogger(__name__)


def fetch_erc20_holdings(address: str) -> list[Holding]:
    if not ALCHEMY_ETH_RPC_URL:
        raise RuntimeError("ALCHEMY_ETH_RPC_URL is not set")

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "alchemy_getTokenBalances",
        "params": [address],
    }

    try:
        response = requests.post(ALCHEMY_ETH_RPC_URL, json=payload, timeout=10)
        response.raise_for_status()

        data = response.json()
        token_balances = data["result"]["tokenBalances"]

        holdings = []

        for token in token_balances:
            raw_balance = int(token["tokenBalance"], 16)

            if raw_balance == 0:
                continue

            metadata = fetch_token_metadata(token["contractAddress"])
            decimals = metadata["decimals"]
            symbol = metadata["symbol"]

            quantity = raw_balance / (10**decimals)

            holdings.append(
                Holding(
                    symbol=symbol.lower(),
                    amount=quantity,
                    cost_basis=0.0,
                    contract_address=token["contractAddress"].lower(),
                    decimals=decimals,
                    is_erc20=True,
                )
            )

        logger.info("Fetched %d ERC-20 tokens", len(holdings))
        return holdings

    except Exception:
        logger.exception("Failed to fetch ERC-20 holdings")
        raise


def fetch_token_metadata(contract_address: str) -> dict:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "alchemy_getTokenMetadata",
        "params": [contract_address],
    }

    response = requests.post(ALCHEMY_ETH_RPC_URL, json=payload, timeout=10)
    response.raise_for_status()

    data = response.json()["result"]

    return {"symbol": data["symbol"], "decimals": data["decimals"]}
