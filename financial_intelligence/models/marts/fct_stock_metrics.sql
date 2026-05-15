{{ config(materialized='table') }}

WITH base AS (
    SELECT * FROM {{ ref('stg_stock_prices') }}
),

rolling AS (
    SELECT
        *,

        -- 20-day moving average (short-term trend)
        ROUND(AVG(close_price) OVER (
            PARTITION BY ticker ORDER BY trade_date
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ), 4)                                             AS ma_20,

        -- 50-day moving average (long-term trend)
        ROUND(AVG(close_price) OVER (
            PARTITION BY ticker ORDER BY trade_date
            ROWS BETWEEN 49 PRECEDING AND CURRENT ROW
        ), 4)                                             AS ma_50,

        -- 20-day rolling volatility (std dev of daily returns)
        ROUND(STDDEV(daily_return_pct) OVER (
            PARTITION BY ticker ORDER BY trade_date
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ), 4)                                             AS volatility_20d,

        -- 20-day average volume (to detect surges)
        ROUND(AVG(volume) OVER (
            PARTITION BY ticker ORDER BY trade_date
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ), 0)                                             AS avg_volume_20d

    FROM base
),

final AS (
    SELECT
        *,

        -- Price relative to its 20-day MA (1.0 = right on the MA)
        ROUND(close_price / NULLIF(ma_20, 0), 4)          AS price_to_ma20_ratio,

        -- Today's volume vs average volume (2.0 = double the usual)
        ROUND(volume / NULLIF(avg_volume_20d, 0), 4)      AS volume_surge_ratio,

        -- MA crossover trend signal
        CASE
            WHEN close_price > ma_20 AND ma_20 > ma_50 THEN 'Bullish'
            WHEN close_price < ma_20 AND ma_20 < ma_50 THEN 'Bearish'
            ELSE 'Neutral'
        END                                                AS trend_signal,

        -- Overbought or oversold vs 20-day MA
        CASE
            WHEN close_price / NULLIF(ma_20, 0) > 1.05 THEN 'Overbought'
            WHEN close_price / NULLIF(ma_20, 0) < 0.95 THEN 'Oversold'
            ELSE 'Normal'
        END                                                AS price_signal

    FROM rolling
)

 SELECT * FROM final
