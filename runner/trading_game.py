import docker
from dataclasses import dataclass
from docker.errors import ContainerError
from typing import Tuple, List, Optional

from competitor import Competitor


def play_trading_game(
    c1: Competitor, c2: Competitor, money_gone_mode: bool
) -> Tuple[int, int]:
    game_state = _GameState(c1.name, c2.name, 10, 50, money_gone_mode)

    client = docker.from_env()
    while game_state.r > 0:
        print(game_state.current_status())
        # print(game_state.m1, game_state.m2)
        try:
            bid_1 = _decode_output(
                client.containers.run(
                    c1.container_image, game_state.encode_for_player_1()
                )
            )
        except ContainerError as e:
            print(f"{c1.name} threw error, forfeiting the game -- {e}")
            return 0, _Config.default_victory_points
        try:
            bid_2 = _decode_output(
                client.containers.run(
                    c2.container_image, game_state.encode_for_player_2()
                )
            )
        except ContainerError as e:
            print(f"{c2.name} threw error, forfeiting the game -- {e}")
            return _Config.default_victory_points, 0

        bids_validity_error = game_state.check_bids_validity(bid_1, bid_2)
        if bids_validity_error is not None:
            reason, s1, s2 = bids_validity_error
            print(reason)
            return s1, s2

        round_result = game_state.apply_bids(int(bid_1), int(bid_2))
        print(round_result)

    game_result, score_1, score_2 = game_state.determine_winner()
    print(f"\n--> {game_result}")
    return score_1, score_2


@dataclass(frozen=True)
class _Config:
    default_victory_points = 10


class _GameState:
    def __init__(
        self,
        p1_name: str,
        p2_name: str,
        item_count: int,
        initial_money: int,
        money_gone_mode: bool,
    ):
        self.p1 = p1_name
        self.p2 = p2_name
        assert item_count % 2 == 0, "Need even item count"
        self.r = item_count
        self.m1 = initial_money
        self.q1 = 0
        self.m2 = initial_money
        self.q2 = 0
        self.history: List[Tuple[int, int]] = []
        self.money_gone_mode = money_gone_mode

    def current_status(self):
        return f"""Items remaining to sell: {self.r}
{self.p1} has {self.q1} item(s) and {self.m1} money
{self.p2} has {self.q2} item(s) and {self.m2} money"""

    def encode_for_player_1(self):
        encoded_history = " ".join(f"{b1}/{b2}" for (b1, b2) in self.history)
        return f"R={self.r} MM={self.m1} MQ={self.q1} OM={self.m2} OQ={self.q2} {encoded_history}"

    def encode_for_player_2(self):
        encoded_history = " ".join(f"{b2}/{b1}" for (b1, b2) in self.history)
        return f"R={self.r} MM={self.m2} MQ={self.q2} OM={self.m1} OQ={self.q1} {encoded_history}"

    def check_bids_validity(
        self, bid_1: str, bid_2: str
    ) -> Optional[Tuple[str, int, int]]:
        """
        On error, reason of invalidity and score to apply
        """
        # print(bid_1, bid_2, "---")
        bid_1_valid = bid_1.isdigit() and 0 <= int(bid_1) <= self.m1
        bid_2_valid = bid_2.isdigit() and 0 <= int(bid_2) <= self.m2
        if bid_1_valid and bid_2_valid:
            return None
        if bid_2_valid and not bid_1_valid:
            return (
                f"Invalid bid of {bid_1} by {self.p1}: should be an integer between 0 and {self.m1}",
                0,
                _Config.default_victory_points,
            )
        if bid_1_valid and not bid_2_valid:
            return (
                f"Invalid bid of {bid_2} by {self.p2}: should be an integer between 0 and {self.m2}",
                _Config.default_victory_points,
                0,
            )
        return "Invalid bid by both players", 0, 0

    def apply_bids(self, bid_1: int, bid_2: int) -> str:
        self.r -= 2
        self.history.append((bid_1, bid_2))

        if bid_1 > bid_2:
            self.q1 += 2
            self.m1 -= bid_1
            if self.money_gone_mode:
                self.m2 -= bid_2
            return f"{self.p1} wins 2 items with a bid of {bid_1} over {bid_2}"
        elif bid_1 < bid_2:
            self.q2 += 2
            self.m2 -= bid_2
            if self.money_gone_mode:
                self.m1 -= bid_1
            return f"{self.p2} wins 2 items with a bid of {bid_2} over {bid_1}"
        else:
            self.q1 += 1
            self.q2 += 1
            if self.money_gone_mode:
                self.m1 -= bid_1
                self.m2 -= bid_2
                explanation_ext = " at full bid price"
            else:
                self.m1 -= (bid_1 + 1) // 2
                self.m2 -= (bid_2 + 1) // 2
                explanation_ext = f" at half bid price of {(bid_1 + 1) // 2}"
            return f"Draw at {bid_1}: each player gets 1 item{explanation_ext}"

    def determine_winner(self) -> Tuple[str, int, int]:
        if self.q1 > self.q2:
            return f"{self.p1} wins {self.q1} to {self.q2}!", self.q1, self.q2
        if self.q1 < self.q2:
            return f"{self.p2} wins {self.q2} to {self.q1}!", self.q1, self.q2
        return f"Draw at {self.q1}!", self.q1, self.q1


def _decode_output(raw_output: bytes) -> str:
    return raw_output.decode("utf-8").strip()
