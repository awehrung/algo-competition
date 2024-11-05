const args = process.argv.slice(2)

/**
 * Example program: reads CLI arguments, converts them to integers,
 * then outputs a random integer between both input values.
 *
 * Also provides methods to parse arguments of the games defined in
 * the README.
 */

const lowerBound = parseInt(args[0], 10);
const upperBound = parseInt(args[1], 10);
console.log(Math.floor(Math.random() * (upperBound - lowerBound) + lowerBound));

// const cooperationGameArgs = parseCooperationGameArgs();
// const standoffGameArgs = parseStandoffGameArgs();

function parseCooperationGameArgs() {
    if (args.length != 2) {
        throw Error(`Expected 2 arguments, got ${args.length}`)
    }
    return {
        myMoves: args[0].split("/"),
        opponentMoves: args[1].split("/"),
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
