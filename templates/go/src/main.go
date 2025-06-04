package main

import (
	"flag"
	"fmt"
	"strconv"
	"strings"
)

func main() {
	// Example program: ignores arguments and always outputs "X"
	//
	// Modify this to the best possible strategy, then upload the
	// docker image with the `build.sh` script.

	flag.Parse()

	// use one of these at your discretion depending on the game
	//rawArgs := flag.Args()
	//args := parseCooperationGameArgs(rawArgs)
	//args := parseStandoffGameArgs(rawArgs)
	//fmt.Println(*args)

	fmt.Println("X")
}

func parseCooperationGameArgs(args []string) *cooperationGameArgs {
	if len(args) != 2 {
		panic(fmt.Sprintf("Expected 2 arguments, got %d", len(args)))
	}
	return &cooperationGameArgs{
		parseMoves(args[0]),
		parseMoves(args[1]),
	}
}

type cooperationGameArgs struct {
	myMoves       []string
	opponentMoves []string
}

func parseMoves(movesRaw string) []string {
	if movesRaw == "[]" {
		return []string{}
	}
	return strings.Split(movesRaw[1:len(movesRaw)-1], ",")
}

func parseStandoffGameArgs(args []string) *standoffGameArgs {
	if len(args) > 3 || len(args) < 2 {
		panic(fmt.Sprintf("Expected between 2 and 3 arguments, got %d", len(args)))
	}

	var neighborRight *playerState
	if len(args) == 3 {
		neighborRight = parsePlayerState(args[2])
	}

	return &standoffGameArgs{
		me:            parsePlayerState(args[0]),
		neighborLeft:  parsePlayerState(args[1]),
		neighborRight: neighborRight,
	}
}

type standoffGameArgs struct {
	me            *playerState
	neighborLeft  *playerState
	neighborRight *playerState
}

type playerState struct {
	hp         int
	ammo       int
	lastAction string
}

func parsePlayerState(playerStateRaw string) *playerState {
	attributes := strings.Split(playerStateRaw, "/")
	if len(attributes) != 3 {
		panic(fmt.Sprintf("Expected 3 arguments, got: %d", len(attributes)))
	}

	hp, err := strconv.Atoi(attributes[0])
	if err != nil {
		panic(fmt.Sprintf("Could not parse HP: %s", err.Error()))
	}
	ammo, err := strconv.Atoi(attributes[1])
	if err != nil {
		panic(fmt.Sprintf("Could not parse ammo: %s", err.Error()))
	}

	return &playerState{
		hp:         hp,
		ammo:       ammo,
		lastAction: attributes[2],
	}
}
