from dataclasses import dataclass
from typing import Optional


@dataclass
class Holding:
    symbol: str
    amount: float
    cost_basis: float = 0.0
    contract_address: Optional[str] = None
    decimals: Optional[int] = None
    is_erc20: bool = False
