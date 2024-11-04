from dataclasses import dataclass
from typing import Tuple, List

import docker
from docker.errors import ContainerError

from competitor import Competitor


def play_cooperation_game(c1: Competitor, c2: Competitor) -> Tuple[int, int]:
    """
    Play a 1v1 game of the cooperation game as defined in the README

    :param c1: first player
    :param c2: second player
    :return tuple of the scores: first player, second player
    """
    score_1 = 0
    score_2 = 0
    moves_1: List[str] = []
    moves_2: List[str] = []

    client = docker.from_env()
    for _ in range(_Config.nb_rounds):
        try:
            decision_1 = _decode_output(
                client.containers.run(
                    c1.container_image, _encode_input(moves_1, moves_2)
                )
            )
        except ContainerError:
            print(f"{c1.name} threw error, forfeiting the game")
            return 0, _Config.score_on_opponent_forfeit

        try:
            decision_2 = _decode_output(
                client.containers.run(
                    c2.container_image, _encode_input(moves_2, moves_1)
                )
            )
        except ContainerError:
            print(f"{c2.name} threw error, forfeiting the game")
            return _Config.score_on_opponent_forfeit, 0

        if not _is_valid_move(decision_1) and not _is_valid_move(decision_2):
            print("Both competitors chose invalid moves, disqualifying both")
            return 0, 0
        elif not _is_valid_move(decision_1):
            print(f"{c1.name} chose invalid move {decision_1}, forfeiting the game")
            return 0, _Config.score_on_opponent_forfeit
        elif not _is_valid_move(decision_2):
            print(f"{c2.name} chose invalid move {decision_2}, forfeiting the game")
            return _Config.score_on_opponent_forfeit, 0

        moves_1.append(decision_1)
        moves_2.append(decision_2)

        if [decision_1, decision_2] == ["B", "B"]:
            print(f"Both betray, {_Config.reward_on_both_betray} point(s) each")
            score_1 += _Config.reward_on_both_betray
            score_2 += _Config.reward_on_both_betray
        elif [decision_1, decision_2] == ["B", "C"]:
            print(
                f"{c1.name} betrays {c2.name} and wins {_Config.reward_on_sole_betrayer} point(s)"
            )
            score_1 += _Config.reward_on_sole_betrayer
        elif [decision_1, decision_2] == ["C", "B"]:
            print(
                f"{c2.name} betrays {c1.name} and wins {_Config.reward_on_sole_betrayer} point(s)"
            )
            score_2 += _Config.reward_on_sole_betrayer
        else:
            print(f"Both cooperate, {_Config.reward_on_both_cooperate} point(s) each")
            score_1 += _Config.reward_on_both_cooperate
            score_2 += _Config.reward_on_both_cooperate

    print(f"Final score: {c1.name}: {score_1}, {c2.name}: {score_2}")
    return score_1, score_2


@dataclass(frozen=True)
class _Config:
    nb_rounds = 10
    score_on_opponent_forfeit = nb_rounds * 2
    reward_on_both_betray = 1
    reward_on_both_cooperate = 2
    reward_on_sole_betrayer = 3


def _encode_input(my_moves: List[str], opponent_moves: List[str]) -> str:
    return f"{'/'.join(my_moves)} {'/'.join(opponent_moves)}"


def _decode_output(raw_output: bytes) -> str:
    return raw_output.decode("utf-8").strip()


def _is_valid_move(move: str) -> bool:
    return move in ("C", "B")
