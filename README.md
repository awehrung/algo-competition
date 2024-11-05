# Algorithm competition

## Introduction

This repo implements a system to make algorithms compete in any text-input/text-output game, independent of implementation language. The competing algorithms need to be docker images that take some text as input and produce some text as output, the concrete form of which depends on the game being played.

Along a runner script, the repo also provides templates to create compatible docker images from Javascript, Python, and Java code. The `src` directory contains sample code that should be edited to match the game specifications. In order to allow getting into the challenge more easily, functions to parse the input for both game defined below have been provided with the templates. To build the docker image from a template, simply run the `build.sh` script from the corresponding directory.

## How to compete

As the competition runner, gather docker images from the competitors and adapt the `runner/compete.py` script to run the correct game with the list of competitors.

As a competitor, build a docker image that matches the game specifications using the templates as starting points and publish it to a registry the competition runner has access to. Notify them about your entry, so that it can be added to the competition.

## Game 1: Cooperation game (iterated prisoner's dilemma)

Consider two opposing mafia criminals facing a high-stakes deal. They can cooperate to make lots of money... but this is not the only option. If one of them betrays the other during the operation, the payoff is even bigger for the betrayer, while the betrayed gets nothing. If they both decide to betray each other at the same time though, the deal fails, and they only get very little. In addition, this is not a one-time deal: this situation will arise many times during their mafia life, and both criminals will remember their previous decisions, as well as their counterpart's. What is the optimal strategy to make the most out of all deals?

This game is played between two players over 10 rounds. Each round, given the history of previous decisions, both players need to make a choice, between cooperation (C) and betrayal (B). The scoring is as follows:
* if both players betray: each get 1 point
* if one player betrays while the other cooperates: the betrayer gets 3 points, the other 0
* if both players cooperate: each get 2 points

Specification for competitors:
* Input: 2 lists of the previous decisions in the following format: `C/B/C/C`, the first representing your previous moves, the second representing your opponent's previous moves
* The input will be transmitted through `docker run` arguments, e.g. `docker run my-competitor:v1 B/C/C C/B/C`
* Output: 1 character representing the decision, either `C` for cooperation or `B` for betrayal
* The output will be read from the console, the container should not print anything else
* Any invalid output will result in forfeiting the game

The competition will pair every competitor in a round-robin tournament, adding the scores obtained each game. Greatest cumulated score wins the tournament.

## Game 2: Mega mexican standoff

After months of betraying one another (see game 1), it finally happened: a gigantic mexican standoff involving all the players, standing in a circle. Each round, you have 3 options at your disposal: Shooting at your neighbors, protecting yourself, or reloading. If you shoot, pistols in both hands fire at the same time, hitting both people standing next to you in the circle (or the one person in front of you if only two people are left). This consumes 1 ammo and inflicts 10 damage, reduced to 4 damage if the target chose to protect themselves. If you reload, you gain 1 ammo back up to your starting maximum of 2. Invalid actions (e.g. shooting with no ammo, reloading with full ammo, unknown output) result in the player doing nothing for the round. Every player starts with 30 health-points, can you be the last one standing?

Specification for competitors:
* Input: up to 3 triplets of HP, ammo and last action in the following format: `30/2/P`, the first being yourself and the others representing your neighbors
* If only two people are left alive, then the third triplet is omitted
* The "last action" are encoded as letters: `S` for Shooting, `P` for Protecting, `R` for Reloading and `N` for Nothing.
* The input will be transmitted through `docker run` arguments, e.g. `docker run my-competitor:v1 20/1/P 20/0/N 16/2/R`
* Output: 1 character representing the decision, using the same encoding as "last action"
* The output will be read from the console, the container should not print anything else
* Any invalid output will result in the action "Nothing" being chosen

The competition will shuffle the competitors to build a starting circle and runs until at most 1 player is left alive.

## Notes

The inspiration for this repo comes from [Robert Axelrod's tournaments](https://www.wikiwand.com/en/articles/The_Evolution_of_Cooperation#Background:_Axelrod's_tournaments) (warning: big spoilers for game 1) from the 80s.

Game 2 is based on the author's memory of a childhood game.

Some lines of code are commented with a suggestion to "add breakpoint" → Setting a breakpoint at these locations will pause between rounds to allow for analysis, tension build-up and dramatic reveals.
