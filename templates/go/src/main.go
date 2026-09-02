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
	//args := parseCooperationGameArgs(flag.Args())
	//args := parseStandoffGameArgs(flag.Args())
	//args := parseTradingGameArgs(flag.Args())
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

func parseTradingGameArgs(args []string) *tradingGameArgs {
	if len(args) < 5 {
		panic(fmt.Sprintf("Expected at least 5 arguments, got %d", len(args)))
	}

	return &tradingGameArgs{
		remainingItems: toIntUnsafe(strings.Split(args[0], "=")[1]),
		myMoney:        toIntUnsafe(strings.Split(args[1], "=")[1]),
		myQuantity:     toIntUnsafe(strings.Split(args[2], "=")[1]),
		otherMoney:     toIntUnsafe(strings.Split(args[3], "=")[1]),
		otherQuantity:  toIntUnsafe(strings.Split(args[4], "=")[1]),
		bidsHistory:    parseBidsHistory(args[5:]),
	}
}

func parseBidsHistory(history []string) []bid {
	var bids []bid
	for _, h := range history {
		splitEntry := strings.Split(h, "/")
		bids = append(bids, bid{
			myBid:    toIntUnsafe(splitEntry[0]),
			otherBid: toIntUnsafe(splitEntry[1]),
		})
	}
	return bids
}

func toIntUnsafe(s string) int {
	i, err := strconv.Atoi(s)
	if err != nil {
		panic(err)
	}
	return i
}

type tradingGameArgs struct {
	remainingItems int
	myMoney        int
	myQuantity     int
	otherMoney     int
	otherQuantity  int
	bidsHistory    []bid
}

type bid struct {
	myBid    int
	otherBid int
}
