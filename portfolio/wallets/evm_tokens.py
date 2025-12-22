import logging
from typing import List

from web3 import Web3

from portfolio.models import Holding

logger = logging.getLogger(__name__)


ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function",
    },
]


def fetch_erc20_holdings(
    wallet_address: str,
    rpc_url: str,
    token_contracts: List[str],
    chain_symbol: str,
) -> List[Holding]:
    holdings: List[Holding] = []

    if not token_contracts:
        return holdings

    web3 = Web3(Web3.HTTPProvider(rpc_url))
    if not web3.is_connected():
        logger.error("ERC-20 RPC connection failed: %s", rpc_url)
        return holdings

    wallet = Web3.to_checksum_address(wallet_address)

    for address in token_contracts:
        try:
            contract = web3.eth.contract(
                address=Web3.to_checksum_address(address),
                abi=ERC20_ABI,
            )

            raw_balance = contract.functions.balanceOf(wallet).call()
            if raw_balance == 0:
                continue

            decimals = contract.functions.decimals().call()
            symbol = contract.functions.symbol().call()

            amount = raw_balance / (10**decimals)

            holdings.append(
                Holding(
                    symbol=symbol,
                    amount=float(amount),
                    cost_basis=0.0,
                    is_erc20=True,
                    chain=chain_symbol,
                    contract_address=address.lower(),
                )
            )

        except Exception:
            logger.exception(
                "Failed ERC-20 fetch for %s on %s",
                address,
                chain_symbol,
            )

    return holdings
