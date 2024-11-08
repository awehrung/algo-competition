const args = process.argv.slice(2)

/**
 * Example program: ignores arguments and always outputs "X"
 *
 * Modify this to the best possible strategy, then upload the
 * docker image with the `build.sh` script.
 */


// use one of these at your discretion depending on the game
// const cooperationLegacyGameArgs = parseCooperationGameArgsLegacy();
// const cooperationGameArgs = parseCooperationGameArgs();
// const standoffGameArgs = parseStandoffGameArgs();

console.log("X");

function parseCooperationGameArgsLegacy() {
    if (args.length == 0) {
        return {
            myMoves: [],
            opponentMoves: []
        }
    }
    if (args.length != 2) {
        throw Error(`Expected 2 arguments, got ${args.length}`)
    }
    return {
        myMoves: args[0].split("/"),
        opponentMoves: args[1].split("/"),
    }
}

function parseCooperationGameArgs() {
    if (args.length != 2) {
        throw Error(`Expected 2 arguments, got ${args.length}`)
    }
    return {
        myMoves: args[0].substring(1, args[0].length - 1).split(","),
        opponentMoves: args[1].substring(1, args[1].length - 1).split(","),
    }
}

function parseStandoffGameArgs() {
    if (args.length > 3 || args.length < 2) {
        throw Error(`Expected between 2 and 3 arguments, got ${args.length}`)
    }

    function parsePlayerState(raw) {
        const arr = raw.split("/")
        if (arr.length != 3) {
            throw Error(`Cannot parse player state, received array of length ${arr.length}`)
        }
        return {
            hp: parseInt(arr[0], 10),
            ammo: parseInt(arr[1], 10),
            lastAction: arr[2]
        }
    }

    return {
        me: parsePlayerState(args[0]),
        neighborLeft: parsePlayerState(args[1]),
        neighborRight: args.length == 3 ? parsePlayerState(args[2]) : null
    }
}
