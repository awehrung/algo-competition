from collections import defaultdict
from dataclasses import dataclass
from enum import StrEnum
from typing import Optional, List

import docker
from docker import DockerClient
from docker.errors import ContainerError

from competitor import Competitor


def play_standoff(competitors: List[Competitor]) -> None:
    """
    Play the mega mexican standoff game as defined in the README, and print the
    results at the end

    :param competitors: Full list of competitors, each entry should be an instance of the
        Competitor dataclass
    """
    if len(competitors) < 3:
        raise Exception("At least 3 competitors needed for standoff game")

    game_state = _init_state(competitors)
    dead_players = defaultdict(list)
    round_nb = 1

    while True:
        print(f"Still alive before round {round_nb}:")
        print(
            "\n".join(
                [
                    f"- {c.name} ({game_state[c].hp} HP, {game_state[c].ammo} ammo)"
                    for c in game_state.keys()
                ]
            )
        )
        # add a breakpoint here for increased suspense
        decisions = _compute_decisions(game_state)
        print(f"Round {round_nb} decisions:")
        print(
            "\n".join(
                [
                    f"- {c.name} ({game_state[c].hp} HP, {game_state[c].ammo} ammo) uses {str(d)}"
                    for c, d in decisions.items()
                ]
            )
        )

        _update_state(game_state, decisions)
        _update_standoff_circle(game_state, dead_players, round_nb)

        # print(game_state)
        if len(game_state.keys()) <= 1:
            print(
                f"\nGame over! Still alive: {'no one' if len(game_state) == 0 else _get_last_player_infos(game_state)}"
            )
            break

        round_nb += 1

    print("Death order:")
    print(
        "\n".join(
            [
                f"- Round {k}: {', '.join(v)}"
                for k, v in sorted(dead_players.items(), key=lambda item: item[0])
            ]
        )
    )


@dataclass(frozen=True)
class _Config:
    starting_hp = 30
    starting_ammo = 2
    max_ammo_capacity = 2
    ammo_loss_on_shoot = 1
    ammo_gain_on_reload = 1
    protect_damage_multiplier = 0.4
    hp_lost_per_hit = 10


class _Action(StrEnum):
    SHOOT = "Shoot"
    PROTECT = "Protect"
    RELOAD = "Reload"
    NOTHING = "Nothing"

    @staticmethod
    def from_str(s):
        if s == "S":
            return _Action.SHOOT
        elif s == "P":
            return _Action.PROTECT
        elif s == "R":
            return _Action.RELOAD
        else:
            return _Action.NOTHING


@dataclass
class _PlayerState:
    hp: int = _Config.starting_hp
    ammo: int = _Config.starting_ammo
    last_action: _Action = _Action.NOTHING
    neighbor_left: Optional[Competitor] = None
    neighbor_right: Optional[Competitor] = None


def _init_state(competitors: List[Competitor]) -> dict[Competitor, _PlayerState]:
    game_state = {c: _PlayerState() for c in competitors}
    for i in range(len(competitors)):
        game_state[competitors[i]].neighbor_left = competitors[i - 1]
        game_state[competitors[i - 1]].neighbor_right = competitors[i]
    return game_state


def _encode_input(
    my_state: _PlayerState,
    neighbor_left_state: _PlayerState,
    neighbor_right_state: _PlayerState,
) -> str:
    my_infos = "/".join(
        [str(my_state.hp), str(my_state.ammo), str(my_state.last_action)[0]]
    )
    neighbor_left_infos = (
        " "
        if neighbor_left_state is None
        else "/".join(
            [
                str(neighbor_left_state.hp),
                str(neighbor_left_state.ammo),
                str(neighbor_left_state.last_action)[0],
            ]
        )
    )
    neighbor_right_infos = (
        " "
        if neighbor_right_state is None
        else "/".join(
            [
                str(neighbor_right_state.hp),
                str(neighbor_right_state.ammo),
                str(neighbor_right_state.last_action)[0],
            ]
        )
    )
    return f"{my_infos} {neighbor_left_infos} {neighbor_right_infos}".strip()


