package de.finatix;

import lombok.AllArgsConstructor;
import lombok.Getter;

import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

public record CooperationGameArgs(
        List<Move> myMoves,
        List<Move> opponentMoves
) {
    @Override
    public String toString() {
        return "%s %s".formatted(
                myMoves.stream().map(Move::getEncoded).collect(Collectors.joining("/")),
                opponentMoves.stream().map(Move::getEncoded).collect(Collectors.joining("/"))
        );
    }

    @Getter
    @AllArgsConstructor
    enum Move {
        COOPERATE("C"),
        BETRAY("B"),
        ;

        private final String encoded;

        public static Move fromString(String raw) {
            return Arrays.stream(Move.values())
                    .filter(a -> raw.equals(a.encoded))
                    .findFirst()
                    .orElseThrow(() -> new IllegalArgumentException("Unknown move: %s".formatted(raw)));
        }
    }
}
