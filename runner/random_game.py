from typing import Tuple

import docker

from competitor import Competitor


def play_random_game(c1: Competitor, c2: Competitor) -> Tuple[int, int]:
    """
    Play a 1v1 test random game (testing only, will be deleted later)
    
    :param c1: first player
    :param c2: second player
    :return tuple of the scores: first player, second player
    """
    s1 = 0
    s2 = 0
    client = docker.from_env()
    r1 = int(client.containers.run(c1.container_image, "50 60").decode("utf-8").strip())
    r2 = int(client.containers.run(c2.container_image, "50 60").decode("utf-8").strip())
    if r1 == r2:
        print(f"Draw at {r1}")
        s1 += 1
        s2 += 1
    elif r1 > r2:
        print(f"{c1.name} wins by {r1} to {r2}")
        s1 += 2
    else:
        print(f"{c2.name} wins by {r2} to {r1}")
        s2 += 2
    return s1, s2
