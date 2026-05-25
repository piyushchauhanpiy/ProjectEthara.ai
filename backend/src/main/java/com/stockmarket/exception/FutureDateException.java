package com.stockmarket.exception;

public class FutureDateException extends RuntimeException {

    public FutureDateException() {
        super("Future dates are not allowed");
    }
}
