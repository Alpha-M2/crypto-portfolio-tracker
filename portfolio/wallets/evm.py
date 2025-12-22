from web3 import Web3
import logging

logger = logging.getLogger(__name__)


def fetch_eth_balance(wallet_address: str, rpc_url: str) -> float:
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 10}))

        if not w3.is_connected():
            logger.error(f"RPC connection failed: {rpc_url}")
            return 0.0

        balance_wei = w3.eth.get_balance(wallet_address)
        balance_eth = w3.from_wei(balance_wei, "ether")
        return float(balance_eth)

    except Exception as e:
        logger.exception(f"Error fetching ETH balance via RPC {rpc_url}")
        return 0.0
