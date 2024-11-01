import docker
from docker.errors import ContainerError
from prettytable import PrettyTable


def main():
    competitors_random = [
        "my-java-competitor:0.0.1",
        "my-java-competitor:0.0.2",
        "my-python-competitor:0.0.1",
        "my-javascript-competitor:0.0.1",
    ]

    competitors = [
        "js-test-competitor:cooperator",
        "js-test-competitor:betrayer",
        "js-test-competitor:random"
    ]

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
        s1, s2 = _play_cooperation_game(c1, c2)
        scores[c1] += s1
        scores[c2] += s2

    print("\nScores after all matches:")
    sorted_results = [
        [v, k] for k, v in sorted(scores.items(), key=lambda item: -item[1])
    ]
    table = PrettyTable(["Points", "Competitor"], align="l")
    table.add_rows(sorted_results)
    print(table)


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
            print(f"{c1} chose invalid move, forfeiting the game")
            return 0, score_on_opponent_forfeit
        elif not is_valid_move(decision_2):
            print(f"{c2} chose invalid move, forfeiting the game")
            return score_on_opponent_forfeit, 0

        moves_1.append(decision_1)
        moves_2.append(decision_2)

        if [decision_1, decision_2] == ["B", "B"]:
            print("Both betray, no points")
        elif [decision_1, decision_2] == ["B", "C"]:
            print(f"{c1} betrays {c2} and wins 3 points")
            score_1 += 3
        elif [decision_1, decision_2] == ["C", "B"]:
            print(f"{c2} betrays {c1} and wins 3 points")
            score_2 += 3
        else:
            print("Both cooperate, 1 point each")
            score_1 += 1
            score_2 += 2
    print(f"Final score: {c1}: {score_1}, {c2}: {score_2}")
    return score_1, score_2


if __name__ == "__main__":
    main()
