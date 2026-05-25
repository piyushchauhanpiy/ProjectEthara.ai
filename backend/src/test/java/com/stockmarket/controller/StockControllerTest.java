package com.stockmarket.controller;

import com.stockmarket.dto.StockLiveResponse;
import com.stockmarket.service.StockService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(StockController.class)
class StockControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private StockService stockService;

    @Test
    void getLiveStock_returnsWrappedResponse() throws Exception {
        when(stockService.getLiveStockData("AAPL")).thenReturn(
                StockLiveResponse.builder()
                        .ticker("AAPL")
                        .companyName("Apple Inc.")
                        .currentPrice(180.0)
                        .open(179.0)
                        .high(181.0)
                        .low(178.0)
                        .previousClose(179.0)
                        .volume(1000L)
                        .currency("USD")
                        .marketState("REGULAR")
                        .timestamp(1715635200L)
                        .build());

        mockMvc.perform(get("/api/stocks/live/AAPL"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.ticker").value("AAPL"));
    }

    @Test
    void getLiveStock_invalidTickerFormat() throws Exception {
        mockMvc.perform(get("/api/stocks/live/INVALID!!!"))
                .andExpect(status().isBadRequest());
    }
}
