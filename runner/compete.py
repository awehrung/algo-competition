import random as rd

from cooperation_game import play_cooperation_game
from random_game import play_random_game
from round_robin_game_runner import run_1v1_round_robin
from standoff_game_runner import play_standoff


def main(game_name: str) -> None:
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
        run_1v1_round_robin(competitors_cooperation, play_cooperation_game)
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
