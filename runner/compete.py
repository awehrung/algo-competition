import random as rd
from collections import defaultdict
from dataclasses import dataclass
from enum import StrEnum
from typing import Optional

import docker
from docker.errors import ContainerError
from prettytable import PrettyTable


def main(game_name):
    competitors_random = [
        "my-java-competitor:0.0.1",
        "my-java-competitor:0.0.2",
        "my-python-competitor:0.0.1",
        "my-javascript-competitor:0.0.1",
    ]
    competitors_cooperation = [
        "js-test-competitor:cooperator",
        "js-test-competitor:betrayer",
        "js-test-competitor:random",
        "js-test-competitor:randomprinter",
    ]
    competitors_standoff = [
        "js-brawl-test:random-1",
        "js-brawl-test:random-2",
        "js-brawl-test:random-3",
        "js-brawl-test:random-4",
        "js-brawl-test:random-5",
    ]
    if game_name == "cooperation":
        _compete_1v1_round_robin(competitors_cooperation, _play_cooperation_game)
    elif game_name == "random":
        _compete_1v1_round_robin(competitors_random, _play_random_game)
    elif game_name == "standoff":
        rd.shuffle(competitors_standoff)
        _compete_standoff(competitors_standoff)
    else:
        print("Unknown game, exiting")
        exit(1)


def _compete_1v1_round_robin(competitors, run_game):
    scores = {c: 0 for c in competitors}
    # client = docker.from_env()
    # print(f"Pulling {len(COMPETITORS)} images")
    # for c in COMPETITORS:
    #     client.images.pull(c)
    pairings = [
        (c1, c2)
        for i1, c1 in enumerate(competitors)
        for i2, c2 in enumerate(competitors)
        if i1 < i2
    ]
    for c1, c2 in pairings:
        print(f"{c1} against {c2}")
        s1, s2 = run_game(c1, c2)
        scores[c1] += s1
        scores[c2] += s2
    print("\nScores after all matches:")
    sorted_results = [
        [v, k] for k, v in sorted(scores.items(), key=lambda item: -item[1])
    ]
    table = PrettyTable(["Points", "Competitor"], align="l")
    table.add_rows(sorted_results)
    print(table)


