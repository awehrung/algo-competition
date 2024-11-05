package de.finatix;

import lombok.AllArgsConstructor;
import lombok.Getter;

import java.util.Arrays;

public record StandoffGameArgs(
        PlayerState me,
        PlayerState neighborLeft,
        PlayerState neighborRight
) {
    record PlayerState(int hp, int ammo, Action lastAction) {
        public static PlayerState fromString(String raw) {
            String[] attributes = raw.split("/");
            if (attributes.length != 3) {
                throw new IllegalArgumentException("Expected 3 attributes, got %s".formatted(attributes.length));
            }
            return new PlayerState(Integer.parseInt(attributes[0]), Integer.parseInt(attributes[1]), Action.fromString(attributes[2]));
        }
    }

    @Getter
    @AllArgsConstructor
    enum Action {
        NOTHING("N"),
        SHOOT("S"),
        PROTECT("P"),
        RELOAD("R"),
        ;

        private final String encoded;

        public static Action fromString(String raw) {
            return Arrays.stream(Action.values())
                    .filter(a -> raw.equals(a.encoded))
                    .findFirst()
                    .orElseThrow(() -> new IllegalArgumentException("Unknown action: %s".formatted(raw)));
        }
    }
}
