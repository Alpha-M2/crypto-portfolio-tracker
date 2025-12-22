import os
import logging


from portfolio.wallets.evm import fetch_eth_balance
from portfolio.wallets.evm_tokens import fetch_erc20_holdings
from portfolio.models import Holding

logger = logging.getLogger(__name__)


class EVMChain:
    def __init__(self, symbol, name, rpc_env_key, native_symbol):
        self.symbol = symbol
        self.name = name
        self.rpc_env_key = rpc_env_key
        self.native_symbol = native_symbol

    def is_enabled(self) -> bool:
        return bool(os.getenv(self.rpc_env_key))

    @property
    def rpc_url(self) -> str:
        return os.getenv(self.rpc_env_key)

    def fetch_holdings(self, wallet_address: str):
        holdings: list[Holding] = []

        # Native balance
        try:
            native_balance = fetch_eth_balance(wallet_address, self.rpc_url)
            if native_balance > 0:
                holdings.append(
                    Holding(
                        symbol=self.native_symbol,
                        amount=native_balance,
                        cost_basis=0.0,
                        is_erc20=False,
                        chain=self.symbol,
                    )
                )
        except Exception:
            logger.exception("Failed fetching native balance for %s", self.name)

        # ERC-20s (explicitly empty until discovery is added)
        erc20_holdings = fetch_erc20_holdings(
            wallet_address=wallet_address,
            rpc_url=self.rpc_url,
            token_contracts=[],  # intentionally empty for now
            chain_symbol=self.symbol,
        )

        holdings.extend(erc20_holdings)
        return holdings
