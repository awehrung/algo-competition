# Algorithm competition

## Introduction

This repo implements a system to make algorithms compete in any text-input/text-output game, independent of
implementation language. The competing algorithms need to be docker images that take some text as input and produce some
text as output, the concrete form of which depends on the game being played.

Along a runner script, the repo also provides templates to create compatible docker images from Javascript, Python,
Java, and Go code. The `src` directory contains sample code that should be edited to match the game specifications. In
order to allow getting into the challenge more easily, functions to parse the input for both games defined below have
been provided with the templates. To test the algorithm, use the `test.sh` script from the corresponding directory. To
build the docker image from a template and push it to a registry, simply run the `build.sh` script from the same
directory.

## How to compete

**As a competitor**, build a docker image that matches the game specifications using the templates as starting points
and publish it to a registry the competition runner has access to. Notify them about your entry, so that it can be added
to the competition. Check the `templates` directory for starting points in Java, Javascript, Python, and Go.

**As the competition runner**, gather docker images from the competitors and create a config file for the game (see
examples under `runner/competition-config`). Make sure you have all dependencies installed, then run the
`runner/compete.py` script with the path to your config file as the program argument to run the game.

```shell
cd runner
pip install -r requirements.txt
python compete.py competition-config/example-config-cooperation.yml
```

Be aware that the docker images need to be compatible with your CPU architecture (submissions built on an ARM-based Mac
will not work on x86-based PCs).

## Game 1: Cooperation game (iterated prisoner's dilemma)

_Consider two opposing mafia criminals facing a high-stakes deal. They can cooperate to make lots of money... but this
is not the only option. If one of them betrays the other during the operation, the payoff is even bigger for the
betrayer, while the betrayed gets nothing. If they both decide to betray each other at the same time though, the deal
fails, and they only get very little. In addition, this is not a one-time deal: this situation will arise many times
during their mafia life, and both criminals will remember their previous decisions, as well as their counterpart's. What
is the optimal strategy to make the most out of all deals?_

This game is played between two players over 10 to 15 rounds (unknown to the players, but the same for each pairing).
Each round, given the history of previous decisions, both players need to make a choice, between cooperation (C) and
betrayal (B). The scoring is as follows:

* if both players betray: each get 1 point
* if one player betrays while the other cooperates: the betrayer gets 3 points, the other 0
* if both players cooperate: each get 2 points

Specification for competitors:

* Input: 2 lists of the previous decisions in the following format: `[C,B,C,C]`, the first representing your previous
  moves, the second representing your opponent's previous moves
* The input will be transmitted through `docker run` arguments, e.g. `docker run my-competitor:v1 "[B,C,C]" "[C,B,C]"`
* Output: 1 character representing the decision, either `C` for cooperation or `B` for betrayal
* The output will be read from the console, the container should not print anything else
* Any invalid output will result in forfeiting the game

The competition will pair every competitor in a round-robin tournament, adding the scores obtained each game. Greatest
cumulated score wins the tournament.

## Game 1 legacy: First version of cooperation game

The rules are the same as in the current game 1, with the following exceptions:

* In the legacy version, exactly 10 rounds are played. The updated version prevents using this information for
  last-minute betrayals.
* The input format is slightly different: `C/B/C/C` for each player, complete command looks like following:
  `docker run my-competitor:v1 B/C/C C/B/C`. The new version removes the ambiguity for the very first round of the game.

## Game 2: Mega mexican standoff

_After months of betraying one another (see game 1), it finally happened: a gigantic mexican standoff involving all the
players, standing in a circle. Each round, you have 3 options at your disposal: Shooting at your neighbors, protecting
yourself, or reloading. If you shoot, pistols in both hands fire at the same time, hitting both people standing next to
you in the circle (or the one person in front of you if only two people are left). This consumes 1 ammo and inflicts 10
damage, reduced to 4 damage if the target chose to protect themselves. If you reload, you gain 1 ammo back up to your
starting maximum of 2. Invalid actions (e.g. shooting with no ammo, reloading with full ammo, unknown output) result in
the player doing nothing for the round. Every player starts with 30 health-points, can you be the last one standing?_

Specification for competitors:

* Input: up to 3 triplets of HP, ammo and last action in the following format: `30/2/P`, the first being yourself and
  the others representing your neighbors
* If only two people are left alive, then the third triplet is omitted
* The "last action" are encoded as letters: `S` for Shooting, `P` for Protecting, `R` for Reloading and `N` for Nothing.
* The input will be transmitted through `docker run` arguments, e.g. `docker run my-competitor:v1 20/1/P 20/0/N 16/2/R`
* Output: 1 character representing the decision, using the same encoding as "last action"
* The output will be read from the console, the container should not print anything else
* Any invalid output will result in the action "Nothing" being chosen

The competition will shuffle the competitors to build a starting circle and runs until at most 1 player is left alive.

## Game 3: Trading game

_You survived the escalation and are ready to embrace a quieter life. Let's start buying stuff! You stand at an auction
with 10 items to be bought and 50 money at your disposal. Each round, 2 of the items will be sold. You have to bid
against another competitor, highest bid wins the items. In case of a draw, you get one item each. But beware! In the
`money-gone` mode, if you lose the bid, you do not get your money back. Your goal is to maximize your total of items
owned at the end of the game._

This game is played in a round-robin format: every competitor is matched to every other competitor in duels. Before each
duel, the auction is reset to the initial conditions (10 items to buy, 50 money available). Each duel lasts 5 rounds (2
items auctioned per round). Every round, each competitor receives the current state of the auction as input, and must
output their bid for the round. There are 2 games modes possible (see config file): in `money-gone`, the money invested
on a lost bid does not get refunded; in `money-not-gone`, lost bids get refunded to the competitor.

Specification for competitors:

* All numbers (money, item count) are integers
* Input: the auction state consisting of the following attributes
    * Count of remaining items to be sold --> `R`
    * Your remaining funds aka "My money" --> `MM`
    * The amount of items you bought aka "My quantity" --> `MQ`
    * Your opponent's funds aka "Other money" --> `OM`
    * The amount of items your opponent bought aka "Other quantity" --> `OQ`
    * The bid history as a space-separated list of `myBid/otherBid`
    * Complete example: `R=4 MM=23 MQ=2 OM=15 OQ=4 10/5 15/16 3/14`
* The input will be transmitted through `docker run` arguments, e.g.
  `docker run my-competitor:v1 R=10 MM=50 MQ=0 OM=50 OQ=0`
* Output: your bid for the round as a number
* The output will be read from the console, the container should not print anything else
* Any invalid output (not a number, negative number, greater than available funds, ...) will result in a forfeit of the
  current auction

Your score in each round is the amount of items you managed to buy. Greatest cumulated score wins the tournament.

## Notes

The inspiration for this repo comes
from [Robert Axelrod's tournaments](https://www.wikiwand.com/en/articles/The_Evolution_of_Cooperation#Background:_Axelrod's_tournaments)
from the 80s mentioned in [this Veritasium YouTube video](https://www.youtube.com/watch?v=mScpHTIi-kM) (warning: big
spoilers for game 1).

Game 2 is based on the author's memory of a childhood game.

Some lines of code are commented with a suggestion to "add breakpoint" → Setting a breakpoint at these locations will
pause between rounds to allow for analysis, tension build-up and dramatic reveals.
