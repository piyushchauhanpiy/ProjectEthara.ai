package com.stockmarket.controller;

import com.stockmarket.dto.ApiResponse;
import com.stockmarket.dto.StockHistoryResponse;
import com.stockmarket.dto.StockLiveResponse;
import com.stockmarket.service.StockService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/stocks")
@RequiredArgsConstructor
@Validated
@Slf4j
@Tag(name = "Stocks", description = "Live and historical stock data APIs")
public class StockController {

    private final StockService stockService;

    @GetMapping("/live/{ticker}")
    @Operation(summary = "Get live stock quote by ticker")
    public ResponseEntity<ApiResponse<StockLiveResponse>> getLiveStock(
            @PathVariable
            @NotBlank(message = "Ticker is required")
            @Pattern(regexp = "^[A-Za-z0-9=.-]{1,12}$", message = "Invalid ticker format")
            String ticker) {
        log.info("Received live stock request for ticker: {}", ticker);
        StockLiveResponse data = stockService.getLiveStockData(ticker);
        return ResponseEntity.ok(ApiResponse.ok(data));
    }

    @GetMapping("/history")
    @Operation(summary = "Get historical OHLC data for a ticker on a specific date")
    public ResponseEntity<ApiResponse<StockHistoryResponse>> getHistoricalStock(
            @RequestParam
            @NotBlank(message = "Ticker is required")
            @Pattern(regexp = "^[A-Za-z0-9=.-]{1,12}$", message = "Invalid ticker format")
            String ticker,
            @RequestParam
            @NotBlank(message = "Date is required")
            @Pattern(regexp = "^\\d{4}-\\d{2}-\\d{2}$", message = "Date must be in YYYY-MM-DD format")
            String date) {
        log.info("Received historical stock request for ticker: {}, date: {}", ticker, date);
        StockHistoryResponse data = stockService.getHistoricalStockData(ticker, date);
        return ResponseEntity.ok(ApiResponse.ok(data));
    }
}
