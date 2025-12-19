import requests
import logging
from config import ALCHEMY_ETH_RPC_URL

logger = logging.getLogger(__name__)

WEI_IN_ETH = 10**18


def fetch_eth_balance(address: str) -> float:
    if not ALCHEMY_ETH_RPC_URL:
        raise RuntimeError("ALCHEMY_ETH_RPC_URL is not set in environment")

    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [address, "latest"],
        "id": 1,
    }

    try:
        response = requests.post(ALCHEMY_ETH_RPC_URL, json=payload, timeout=10)
        response.raise_for_status()

        data = response.json()

        if "error" in data:
            raise RuntimeError(data["error"])

        balance_wei = int(data["result"], 16)
        balance_eth = balance_wei / WEI_IN_ETH

        logger.info("Fetched ETH balance via Alchemy for %s", address)
        return balance_eth

    except Exception:
        logger.exception("Failed to fetch ETH balance via Alchemy")
        raise
