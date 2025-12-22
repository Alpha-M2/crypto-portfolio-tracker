from web3 import Web3


def normalize_evm_address(address: str) -> str:
    """
    Normalize an EVM address to checksum format.
    Raises ValueError if invalid.
    """
    if not Web3.is_address(address):
        raise ValueError(f"Invalid EVM address: {address}")

    return Web3.to_checksum_address(address)
