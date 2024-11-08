from __future__ import annotations

import random as rd
import sys
from dataclasses import dataclass
from functools import partial
from typing import List

import docker
import yaml

from competitor import Competitor
from cooperation_game import play_cooperation_game_legacy, play_cooperation_game
from random_game import play_random_game
from round_robin_game_runner import run_1v1_round_robin
from standoff_game_runner import play_standoff


@dataclass(frozen=True)
class _Config:
    game_name: str
    competitors: List[Competitor]

    @staticmethod
    def load_from_file(config_path: str) -> _Config:
        with open(config_path, "r") as config_file:
            config = yaml.safe_load(config_file)
        if not "game" in config or not "competitors" in config:
            raise ValueError("Invalid config file")
        return _Config(
            config["game"], [Competitor.from_raw(c) for c in config["competitors"]]
        )


def run(config: _Config) -> None:
    client = docker.from_env()
    print(f"Pulling images")
    for c in config.competitors:
        if "/" in c.container_image:
            print(f"Pulling {c.container_image}")
            client.images.pull(c.container_image)

    if config.game_name == "cooperation-legacy":
        run_1v1_round_robin(config.competitors, play_cooperation_game_legacy)
    elif config.game_name == "cooperation":
        nb_rounds = rd.randint(10, 15)
        print(f"Playing {nb_rounds} rounds")
        run_1v1_round_robin(
            config.competitors,
            partial(play_cooperation_game, nb_rounds=nb_rounds),
        )
    elif config.game_name == "random":
        run_1v1_round_robin(config.competitors, play_random_game)
    elif config.game_name == "standoff":
        rd.shuffle(config.competitors)
        play_standoff(config.competitors)
    else:
        print("Unknown game, exiting")
        exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Expected exactly 1 argument (path to config file)")
        exit(1)
    run(_Config.load_from_file(sys.argv[1]))
