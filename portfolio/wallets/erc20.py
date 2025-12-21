import requests
import logging
from web3 import Web3

from config import ALCHEMY_ETH_RPC_URL
from portfolio.wallets.utils import erc20_to_holding

logger = logging.getLogger(__name__)


def fetch_erc20_holdings(
    wallet_address: str,
    rpc_url: str | None = None,
) -> list:
    """
    Fetch ERC-20 balances for an EVM-compatible chain.
    """
    rpc = rpc_url or ALCHEMY_ETH_RPC_URL
    w3 = Web3(Web3.HTTPProvider(rpc))

    tokens = discover_erc20_tokens(wallet_address, w3)

    holdings = []

    for token in tokens:
        try:
            holding = erc20_to_holding(wallet_address, token, w3)
            if holding.amount > 0:
                holdings.append(holding)
        except Exception:
            logger.exception("Failed to fetch token %s", token)

    logger.info(
        "Fetched %d ERC-20 tokens via RPC %s",
        len(holdings),
        rpc,
    )

    return holdings


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
