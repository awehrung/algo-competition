from typing import List, Callable, Tuple

from prettytable import PrettyTable

from competitor import Competitor


def run_1v1_round_robin(
    competitors: List[str | Competitor],
    game_func: Callable[[Competitor, Competitor], Tuple[int, int]],
) -> None:
    """
    Run the input 1v1 function in a round-robin mode, so that every competitor meets every other
    competitor. The scores are added across the games, and printed as a table at the end.

    :param competitors: Full list of competitors, each entry should be an instance of the Competitor
        dataclass, with friendly name and image path, e.g. Competitor("John", "registry.gitlab.com/my-competitor:v1").
        Optionally use simple strings instead, e.g. "my-competitor:v1".
    :param game_func: The 1v1 function that plays a match between two competitors. It takes the
        image names as input and produces the score of both players as output.
    """
    for i in range(len(competitors)):
        c = competitors[i]
        if isinstance(c, str):
            competitor = Competitor(c.split("/")[-1], c)
            competitors[i] = competitor
    competitors: List[Competitor]

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
        print(f"\n{c1.name} against {c2.name}")
        # add a breakpoint here for added suspense
        s1, s2 = game_func(c1, c2)
        scores[c1] += s1
        scores[c2] += s2

    print("\nScores after all matches:")
    sorted_results = [
        [v, k.name] for k, v in sorted(scores.items(), key=lambda item: -item[1])
    ]

    table = PrettyTable(["Points", "Competitor"], align="l")
    table.add_rows(sorted_results)
    print(table)
