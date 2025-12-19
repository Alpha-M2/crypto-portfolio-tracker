from dataclasses import dataclass


@dataclass
class Holding:
    symbol: str
    quantity: float
    avg_buy_price: float