def _compete_standoff(competitors):
    @dataclass(frozen=True)
    class Config:
        starting_hp = 30
        starting_ammo = 2
        max_ammo_capacity = 2
        ammo_loss_on_shoot = 1
        ammo_gain_on_reload = 1
        protect_damage_multiplier = 0.6
        hp_lost_per_hit = 10

    class Action(StrEnum):
        SHOOT = "Shoot"
        PROTECT = "Protect"
        RELOAD = "Reload"
        NOTHING = "Nothing"

        @staticmethod
        def from_str(s):
            if s == "S":
                return Action.SHOOT
            elif s == "P":
                return Action.PROTECT
            elif s == "R":
                return Action.RELOAD
            else:
                return Action.NOTHING

    @dataclass
    class PlayerState:
        hp: int = Config.starting_hp
        ammo: int = Config.starting_ammo
        last_action: Action = Action.NOTHING
        neighbor_left: Optional[str] = None
        neighbor_right: Optional[str] = None

    def encode_input(my_state, neighbor_left_state, neighbor_right_state):
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

    def decode_output(raw_output):
        return raw_output.decode("utf-8").strip()

    def check_move_validity(move, hp, ammo):
        if not move in ("S", "P", "R"):
            return "Unknown move"
        if hp <= 0:
            return "Cannot act, player is dead"
        if move == "S" and ammo <= 0:
            return "Cannot shoot, no ammo"
        if move == "R" and ammo >= Config.max_ammo_capacity:
            return "Cannot reload, ammo full"
        return None

    def compute_decisions(_game_state):
        client = docker.from_env()
        _decisions = {}
        for c in _game_state.keys():
            container_input = encode_input(
                _game_state[c],
                (
                    None
                    if _game_state[c].neighbor_left is None
                    else _game_state[_game_state[c].neighbor_left]
                ),
                (
                    None
                    if _game_state[c].neighbor_right is None
                    else _game_state[_game_state[c].neighbor_right]
                ),
            )
            # print(container_input)
            decision = decode_output(
                client.containers.run(
                    c,
                    container_input,
                )
            )
            error_message = check_move_validity(
                decision, _game_state[c].hp, _game_state[c].ammo
            )
            if error_message is None:
                _decisions[c] = Action.from_str(decision)
            else:
                print(f"Invalid move {decision} for player {c}: {error_message}")
                _decisions[c] = Action.NOTHING
        return _decisions

    def update_state(_game_state, _decisions):
        for c in _game_state.keys():
            _game_state[c].last_action = _decisions[c]
            neighbor_left = _game_state[c].neighbor_left
            neighbor_right = _game_state[c].neighbor_right
            if _decisions[c] == Action.SHOOT:
                _game_state[c].ammo -= Config.ammo_loss_on_shoot
                if neighbor_left is not None:
                    _game_state[neighbor_left].hp -= int(
                        Config.hp_lost_per_hit
                        * (
                            Config.protect_damage_multiplier
                            if _decisions[neighbor_left] == Action.PROTECT
                            else 1
                        )
                    )
                if neighbor_right is not None:
                    _game_state[neighbor_right].hp -= int(
                        Config.hp_lost_per_hit
                        * (
                            Config.protect_damage_multiplier
                            if _decisions[neighbor_right] == Action.PROTECT
                            else 1
                        )
                    )
            elif _decisions[c] == Action.RELOAD:
                _game_state[c].ammo += Config.ammo_gain_on_reload

    def update_standoff_circle(_game_state, _dead_players, _round_nb):
        game_state_keys = list(_game_state.keys())
        for c in game_state_keys:
            if _game_state[c].hp <= 0:
                print(f"{c} is dead")
                dead_player_state = _game_state.pop(c)
                _dead_players[_round_nb].append(c)
                if dead_player_state.neighbor_left in _game_state:
                    _game_state[dead_player_state.neighbor_left].neighbor_right = (
                        dead_player_state.neighbor_right
                    )
                if dead_player_state.neighbor_right in _game_state:
                    _game_state[dead_player_state.neighbor_right].neighbor_left = (
                        dead_player_state.neighbor_left
                    )
            else:
                if _game_state[c].neighbor_left == _game_state[c].neighbor_right:
                    _game_state[c].neighbor_right = None

    # init state
    game_state = {c: PlayerState() for c in competitors}
    for i in range(len(competitors)):
        game_state[competitors[i]].neighbor_left = competitors[i - 1]
        game_state[competitors[i - 1]].neighbor_right = competitors[i]

    dead_players = defaultdict(list)
    round_nb = 1

    while True:
        decisions = compute_decisions(game_state)
        print(f"Round {round_nb} decisions:")
        print(
            "\n".join(
                [
                    f"- {c} ({game_state[c].hp} HP, {game_state[c].ammo} ammo) uses {str(d)}"
                    for c, d in decisions.items()
                ]
            )
        )

        update_state(game_state, decisions)
        update_standoff_circle(game_state, dead_players, round_nb)

        # print(game_state)
        if len(game_state.keys()) <= 1:
            print(
                f"\nGame over! Still alive: {'no one' if len(game_state) == 0 else f'{list(game_state.keys())[0]} with {list(game_state.values())[0].hp} HP and  {list(game_state.values())[0].ammo} ammo'}"
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


def _play_random_game(c1, c2):
    s1 = 0
    s2 = 0
    client = docker.from_env()
    r1 = int(client.containers.run(c1, "50 60").decode("utf-8").strip())
    r2 = int(client.containers.run(c2, "50 60").decode("utf-8").strip())
    if r1 == r2:
        print(f"Draw at {r1}")
        s1 += 0.5
        s2 += 0.5
    elif r1 > r2:
        print(f"{c1} wins by {r1} to {r2}")
        s1 += 1
    else:
        print(f"{c2} wins by {r2} to {r1}")
        s2 += 1
    return s1, s2


def _play_cooperation_game(c1, c2):
    score_1 = 0
    score_2 = 0
    moves_1 = []
    moves_2 = []

    def encode_input(my_moves, opponent_moves):
        return f"[{','.join(my_moves)}] [{','.join(opponent_moves)}]"

    def decode_output(raw_output):
        return raw_output.decode("utf-8").strip()

    def is_valid_move(move):
        return move in ("C", "B")

    client = docker.from_env()
    nb_rounds = 10
    score_on_opponent_forfeit = nb_rounds * 2
    for _ in range(nb_rounds):
        try:
            decision_1 = decode_output(
                client.containers.run(c1, encode_input(moves_1, moves_2))
            )
        except ContainerError:
            print(f"{c1} threw error, forfeiting the game")
            return 0, score_on_opponent_forfeit

        try:
            decision_2 = decode_output(
                client.containers.run(c2, encode_input(moves_2, moves_1))
            )
        except ContainerError:
            print(f"{c2} threw error, forfeiting the game")
            return score_on_opponent_forfeit, 0

        if not is_valid_move(decision_1) and not is_valid_move(decision_2):
            print("Both competitors chose invalid moves, disqualifying both")
            return 0, 0
        elif not is_valid_move(decision_1):
            print(f"{c1} chose invalid move {decision_1}, forfeiting the game")
            return 0, score_on_opponent_forfeit
        elif not is_valid_move(decision_2):
            print(f"{c2} chose invalid move {decision_2}, forfeiting the game")
            return score_on_opponent_forfeit, 0

        moves_1.append(decision_1)
        moves_2.append(decision_2)

        if [decision_1, decision_2] == ["B", "B"]:
            print("Both betray, 1 point each")
            score_1 += 1
            score_2 += 1
        elif [decision_1, decision_2] == ["B", "C"]:
            print(f"{c1} betrays {c2} and wins 3 points")
            score_1 += 3
        elif [decision_1, decision_2] == ["C", "B"]:
            print(f"{c2} betrays {c1} and wins 3 points")
            score_2 += 3
        else:
            print("Both cooperate, 2 point each")
            score_1 += 2
            score_2 += 2
    print(f"Final score: {c1}: {score_1}, {c2}: {score_2}")
    return score_1, score_2


if __name__ == "__main__":
    main("standoff")
