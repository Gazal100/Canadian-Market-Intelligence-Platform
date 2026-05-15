import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import duckdb
import os

DB_PATH = 'financial_db.duckdb'

def load_data():
    conn = duckdb.connect(DB_PATH)
    df = conn.execute('''
        SELECT
            trade_date, ticker, sector, close_price,
            daily_return_pct, daily_range_pct, volume,
            volume_surge_ratio, volatility_20d,
            ma_20, price_to_ma20_ratio, trend_signal, price_signal
        FROM marts.fct_stock_metrics
        WHERE volatility_20d      IS NOT NULL
          AND volume_surge_ratio  IS NOT NULL
        ORDER BY ticker, trade_date
    ''').df()
    conn.close()
    print(f'Loaded {len(df)} rows from fct_stock_metrics')
    return df

def detect_for_ticker(ticker_df):
    FEATURES = ['daily_return_pct','volume_surge_ratio','volatility_20d','daily_range_pct']
    feature_df = ticker_df[FEATURES].dropna()

    if len(feature_df) < 30:
        return None   # not enough history

    # ── Method 1: Z-Score ────────────────────────────────────────────
    scaler  = StandardScaler()
    scaled  = scaler.fit_transform(feature_df)
    z_any   = (np.abs(scaled) > 2.5).any(axis=1)
    z_flag  = z_any.astype(int)

    # ── Method 2: Isolation Forest ───────────────────────────────────
    iso = IsolationForest(contamination=0.05, n_estimators=100, random_state=42)
    labels    = iso.fit_predict(feature_df)   # -1=anomaly, 1=normal
    iso_flag  = (labels == -1).astype(int)

    # Normalize raw scores to 0-100 (higher = more anomalous)
    raw   = iso.score_samples(feature_df)
    lo, hi = raw.min(), raw.max()
    score = 100 * (1 - (raw - lo) / (hi - lo + 1e-10))

    # ── Combine ───────────────────────────────────────────────────────
    out = ticker_df.loc[feature_df.index].copy()
    out['z_anomaly']        = z_flag
    out['iso_anomaly']      = iso_flag
    out['anomaly_score']    = np.round(score, 2)
    out['is_anomaly']       = ((z_flag + iso_flag) >= 1).astype(int)
    out['anomaly_severity'] = pd.cut(
        score, bins=[0,40,70,100],
        labels=['Low','Medium','High'], include_lowest=True
    ).astype(str)
    return out

def run():
    df = load_data()
    results = []
    for ticker in sorted(df['ticker'].unique()):
        print(f'  Processing {ticker}...')
        r = detect_for_ticker(df[df['ticker']==ticker].copy())
        if r is not None:
            results.append(r)

    final = pd.concat(results, ignore_index=True)

    total = len(final)
    n_anom = final['is_anomaly'].sum()
    n_high = (final['anomaly_severity']=='High').sum()
    print(f'')
    print(f'Total rows:       {total}')
    print(f'Anomalies found:  {n_anom}  ({n_anom/total*100:.1f}%)')
    print(f'High severity:    {n_high}')

    # Write results back to DuckDB
    conn = duckdb.connect(DB_PATH)
    conn.execute('CREATE SCHEMA IF NOT EXISTS marts')
    conn.execute('DROP TABLE IF EXISTS marts.fct_anomaly_signals')
    conn.execute('CREATE TABLE marts.fct_anomaly_signals AS SELECT * FROM final')
    n = conn.execute('SELECT COUNT(*) FROM marts.fct_anomaly_signals').fetchone()[0]
    print(f'Written {n} rows to marts.fct_anomaly_signals')
    conn.close()

    # Export CSVs for Power BI
    os.makedirs('outputs', exist_ok=True)
    final.to_csv('outputs/anomaly_signals.csv', index=False)

    conn2 = duckdb.connect(DB_PATH)
    conn2.execute("COPY marts.fct_stock_metrics TO 'outputs/stock_metrics.csv' (HEADER, DELIMITER ',')")
    conn2.close()

    print('CSVs written to outputs/ — ready for Power BI')
    print('Done!')

if __name__ == '__main__':
    run()
