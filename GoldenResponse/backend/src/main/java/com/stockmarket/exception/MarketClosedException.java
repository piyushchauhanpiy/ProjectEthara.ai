package com.stockmarket.exception;

public class MarketClosedException extends RuntimeException {

    public MarketClosedException() {
        super("Market Closed");
    }
}
