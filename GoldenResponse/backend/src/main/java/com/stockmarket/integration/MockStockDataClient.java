package com.stockmarket.integration;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import reactor.core.publisher.Mono;

import java.util.HashMap;
import java.util.Map;
import java.util.Random;

@Component
@Slf4j
public class MockStockDataClient {

    private final ObjectMapper objectMapper = new ObjectMapper();
    private final Random random = new Random();

    private static final Map<String, Double> BASE_PRICES = new HashMap<>();
    
    static {
        BASE_PRICES.put("AAPL", 175.50);
        BASE_PRICES.put("GOOGL", 140.25);
        BASE_PRICES.put("MSFT", 378.90);
        BASE_PRICES.put("AMZN", 178.35);
        BASE_PRICES.put("TSLA", 245.80);
        BASE_PRICES.put("META", 505.20);
        BASE_PRICES.put("NVDA", 890.15);
        BASE_PRICES.put("TCS.NS", 3800.75);
        BASE_PRICES.put("RELIANCE.NS", 2980.50);
        BASE_PRICES.put("INFY.NS", 1450.30);
    }

    public Mono<String> fetchLiveQuote(String ticker) {
        log.info("Fetching mock live quote for {}", ticker);
        
        double basePrice = BASE_PRICES.getOrDefault(ticker.toUpperCase(), 100.0);
        double currentPrice = basePrice + (random.nextDouble() - 0.5) * (basePrice * 0.02);
        double change = currentPrice - basePrice;
        double changePercent = (change / basePrice) * 100;
        
        ObjectNode response = objectMapper.createObjectNode();
        ObjectNode quoteResponse = response.putObject("quoteResponse");
        quoteResponse.put("result", 1);
        
        ObjectNode result = quoteResponse.putArray("result").addObject();
        result.put("symbol", ticker.toUpperCase());
        result.put("regularMarketPrice", currentPrice);
        result.put("regularMarketOpen", basePrice + (random.nextDouble() - 0.5) * (basePrice * 0.01));
        result.put("regularMarketDayHigh", currentPrice + (random.nextDouble() * (basePrice * 0.01)));
        result.put("regularMarketDayLow", currentPrice - (random.nextDouble() * (basePrice * 0.01)));
        result.put("regularMarketPreviousClose", basePrice);
        result.put("regularMarketChange", change);
        result.put("regularMarketChangePercent", changePercent);
        result.put("regularMarketVolume", 1000000L + random.nextInt(500000)); // Mock volume
        result.put("marketState", "REGULAR");
        result.put("currency", ticker.endsWith(".NS") ? "INR" : "USD");
        result.put("regularMarketTime", System.currentTimeMillis() / 1000L);
        
        try {
            return Mono.just(objectMapper.writeValueAsString(response));
        } catch (Exception e) {
            return Mono.error(new RuntimeException("Failed to generate mock data", e));
        }
    }

    public Mono<String> fetchChartHistory(String ticker, long period1, long period2) {
        log.info("Fetching mock history for ticker: {}, period1: {}, period2: {}", ticker, period1, period2);
        
        double basePrice = BASE_PRICES.getOrDefault(ticker.toUpperCase(), 100.0);
        
        // Build JSON structure matching Yahoo Finance format exactly
        StringBuilder json = new StringBuilder();
        json.append("{\"chart\":{\"result\":[");
        json.append("{\"timestamp\":[").append(period1).append("],");
        json.append("\"meta\":{\"currency\":\"").append(ticker.endsWith(".NS") ? "INR" : "USD").append("\",\"symbol\":\"").append(ticker.toUpperCase()).append("\"},");
        json.append("\"indicators\":{");
        json.append("\"quote\":[{");
        json.append("\"open\":[").append(basePrice * 0.99).append("],");
        json.append("\"high\":[").append(basePrice * 1.01).append("],");
        json.append("\"low\":[").append(basePrice * 0.98).append("],");
        json.append("\"close\":[").append(basePrice).append("],");
        json.append("\"volume\":[1000000]");
        json.append("}],");
        json.append("\"adjclose\":[{\"adjclose\":[").append(basePrice).append("]}]");
        json.append("}");
        json.append("}]}}");
        
        String jsonString = json.toString();
        log.info("Generated mock history JSON: {}", jsonString);
        return Mono.just(jsonString);
    }
}
