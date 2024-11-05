package de.finatix;

import java.util.Arrays;
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

//        CooperationGameArgs cooperationGameArgs = parseCooperationGameArgs(args);
//        StandoffGameArgs standoffGameArgs = parseStandoffGameArgs(args);
    }

    private static CooperationGameArgs parseCooperationGameArgs(String[] rawArgs) {
        if (rawArgs.length != 2) {
            throw new IllegalArgumentException("Expected 2 arguments, got %d".formatted(rawArgs.length));
        }
        return new CooperationGameArgs(
                Arrays.stream(rawArgs[0].split("/")).map(CooperationGameArgs.Move::fromString).toList(),
                Arrays.stream(rawArgs[1].split("/")).map(CooperationGameArgs.Move::fromString).toList()
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
