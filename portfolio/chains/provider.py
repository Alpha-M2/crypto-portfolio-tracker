import os
import logging
from web3 import Web3

logger = logging.getLogger(__name__)


class ChainProvider:
    def __init__(self, chain):
        self.chain = chain
        self.rpc_url = os.getenv(chain.rpc_env_var)
        if not self.rpc_url:
            raise ValueError(
                f"RPC URL for {chain.symbol} not set in environment variable {chain.rpc_env_var}"
            )
        self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))

    def fetch_native_balance(self, wallet_address):
        try:
            balance = self.web3.eth.get_balance(wallet_address)
            return self.web3.fromWei(balance, "ether")
        except Exception as e:
            logger.exception(
                "Failed to fetch native balance for %s on %s",
                wallet_address,
                self.chain.symbol,
            )
            return 0.0

    def fetch_erc20_holdings(self, wallet_address):
        # TODO: Implement ERC-20 fetching per chain
        # Return a list of holdings objects with contract_address, symbol, amount
        return []
