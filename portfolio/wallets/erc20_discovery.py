import os
import logging
import requests
from typing import List, Set
from web3 import Web3

logger = logging.getLogger(__name__)


TRANSFER_TOPIC = Web3.keccak(text="Transfer(address,address,uint256)").hex()

ROUTESCAN_API_KEY = os.getenv("ROUTESCAN_API_KEY")
ROUTESCAN_BASE_URL = "https://api.routescan.io/v2/network/evm"


DEFAULT_BLOCK_LOOKBACK = 3_000_000


def discover_erc20_contracts(
    wallet_address: str,
    rpc_url: str,
    chain_id: int | None = None,
) -> List[str]:
    wallet = Web3.to_checksum_address(wallet_address)

    if ROUTESCAN_API_KEY and chain_id:
        try:
            contracts = _discover_via_routescan(wallet, chain_id)
            if contracts:
                logger.info(
                    "RouteScan discovered %d ERC-20 contracts",
                    len(contracts),
                )
                return sorted(contracts)
        except Exception:
            logger.exception("RouteScan ERC-20 discovery failed, falling back")

    try:
        contracts = _discover_via_rpc(wallet, rpc_url)
        logger.info(
            "RPC log discovery found %d ERC-20 contracts",
            len(contracts),
        )
        return sorted(contracts)
    except Exception:
        logger.exception("RPC ERC-20 discovery failed")

    return []


def _discover_via_routescan(wallet: str, chain_id: int) -> Set[str]:
    headers = {
        "Authorization": f"Bearer {ROUTESCAN_API_KEY}",
        "Accept": "application/json",
    }

    params = {
        "chainId": chain_id,
        "topic": TRANSFER_TOPIC,
        "address": wallet,
        "limit": 1000,
    }

    url = f"{ROUTESCAN_BASE_URL}/logs"

    resp = requests.get(url, headers=headers, params=params, timeout=15)
    resp.raise_for_status()

    data = resp.json()
    contracts: Set[str] = set()

    for log in data.get("items", []):
        contract = log.get("address")
        if contract:
            contracts.add(contract.lower())

    return contracts


def _discover_via_rpc(wallet: str, rpc_url: str) -> Set[str]:
    web3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 15}))
    if not web3.is_connected():
        raise ConnectionError(f"RPC connection failed: {rpc_url}")

    latest_block = web3.eth.block_number
    from_block = max(0, latest_block - DEFAULT_BLOCK_LOOKBACK)

    logs = web3.eth.get_logs(
        {
            "fromBlock": from_block,
            "toBlock": "latest",
            "topics": [
                TRANSFER_TOPIC,
                None,
                Web3.keccak(hexstr=wallet.lower()).hex(),
            ],
        }
    )

    contracts: Set[str] = set()
    for log in logs:
        contracts.add(log["address"].lower())

    return contracts
