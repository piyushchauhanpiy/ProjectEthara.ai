package com.stockmarket.util;

import com.stockmarket.exception.FutureDateException;

import java.time.LocalDate;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;

public final class DateUtil {

    private static final DateTimeFormatter ISO_DATE = DateTimeFormatter.ISO_LOCAL_DATE;

    private DateUtil() {
    }

    public static LocalDate parseAndValidate(String date) {
        if (date == null || date.isBlank()) {
            throw new IllegalArgumentException("Date is required");
        }
        try {
            LocalDate parsed = LocalDate.parse(date.trim(), ISO_DATE);
            if (parsed.isAfter(LocalDate.now(ZoneOffset.UTC))) {
                throw new FutureDateException();
            }
            return parsed;
        } catch (DateTimeParseException e) {
            throw new IllegalArgumentException("Date must be in YYYY-MM-DD format");
        }
    }

    public static long toEpochStart(LocalDate date) {
        return date.atStartOfDay(ZoneOffset.UTC).toEpochSecond();
    }

    public static long toEpochEnd(LocalDate date) {
        return date.plusDays(1).atStartOfDay(ZoneOffset.UTC).toEpochSecond();
    }
}
