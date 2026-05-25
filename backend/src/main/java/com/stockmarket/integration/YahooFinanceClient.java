package com.stockmarket.integration;

import com.stockmarket.exception.RemoteApiException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Mono;
import reactor.util.retry.Retry;

import java.time.Duration;

@Component
@RequiredArgsConstructor
@Slf4j
public class YahooFinanceClient {

    private final WebClient yahooFinanceWebClient;

    @Value("${app.yahoo-finance.max-retries:3}")
    private int maxRetries;

    public Mono<String> fetchLiveQuote(String ticker) {
        String uri = "/v7/finance/quote?symbols=" + ticker;
        log.info("Fetching live quote for {}", ticker);
        return executeGet(uri);
    }

    public Mono<String> fetchChartHistory(String ticker, long period1, long period2) {
        String uri = String.format(
                "/v8/finance/chart/%s?period1=%d&period2=%d&interval=1d&includePrePost=false",
                ticker, period1, period2);
        log.info("Fetching history for {} ({} - {})", ticker, period1, period2);
        return executeGet(uri);
    }

    private Mono<String> executeGet(String uri) {
        return yahooFinanceWebClient.get()
                .uri(uri)
                .retrieve()
                .bodyToMono(String.class)
                .retryWhen(Retry.backoff(maxRetries, Duration.ofSeconds(1))
                        .filter(this::isRetryable)
                        .onRetryExhaustedThrow((spec, signal) ->
                                new RemoteApiException("Yahoo Finance API unavailable after retries")))
                .onErrorMap(this::mapToRemoteApiException);
    }

    private Throwable mapToRemoteApiException(Throwable error) {
        if (error instanceof RemoteApiException) {
            return error;
        }
        if (error instanceof WebClientResponseException.TooManyRequests) {
            return new RemoteApiException("Yahoo Finance rate limit exceeded");
        }
        if (error instanceof WebClientResponseException ex) {
            return new RemoteApiException("Yahoo Finance API error: " + ex.getStatusCode());
        }
        return new RemoteApiException("Failed to communicate with Yahoo Finance", error);
    }

    private boolean isRetryable(Throwable t) {
        if (t instanceof WebClientResponseException ex) {
            int status = ex.getStatusCode().value();
            return status >= 500 || status == 429;
        }
        return true;
    }
}
