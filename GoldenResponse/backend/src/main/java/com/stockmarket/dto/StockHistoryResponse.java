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
public class StockHistoryResponse implements Serializable {

    private String ticker;
    private String date;
    private Double open;
    private Double high;
    private Double low;
    private Double close;
    private Double adjustedClose;
    private Long volume;
}
