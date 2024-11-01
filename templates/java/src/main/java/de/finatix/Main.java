package de.finatix;

import java.util.Random;

/**
 * Example program: reads CLI arguments, converts them to integers,
 * then outputs a random integer between both input values
 */
public class Main {
    public static void main(String[] args) {
        Random rd = new Random();
        int lowerBound = Integer.parseInt(args[0]);
        int upperBound = Integer.parseInt(args[1]);
        System.out.println(rd.nextInt(lowerBound, upperBound));
    }
}