def _decode_output(raw_output: bytes) -> str:
    return raw_output.decode("utf-8").strip()


def _check_move_validity(move: str, hp: int, ammo: int) -> Optional[str]:
    if not move in ("S", "P", "R", "N"):
        return "Unknown move"
    if hp <= 0:
        return "Cannot act, player is dead"
    if move == "S" and ammo <= 0:
        return "Cannot shoot, no ammo"
    if move == "R" and ammo >= _Config.max_ammo_capacity:
        return "Cannot reload, ammo full"
    return None


def _compute_decisions(
    game_state: dict[Competitor, _PlayerState]
) -> dict[Competitor, _Action]:
    client = docker.from_env()
    decisions = {}
    for c in game_state.keys():
        container_input = _encode_input(
            game_state[c],
            (
                None
                if game_state[c].neighbor_left is None
                else game_state[game_state[c].neighbor_left]
            ),
            (
                None
                if game_state[c].neighbor_right is None
                else game_state[game_state[c].neighbor_right]
            ),
        )
        # print(container_input)
        decision = _run_turn(client, c.container_image, container_input)
        error_message = _check_move_validity(
            decision, game_state[c].hp, game_state[c].ammo
        )
        if error_message is None:
            decisions[c] = _Action.from_str(decision)
        else:
            print(f"Invalid move {decision} for player {c.name}: {error_message}")
            decisions[c] = _Action.NOTHING
    return decisions


def _run_turn(client: DockerClient, image_name: str, container_input: str) -> str:
    try:
        return _decode_output(
            client.containers.run(
                image_name,
                container_input,
            )
        )
    except ContainerError:
        print(f"{image_name} threw error")
        return "N"


def _update_state(
    game_state: dict[Competitor, _PlayerState], decisions: dict[Competitor, _Action]
) -> None:
    for c in game_state.keys():
        game_state[c].last_action = decisions[c]
        neighbor_left = game_state[c].neighbor_left
        neighbor_right = game_state[c].neighbor_right
        if decisions[c] == _Action.SHOOT:
            game_state[c].ammo -= _Config.ammo_loss_on_shoot
            if neighbor_left is not None:
                damage_done_left = int(
                    _Config.hp_lost_per_hit
                    * (
                        _Config.protect_damage_multiplier
                        if decisions[neighbor_left] == _Action.PROTECT
                        else 1
                    )
                )
                print(
                    f"{neighbor_left.name} takes {damage_done_left} damage from {c.name}"
                )
                game_state[neighbor_left].hp -= damage_done_left
            if neighbor_right is not None:
                damage_done_right = int(
                    _Config.hp_lost_per_hit
                    * (
                        _Config.protect_damage_multiplier
                        if decisions[neighbor_right] == _Action.PROTECT
                        else 1
                    )
                )
                print(
                    f"{neighbor_right.name} takes {damage_done_right} damage from {c.name}"
                )
                game_state[neighbor_right].hp -= damage_done_right
        elif decisions[c] == _Action.RELOAD:
            game_state[c].ammo += _Config.ammo_gain_on_reload


def _update_standoff_circle(
    game_state: dict[Competitor, _PlayerState],
    dead_players: dict[int, List[str]],
    round_nb: int,
) -> None:
    game_state_keys = list(game_state.keys())
    for c in game_state_keys:
        if game_state[c].hp <= 0:
            print(f"{c.name} is dead")
            dead_player_state = game_state.pop(c)
            dead_players[round_nb].append(c.name)
            if dead_player_state.neighbor_left in game_state:
                game_state[dead_player_state.neighbor_left].neighbor_right = (
                    dead_player_state.neighbor_right
                )
            if dead_player_state.neighbor_right in game_state:
                game_state[dead_player_state.neighbor_right].neighbor_left = (
                    dead_player_state.neighbor_left
                )
        else:
            if game_state[c].neighbor_left == game_state[c].neighbor_right:
                game_state[c].neighbor_right = None


def _get_last_player_infos(game_state: dict[Competitor, _PlayerState]) -> str:
    player, player_state = list(game_state.items())[0]
    return f"{player.name} with {player_state.hp} HP and {player_state.ammo} ammo"
