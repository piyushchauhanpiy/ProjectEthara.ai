package com.stockmarket.exception;

public class InvalidTickerException extends RuntimeException {

    public InvalidTickerException(String message) {
        super(message);
    }
}
