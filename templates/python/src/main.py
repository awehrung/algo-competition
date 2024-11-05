import sys

import numpy as np

from cooperation_game_args import CooperationGameArgs, Move
from standoff_game_args import StandoffGameArgs, PlayerState


def main():
    lower_bound = int(sys.argv[1])
    upper_bound = int(sys.argv[2])
    print(np.random.randint(lower_bound, upper_bound))

    # cooperation_game_args = parse_cooperation_game_args()
    # standoff_game_args = parse_standoff_game_args()


def parse_cooperation_game_args() -> CooperationGameArgs:
    if len(sys.argv) != 3:
        raise Exception(f"Expected 2 arguments, got {len(sys.argv) - 1}")
    return CooperationGameArgs(
        [Move.from_str(m) for m in sys.argv[1].split("/")],
        [Move.from_str(m) for m in sys.argv[2].split("/")],
    )


def parse_standoff_game_args() -> StandoffGameArgs:
    if len(sys.argv) > 4 or len(sys.argv) < 3:
        raise Exception(f"Expected between 2 and 3 arguments, got {len(sys.argv) - 1}")
    return StandoffGameArgs(
        PlayerState.from_str(sys.argv[1]),
        PlayerState.from_str(sys.argv[2]),
        PlayerState.from_str(sys.argv[3]) if len(sys.argv) == 4 else None,
    )


if __name__ == "__main__":
    """
    Example program: reads CLI arguments, converts them to integers,
    then outputs a random integer between both input values.
    
    Also provides methods to parse arguments of the games defined in
    the README.
    """
    main()
