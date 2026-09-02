import sys
from random import randint

from cooperation_game_args import CooperationGameArgs, Move
from standoff_game_args import StandoffGameArgs, PlayerState
from trading_game_args import TradingGameArgs


def main():
    """
    Example program: ignores arguments and always outputs "X"

    Modify this to the best possible strategy, then upload the
    docker image with the `build.sh` script.
    """

    # use one of these at your discretion depending on the game
    # cooperation_game_args = parse_cooperation_game_args_legacy()
    # cooperation_game_args = parse_cooperation_game_args()
    # standoff_game_args = parse_standoff_game_args()
    # trading_game_args = parse_trading_game_args()

    print("X")


def parse_cooperation_game_args_legacy() -> CooperationGameArgs:
    if len(sys.argv) == 1:
        return CooperationGameArgs([], [])
    if len(sys.argv) != 3:
        raise Exception(f"Expected 2 arguments, got {len(sys.argv) - 1}")
    return CooperationGameArgs(
        Move.list_from_raw(sys.argv[1], True), Move.list_from_raw(sys.argv[2], True)
    )


def parse_cooperation_game_args() -> CooperationGameArgs:
    if len(sys.argv) != 3:
        raise Exception(f"Expected 2 arguments, got {len(sys.argv) - 1}")
    return CooperationGameArgs(
        Move.list_from_raw(sys.argv[1]), Move.list_from_raw(sys.argv[2])
    )


def parse_standoff_game_args() -> StandoffGameArgs:
    if len(sys.argv) > 4 or len(sys.argv) < 3:
        raise Exception(f"Expected between 2 and 3 arguments, got {len(sys.argv) - 1}")
    return StandoffGameArgs(
        PlayerState.from_str(sys.argv[1]),
        PlayerState.from_str(sys.argv[2]),
        PlayerState.from_str(sys.argv[3]) if len(sys.argv) == 4 else None,
    )

def parse_trading_game_args() -> TradingGameArgs:
    if len(sys.argv) < 6:
        raise Exception(f"Expected at least 5 arguments, got {len(sys.argv) - 1}")
    return TradingGameArgs(
        int(sys.argv[1].split("=")[1]),
        int(sys.argv[2].split("=")[1]),
        int(sys.argv[3].split("=")[1]),
        int(sys.argv[4].split("=")[1]),
        int(sys.argv[5].split("=")[1]),
        [(int(h.split("/")[0]), int(h.split("/")[1])) for h in sys.argv[6:]]
    )


if __name__ == "__main__":
    main()
