package com.stockmarket.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class StockLiveResponse implements Serializable {

    private String ticker;
    private String companyName;
    private Double currentPrice;
    private Double open;
    private Double high;
    private Double low;
    private Double previousClose;
    private Long volume;
    private String currency;
    private String marketState;
    private Long timestamp;
}
