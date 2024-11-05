from dataclasses import dataclass
from enum import StrEnum
from typing import List


class Move(StrEnum):
    COOPERATE = "C"
    BETRAY = "B"

    @staticmethod
    def from_str(s: str):
        if s == "C":
            return Move.COOPERATE
        elif s == "B":
            return Move.BETRAY
        else:
            raise Exception(f"Unknown move: {s}")


@dataclass(frozen=True)
class CooperationGameArgs:
    my_moves: List[Move]
    opponent_moves: List[Move]
