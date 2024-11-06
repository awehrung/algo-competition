package de.finatix;

import java.util.List;
import java.util.Random;

/**
 * Example program: reads CLI arguments, converts them to integers,
 * then outputs a random integer between both input values.
 * <p>
 * Also provides methods to parse arguments of the games defined in
 * the README.
 */
public class Main {
    public static void main(String[] args) {
        Random rd = new Random();
        int lowerBound = Integer.parseInt(args[0]);
        int upperBound = Integer.parseInt(args[1]);
        System.out.println(rd.nextInt(lowerBound, upperBound));

//        CooperationGameArgs cooperationGameArgs = parseCooperationGameArgsLegacy(args);
//        CooperationGameArgs cooperationGameArgs = parseCooperationGameArgs(args);
//        StandoffGameArgs standoffGameArgs = parseStandoffGameArgs(args);
    }

    private static CooperationGameArgs parseCooperationGameArgsLegacy(String[] rawArgs) {
        if (rawArgs.length == 0) {
            return new CooperationGameArgs(List.of(), List.of());
        }
        if (rawArgs.length != 2) {
            throw new IllegalArgumentException("Expected 2 arguments, got %d".formatted(rawArgs.length));
        }
        return new CooperationGameArgs(
                CooperationGameArgs.Move.listFromRaw(rawArgs[0], true),
                CooperationGameArgs.Move.listFromRaw(rawArgs[1], true)
        );
    }

    private static CooperationGameArgs parseCooperationGameArgs(String[] rawArgs) {
        if (rawArgs.length != 2) {
            throw new IllegalArgumentException("Expected 2 arguments, got %d".formatted(rawArgs.length));
        }
        return new CooperationGameArgs(
                CooperationGameArgs.Move.listFromRaw(rawArgs[0]),
                CooperationGameArgs.Move.listFromRaw(rawArgs[1])
        );
    }

    private static StandoffGameArgs parseStandoffGameArgs(String[] rawArgs) {
        if (rawArgs.length > 3 || rawArgs.length < 2) {
            throw new IllegalArgumentException("Expected between 2 and 3 arguments, got %d".formatted(rawArgs.length));
        }
        return new StandoffGameArgs(
                StandoffGameArgs.PlayerState.fromString(rawArgs[0]),
                StandoffGameArgs.PlayerState.fromString(rawArgs[1]),
                rawArgs.length == 3 ? StandoffGameArgs.PlayerState.fromString(rawArgs[2]) : null
        );
    }
}
