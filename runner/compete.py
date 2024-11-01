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
        hp: int = 30
        ammo: int = 2
        last_action: Action = Action.NOTHING
        neighbor_left: Optional[str] = None
        neighbor_right: Optional[str] = None

    def encode_input(my_state, neighbor_left_state, neighbor_right_state):
        my_infos = "/".join([str(my_state.hp), str(my_state.ammo)])
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
        return f"{my_infos} {neighbor_left_infos} {neighbor_right_infos}"

    def decode_output(raw_output):
        return raw_output.decode("utf-8").strip()

    def check_move_validity(move, hp, ammo):
        if not move in ("S", "P", "R"):
            return "Unknown move"
        if hp <= 0:
            return "Cannot act, player is dead"
        if move == "S" and ammo <= 0:
            return "Cannot shoot, no ammo"
        if move == "R" and ammo >= 2:
            return "Cannot reload, ammo full"
        return None

    # init state
    game_state = {c: PlayerState() for c in competitors}
    for i in range(len(competitors)):
        game_state[competitors[i]].neighbor_left = competitors[i - 1]
        game_state[competitors[i - 1]].neighbor_right = competitors[i]

    client = docker.from_env()
    dead_players = defaultdict(list)
    round_nb = 1

    while True:
        # compute decisions
        decisions = {}
        for c in game_state.keys():
            decision = decode_output(
                client.containers.run(
                    c,
                    encode_input(
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
                    ),
                )
            )
            error_message = check_move_validity(
                decision, game_state[c].hp, game_state[c].ammo
            )
            if error_message is None:
                decisions[c] = Action.from_str(decision)
            else:
                print(f"Invalid move {decision} for player {c}: {error_message}")
                decisions[c] = Action.NOTHING
        print(f"Round {round_nb} decisions:")
        print("\n".join([f"- {c} uses {str(d)}" for c, d in decisions.items()]))

        # update state
        for c in game_state.keys():
            game_state[c].last_action = decisions[c]
            neighbor_left = game_state[c].neighbor_left
            neighbor_right = game_state[c].neighbor_right
            if decisions[c] == Action.SHOOT:
                game_state[c].ammo -= 1
                if neighbor_left is not None:
                    game_state[neighbor_left].hp -= int(
                        10 * (0.5 if decisions[neighbor_left] == Action.PROTECT else 1)
                    )
                if neighbor_right is not None:
                    game_state[neighbor_right].hp -= int(
                        10 * (0.5 if decisions[neighbor_right] == Action.PROTECT else 1)
                    )
            elif decisions[c] == Action.RELOAD:
                game_state[c].ammo += 1

        # update standoff circle
        game_state_keys = list(game_state.keys())
        for c in game_state_keys:
            if game_state[c].hp <= 0:
                print(f"{c} is dead")
                dead_player_state = game_state.pop(c)
                dead_players[round_nb].append(c)
                if dead_player_state.neighbor_left is not None:
                    game_state[dead_player_state.neighbor_left].neighbor_right = (
                        dead_player_state.neighbor_right
                    )
                if dead_player_state.neighbor_right is not None:
                    game_state[dead_player_state.neighbor_right].neighbor_left = (
                        dead_player_state.neighbor_left
                    )
            else:
                if game_state[c].neighbor_left == game_state[c].neighbor_right:
                    game_state[c].neighbor_left = None

        print(game_state)
        if len(game_state.keys()) <= 1:
            print(
                f"Game over! Still alive: {'no one' if len(game_state) == 0 else f'{list(game_state.keys())[0]} with {list(game_state.values())[0].hp} HP and  {list(game_state.values())[0].ammo} ammo'}"
            )
            break

        round_nb += 1
    print("Death order:")
    for k, v in sorted(dead_players.items(), key=lambda item: item[0]):
        print(f"- Round {k}: {', '.join(v)}")


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
