package com.stockmarket.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.stockmarket.dto.StockHistoryResponse;
import com.stockmarket.dto.StockLiveResponse;
import com.stockmarket.exception.MarketClosedException;
import com.stockmarket.exception.ResourceNotFoundException;
import com.stockmarket.integration.YahooFinanceClient;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Spy;
import org.mockito.junit.jupiter.MockitoExtension;
import reactor.core.publisher.Mono;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class StockServiceTest {

    @Mock
    private YahooFinanceClient yahooFinanceClient;

    @Spy
    private ObjectMapper objectMapper = new ObjectMapper();

    @InjectMocks
    private StockService stockService;

    private String validLiveJson;
    private String emptyLiveJson;
    private String validHistoryJson;
    private String emptyHistoryJson;

    @BeforeEach
    void setUp() {
        validLiveJson = """
                {"quoteResponse":{"result":[{"symbol":"AAPL","longName":"Apple Inc.",
                "regularMarketPrice":180.5,"regularMarketOpen":179.0,
                "regularMarketDayHigh":181.0,"regularMarketDayLow":178.5,
                "regularMarketPreviousClose":179.5,"regularMarketVolume":50000000,
                "currency":"USD","marketState":"REGULAR","regularMarketTime":1715635200}]}}
                """.replace("\n", "");

        emptyLiveJson = "{\"quoteResponse\":{\"result\":[]}}";

        validHistoryJson = """
                {"chart":{"result":[{"timestamp":[1715299200],
                "indicators":{"quote":[{"open":[182.2],"high":[185.33],"low":[181.5],
                "close":[184.1],"volume":[8292012]}],
                "adjclose":[{"adjclose":[184.1]}]}}]}}
                """.replace("\n", "");

        emptyHistoryJson = "{\"chart\":{\"result\":[]}}";
    }

    @Test
    void getLiveStockData_success() {
        when(yahooFinanceClient.fetchLiveQuote("AAPL")).thenReturn(Mono.just(validLiveJson));

        StockLiveResponse response = stockService.getLiveStockData("aapl");

        assertNotNull(response);
        assertEquals("AAPL", response.getTicker());
        assertEquals("Apple Inc.", response.getCompanyName());
        assertEquals(180.5, response.getCurrentPrice());
    }

    @Test
    void getLiveStockData_tickerNotFound() {
        when(yahooFinanceClient.fetchLiveQuote("INVALID")).thenReturn(Mono.just(emptyLiveJson));

        assertThrows(ResourceNotFoundException.class,
                () -> stockService.getLiveStockData("INVALID"));
    }

    @Test
    void getHistoricalStockData_marketClosed() {
        when(yahooFinanceClient.fetchChartHistory(eq("AAPL"), anyLong(), anyLong()))
                .thenReturn(Mono.just(emptyHistoryJson));

        assertThrows(MarketClosedException.class,
                () -> stockService.getHistoricalStockData("AAPL", "2024-05-11"));
    }

    @Test
    void getHistoricalStockData_futureDateRejected() {
        assertThrows(com.stockmarket.exception.FutureDateException.class,
                () -> stockService.getHistoricalStockData("AAPL", "2099-01-01"));
    }
}
