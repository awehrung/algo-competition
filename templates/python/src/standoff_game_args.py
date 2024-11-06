from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum


class Action(StrEnum):
    SHOOT = "S"
    PROTECT = "P"
    RELOAD = "R"
    NOTHING = "N"

    @staticmethod
    def from_str(s: str) -> Action:
        if s == "S":
            return Action.SHOOT
        elif s == "P":
            return Action.PROTECT
        elif s == "R":
            return Action.RELOAD
        elif s == "N":
            return Action.NOTHING
        else:
            raise Exception(f"Unknown action: {s}")


@dataclass(frozen=True)
class PlayerState:
    hp: int
    ammo: int
    last_action: Action

    @staticmethod
    def from_str(raw: str) -> PlayerState:
        attr = raw.split("/")
        if len(attr) != 3:
            raise Exception(f"Expected 3 arguments, got {len(attr)}")
        return PlayerState(int(attr[0]), int(attr[1]), Action.from_str(attr[2]))


@dataclass(frozen=True)
class StandoffGameArgs:
    me: PlayerState
    neighbor_left: PlayerState
    neighbor_right: PlayerState
