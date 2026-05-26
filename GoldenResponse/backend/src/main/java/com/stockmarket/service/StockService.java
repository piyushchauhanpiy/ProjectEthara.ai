package com.stockmarket.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.stockmarket.config.CacheConfig;
import com.stockmarket.dto.StockHistoryResponse;
import com.stockmarket.dto.StockLiveResponse;
import com.stockmarket.exception.MarketClosedException;
import com.stockmarket.exception.ResourceNotFoundException;
import com.stockmarket.integration.YahooFinanceClient;
import com.stockmarket.util.DateUtil;
import com.stockmarket.util.TickerUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.ZoneOffset;

@Service
@RequiredArgsConstructor
@Slf4j
public class StockService {

    private final YahooFinanceClient yahooFinanceClient;
    private final ObjectMapper objectMapper;

    @Cacheable(value = CacheConfig.LIVE_STOCKS, key = "#ticker")
    public StockLiveResponse getLiveStockData(String ticker) {
        String symbol = TickerUtil.sanitize(ticker);
        String rawJson = yahooFinanceClient.fetchLiveQuote(symbol).block();
        return parseLiveResponse(symbol, rawJson);
    }

    @Cacheable(value = CacheConfig.HISTORICAL_STOCKS, key = "#ticker + '_' + #date")
    public StockHistoryResponse getHistoricalStockData(String ticker, String date) {
        String symbol = TickerUtil.sanitize(ticker);
        LocalDate targetDate = DateUtil.parseAndValidate(date);
        String dateStr = targetDate.toString();

        long period1 = DateUtil.toEpochStart(targetDate);
        long period2 = DateUtil.toEpochEnd(targetDate);

        log.info("Fetching historical data for {} on {} (period1: {}, period2: {})", symbol, dateStr, period1, period2);
        String rawJson = yahooFinanceClient.fetchChartHistory(symbol, period1, period2).block();
        log.info("Received raw JSON: {}", rawJson);
        return parseHistoryResponse(symbol, dateStr, targetDate, rawJson);
    }

    private StockLiveResponse parseLiveResponse(String symbol, String rawJson) {
        try {
            JsonNode root = objectMapper.readTree(rawJson);
            JsonNode results = root.path("quoteResponse").path("result");

            if (!results.isArray() || results.isEmpty()) {
                throw new ResourceNotFoundException("Ticker not found: " + symbol);
            }

            JsonNode data = results.get(0);
            if (data.path("regularMarketPrice").isMissingNode() || data.path("regularMarketPrice").isNull()) {
                throw new ResourceNotFoundException("No market data for ticker: " + symbol);
            }

            String companyName = data.path("longName").asText(null);
            if (companyName == null || companyName.isBlank()) {
                companyName = data.path("shortName").asText(symbol);
            }

            return StockLiveResponse.builder()
                    .ticker(data.path("symbol").asText(symbol))
                    .companyName(companyName)
                    .currentPrice(data.path("regularMarketPrice").asDouble())
                    .open(data.path("regularMarketOpen").asDouble())
                    .high(data.path("regularMarketDayHigh").asDouble())
                    .low(data.path("regularMarketDayLow").asDouble())
                    .previousClose(data.path("regularMarketPreviousClose").asDouble())
                    .volume(data.path("regularMarketVolume").asLong(0L))
                    .currency(data.path("currency").asText("USD"))
                    .marketState(data.path("marketState").asText("UNKNOWN"))
                    .timestamp(data.path("regularMarketTime").asLong(0L))
                    .build();
        } catch (ResourceNotFoundException e) {
            throw e;
        } catch (Exception e) {
            log.error("Failed to parse live data for {}", symbol, e);
            throw new ResourceNotFoundException("Unable to parse live data for: " + symbol);
        }
    }

    private StockHistoryResponse parseHistoryResponse(String symbol, String dateStr,
                                                      LocalDate targetDate, String rawJson) {
        try {
            JsonNode root = objectMapper.readTree(rawJson);
            JsonNode chart = root.path("chart");

            if (chart.path("error").has("code")) {
                throw new ResourceNotFoundException("Historical data not found for: " + symbol);
            }

            JsonNode results = chart.path("result");
            if (!results.isArray() || results.isEmpty()) {
                throw new MarketClosedException();
            }

            JsonNode dataNode = results.get(0);
            JsonNode timestamps = dataNode.path("timestamp");

            if (!timestamps.isArray() || timestamps.isEmpty()) {
                throw new MarketClosedException();
            }

            JsonNode quote = dataNode.path("indicators").path("quote").get(0);
            JsonNode adjCloseArr = dataNode.path("indicators").path("adjclose");
            JsonNode adjClose = adjCloseArr.isArray() && !adjCloseArr.isEmpty()
                    ? adjCloseArr.get(0).path("adjclose")
                    : null;

            int index = findDateIndex(timestamps, targetDate);
            if (index < 0) {
                throw new MarketClosedException();
            }

            Double open = getDoubleAt(quote.path("open"), index);
            Double high = getDoubleAt(quote.path("high"), index);
            Double low = getDoubleAt(quote.path("low"), index);
            Double close = getDoubleAt(quote.path("close"), index);
            Double adjustedClose = adjClose != null ? getDoubleAt(adjClose, index) : close;
            Long volume = getLongAt(quote.path("volume"), index);

            if (open == null || high == null || low == null || close == null) {
                throw new MarketClosedException();
            }

            return StockHistoryResponse.builder()
                    .ticker(symbol)
                    .date(dateStr)
                    .open(open)
                    .high(high)
                    .low(low)
                    .close(close)
                    .adjustedClose(adjustedClose != null ? adjustedClose : close)
                    .volume(volume != null ? volume : 0L)
                    .build();
        } catch (MarketClosedException | ResourceNotFoundException e) {
            throw e;
        } catch (Exception e) {
            log.error("Failed to parse historical data for {} on {}", symbol, dateStr, e);
            throw new MarketClosedException();
        }
    }

    private int findDateIndex(JsonNode timestamps, LocalDate targetDate) {
        long targetEpoch = targetDate.atStartOfDay(ZoneOffset.UTC).toEpochSecond();
        for (int i = 0; i < timestamps.size(); i++) {
            long ts = timestamps.get(i).asLong();
            LocalDate candleDate = java.time.Instant.ofEpochSecond(ts)
                    .atZone(ZoneOffset.UTC)
                    .toLocalDate();
            if (candleDate.equals(targetDate)) {
                return i;
            }
        }
        if (timestamps.size() == 1) {
            return 0;
        }
        return -1;
    }

    private Double getDoubleAt(JsonNode array, int index) {
        if (array == null || !array.isArray() || index >= array.size()) {
            return null;
        }
        JsonNode val = array.get(index);
        if (val == null || val.isNull()) {
            return null;
        }
        return val.asDouble();
    }

    private Long getLongAt(JsonNode array, int index) {
        if (array == null || !array.isArray() || index >= array.size()) {
            return null;
        }
        JsonNode val = array.get(index);
        if (val == null || val.isNull()) {
            return null;
        }
        return val.asLong();
    }
}
