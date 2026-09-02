package de.finatix;

import org.apache.commons.lang3.tuple.Pair;

import java.util.List;

public record TradingGameArgs(
        int remainingItems,
        int myMoney,
        int myQuantity,
        int otherMoney,
        int otherQuantity,
        List<Pair<Integer, Integer>> bidsHistory
) {
}
