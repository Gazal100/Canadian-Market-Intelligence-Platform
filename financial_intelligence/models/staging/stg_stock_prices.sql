{{ config(materialized='view') }}

SELECT
    CAST(trade_date AS DATE)                              AS trade_date,
    ticker,
    sector,
    ROUND(open_price,  4)                                 AS open_price,
    ROUND(high_price,  4)                                 AS high_price,
    ROUND(low_price,   4)                                 AS low_price,
    ROUND(close_price, 4)                                 AS close_price,
    CAST(volume AS BIGINT)                                AS volume,

    -- Daily return: percentage price moved from open to close
    ROUND((close_price - open_price)
          / NULLIF(open_price, 0) * 100, 4)               AS daily_return_pct,

    -- Daily range: high minus low as a percentage (volatility proxy)
    ROUND((high_price - low_price)
          / NULLIF(low_price, 0) * 100, 4)                AS daily_range_pct,

    -- Absolute price change from the previous day
    ROUND(close_price - LAG(close_price)
          OVER (PARTITION BY ticker ORDER BY trade_date), 4) AS price_change

FROM {{ source('raw', 'stock_prices') }}
WHERE trade_date IS NOT NULL
  AND close_price > 0
ORDER BY ticker, trade_date
