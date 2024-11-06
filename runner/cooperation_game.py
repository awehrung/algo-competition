from dataclasses import dataclass
from typing import Tuple, List

import docker
from docker.errors import ContainerError

from competitor import Competitor


def play_cooperation_game_legacy(c1: Competitor, c2: Competitor) -> Tuple[int, int]:
    return _play_cooperation_game(c1, c2, 10, True)


def play_cooperation_game(
    c1: Competitor, c2: Competitor, nb_rounds: int
) -> Tuple[int, int]:
    return _play_cooperation_game(c1, c2, nb_rounds)


def _play_cooperation_game(
    c1: Competitor, c2: Competitor, nb_rounds: int, syntax_legacy: bool = False
) -> Tuple[int, int]:
    """
    Play a 1v1 game of the cooperation game as defined in the README

    :param c1: first player
    :param c2: second player
    :param nb_rounds: number of rounds to play per game
    :param syntax_legacy: if True, use legacy syntax for container inputs (see README)
    :return tuple of the scores: first player, second player
    """
    score_1 = 0
    score_2 = 0
    moves_1: List[str] = []
    moves_2: List[str] = []

    client = docker.from_env()
    for _ in range(nb_rounds):
        try:
            decision_1 = _decode_output(
                client.containers.run(
                    c1.container_image, _encode_input(moves_1, moves_2, syntax_legacy)
                )
            )
        except ContainerError as e:
            print(f"{c1.name} threw error, forfeiting the game -- {e}")
            return 0, nb_rounds * _Config.score_multiplier_on_opponent_forfeit

        try:
            decision_2 = _decode_output(
                client.containers.run(
                    c2.container_image, _encode_input(moves_2, moves_1, syntax_legacy)
                )
            )
        except ContainerError as e:
            print(f"{c2.name} threw error, forfeiting the game -- {e}")
            return nb_rounds * _Config.score_multiplier_on_opponent_forfeit, 0

        if not _is_valid_move(decision_1) and not _is_valid_move(decision_2):
            print("Both competitors chose invalid moves, disqualifying both")
            return 0, 0
        elif not _is_valid_move(decision_1):
            print(f"{c1.name} chose invalid move {decision_1}, forfeiting the game")
            return 0, nb_rounds * _Config.score_multiplier_on_opponent_forfeit
        elif not _is_valid_move(decision_2):
            print(f"{c2.name} chose invalid move {decision_2}, forfeiting the game")
            return nb_rounds * _Config.score_multiplier_on_opponent_forfeit, 0

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
    score_multiplier_on_opponent_forfeit = 2
    reward_on_both_betray = 1
    reward_on_both_cooperate = 2
    reward_on_sole_betrayer = 3


def _encode_input(
    my_moves: List[str], opponent_moves: List[str], syntax_legacy: bool
) -> str:
    if syntax_legacy:
        if len(my_moves) == 0 or len(opponent_moves) == 0:
            return ""
        return f"{'/'.join(my_moves)} {'/'.join(opponent_moves)}"

    return f"[{','.join(my_moves)}] [{','.join(opponent_moves)}]"


def _decode_output(raw_output: bytes) -> str:
    return raw_output.decode("utf-8").strip()


def _is_valid_move(move: str) -> bool:
    return move in ("C", "B")
