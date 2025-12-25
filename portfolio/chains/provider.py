import os
import logging
from web3 import Web3

logger = logging.getLogger(__name__)


class ChainProvider:
    def __init__(self, chain):
        self.chain = chain
        self.rpc_url = os.getenv(chain.rpc_env_key)
        if not self.rpc_url:
            raise ValueError(f"RPC URL not set for {chain.symbol}")
        self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))

    def fetch_native_balance(self, wallet_address):
        try:
            balance = self.web3.eth.get_balance(wallet_address)
            return self.web3.fromWei(balance, "ether")
        except Exception:
            logger.exception("Failed native balance fetch")
            return 0.0
