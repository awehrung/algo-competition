from typing import Tuple

import docker


def play_random_game(c1: str, c2: str) -> Tuple[int, int]:
    """
    Play a 1v1 test random game (testing only, will be deleted later)
    
    :param c1: docker image name of first player
    :param c2: docker image name of second player
    :return tuple of the scores: first player, second player
    """
    s1 = 0
    s2 = 0
    client = docker.from_env()
    r1 = int(client.containers.run(c1, "50 60").decode("utf-8").strip())
    r2 = int(client.containers.run(c2, "50 60").decode("utf-8").strip())
    if r1 == r2:
        print(f"Draw at {r1}")
        s1 += 1
        s2 += 1
    elif r1 > r2:
        print(f"{c1} wins by {r1} to {r2}")
        s1 += 2
    else:
        print(f"{c2} wins by {r2} to {r1}")
        s2 += 2
    return s1, s2
