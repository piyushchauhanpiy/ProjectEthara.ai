package com.stockmarket.util;

import com.stockmarket.exception.InvalidTickerException;

import java.util.regex.Pattern;

public final class TickerUtil {

    private static final Pattern TICKER_PATTERN = Pattern.compile("^[A-Za-z0-9=.-]{1,12}$");

    private TickerUtil() {
    }

    public static String sanitize(String ticker) {
        if (ticker == null || ticker.isBlank()) {
            throw new InvalidTickerException("Ticker symbol is required");
        }
        String cleaned = ticker.trim().toUpperCase();
        if (!TICKER_PATTERN.matcher(cleaned).matches()) {
            throw new InvalidTickerException("Invalid ticker format: " + ticker);
        }
        return cleaned;
    }
}
