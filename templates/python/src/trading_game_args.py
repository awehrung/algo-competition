from dataclasses import dataclass

from typing import Tuple, List


# R=10 MM=50 MQ=0 OM=50 OQ=0
# R=4 MM=23 MQ=2 OM=15 OQ=4 10/5 15/16 3/14
@dataclass(frozen=True)
class TradingGameArgs:
    remaining_items: int
    my_money: int
    my_quantity: int
    other_money: int
    other_quantity: int
    bids_history: List[Tuple[int, int]]
