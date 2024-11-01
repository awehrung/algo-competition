# Algorithm competition

## Introduction

This repo implements a system to make algorithms compete in any text-input/text-output game, independent of implementation language. The competing algorithms need to be docker images that take some text as input and produce some text as output, the concrete form of which depends on the game being played.

Along a runner script, the repo also provides templates to create compatible docker images from Javascript, Python, and Java code. 

## Game 1: Cooperation game (iterated prisoner's dilemma)

Imagine two opposing mafia criminals facing a high-stakes deal. They can cooperate to make lots of money... but this is not the only option. If one of them betrays the other during the operation, the payoff is even bigger for the betrayer, while the betrayed gets nothing. If they both decide to betray each other at the same time though, the deal fails, and they only get very little. In addition, this is not a one-time deal: this situation will arise many times during their mafia life, and both criminals will remember their previous decisions, as well as their counterpart's. What is the optimal strategy to make the most out of all deals?

This game is played between two players over 10 rounds. Each round, given the history of previous decisions, both players need to make a choice, between cooperation (C) and betrayal (B). The scoring is as follows:
* if both players betray: each get 1 point
* if one player betrays while the other cooperates: the betrayer gets 3 points, the other 0
* if both players cooperate: each get 2 points

Specification for competitors:
* Input: 2 lists of the previous decisions in the following format: `[C,B,C,C]`, the first representing your previous moves, the second representing your opponent's previous moves
* The input will be transmitted through `docker run` arguments, e.g. `docker run my-competitor:v1 "[B,C,C]" "[C,B,C]"`
* Output: 1 character representing the decision, either `C` for cooperation or `B` for betrayal
* The output will be read from the console, the container should not print anything else
* Any invalid output will result in forfeiting the game

The competition will pair every competitor in a round-robin tournament, adding the scores obtained each game. Greatest cumulated score wins the tournament.
