package com.stockmarket.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class MarketClosedResponse {

    private String message;

    public static MarketClosedResponse of() {
        return new MarketClosedResponse("Market Closed");
    }
}
