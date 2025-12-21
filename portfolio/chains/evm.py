from typing import List

from portfolio.chains.provider import ChainProvider
from portfolio.wallets.evm import fetch_eth_balance
from portfolio.wallets.utils import eth_balance_to_holding
from portfolio.wallets.erc20 import fetch_erc20_holdings


class EVMChainProvider(ChainProvider):
    def fetch_native_balance(self, wallet_address: str):
        balance = fetch_eth_balance(
            wallet_address,
            rpc_url=self.rpc_url,
        )
        return eth_balance_to_holding(balance)

    def fetch_token_balances(self, wallet_address: str) -> List:
        return fetch_erc20_holdings(
            wallet_address,
            rpc_url=self.rpc_url,
        )

    def supports_tokens(self) -> bool:
        return True
