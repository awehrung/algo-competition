from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from typing import List, Self


class Move(StrEnum):
    COOPERATE = "C"
    BETRAY = "B"

    @staticmethod
    def from_str(s: str) -> Move:
        if s == "C":
            return Move.COOPERATE
        elif s == "B":
            return Move.BETRAY
        else:
            raise Exception(f"Unknown move: {s}")

    @staticmethod
    def list_from_raw(s: str, legacy: bool = False) -> List[Move]:
        if legacy:
            return [Move.from_str(m) for m in s.split("/")]
        return [
            Move.from_str(m)
            for m in s.lstrip("[").rstrip("]").split(",")
            if len(m) == 1
        ]


@dataclass(frozen=True)
class CooperationGameArgs:
    my_moves: List[Move]
    opponent_moves: List[Move]
