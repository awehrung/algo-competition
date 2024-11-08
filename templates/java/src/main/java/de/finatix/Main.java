package de.finatix;

import java.util.List;

/**
 * Example program: ignores arguments and always outputs "X"
 * <p>
 * Modify this to the best possible strategy, then upload the
 * docker image with the <code>build.sh</code> script.
 */
public class Main {
    public static void main(String[] args) {
        // use one of these at your discretion depending on the game
        // CooperationGameArgs cooperationLegacyGameArgs = parseCooperationGameArgsLegacy(args);
        // CooperationGameArgs cooperationGameArgs = parseCooperationGameArgs(args);
        // StandoffGameArgs standoffGameArgs = parseStandoffGameArgs(args);

        System.out.println("X");
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
