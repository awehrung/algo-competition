import random as rd
from functools import partial

from competitor import Competitor
from cooperation_game import play_cooperation_game_legacy, play_cooperation_game
from random_game import play_random_game
from round_robin_game_runner import run_1v1_round_robin
from standoff_game_runner import play_standoff


def main(game_name: str) -> None:
    competitors_random = [
        Competitor("my-java-competitor-1", "my-java-competitor:0.0.1"),
        Competitor(
            "my-java-competitor-2",
            "my-java-competitor:0.0.2",
        ),
        "my-python-competitor:0.0.1",
        Competitor(
            "my-javascript-competitor-1",
            "my-javascript-competitor:0.0.1",
        ),
    ]
    competitors_cooperation = [
        "js-test-competitor:cooperator",
        Competitor("SurelyNotBetrayer", "js-test-competitor:betrayer"),
        "js-test-competitor:random",
        "js-test-competitor:randomprinter",
    ]
    competitors_standoff = [
        Competitor("John", "js-brawl-test:random-1"),
        Competitor("Jack", "js-brawl-test:random-2"),
        Competitor("Joe", "js-brawl-test:random-3"),
        Competitor("Jill", "js-brawl-test:random-4"),
        Competitor("Jules", "js-brawl-test:random-5"),
    ]
    if game_name == "cooperation-legacy":
        run_1v1_round_robin(competitors_cooperation, play_cooperation_game_legacy)
    elif game_name == "cooperation":
        nb_rounds = rd.randint(10, 15)
        print(f"Playing {nb_rounds} rounds")
        run_1v1_round_robin(
            competitors_cooperation,
            partial(play_cooperation_game, nb_rounds=nb_rounds),
        )
    elif game_name == "random":
        run_1v1_round_robin(competitors_random, play_random_game)
    elif game_name == "standoff":
        rd.shuffle(competitors_standoff)
        play_standoff(competitors_standoff)
    else:
        print("Unknown game, exiting")
        exit(1)


if __name__ == "__main__":
    main("standoff")
