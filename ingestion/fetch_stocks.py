import yfinance as yf
import pandas as pd
import duckdb

# ── 10 TSX companies across 5 sectors ────────────────────────────────
TICKERS = {
    'RY.TO':   'Financials',    # Royal Bank of Canada
    'TD.TO':   'Financials',    # TD Bank
    'BMO.TO':  'Financials',    # Bank of Montreal
    'SU.TO':   'Energy',        # Suncor Energy
    'CNQ.TO':  'Energy',        # Canadian Natural Resources
    'ENB.TO':  'Energy',        # Enbridge
    'SHOP.TO': 'Technology',    # Shopify
    'CP.TO':   'Industrials',   # Canadian Pacific Railway
    'BCE.TO':  'Telecom',       # BCE Inc
    'ATD.TO':  'Consumer',      # Alimentation Couche-Tard
}

def fetch_all_stocks(period='2y', interval='1d'):
    all_frames = []
    for ticker, sector in TICKERS.items():
        print(f'  Fetching {ticker}...')
        try:
            stock = yf.Ticker(ticker)
            df    = stock.history(period=period, interval=interval)
            if df.empty:
                print(f'  WARNING: No data for {ticker}')
                continue
            df['ticker'] = ticker
            df['sector'] = sector
            df.reset_index(inplace=True)
            df.rename(columns={
                'Date':         'trade_date',
                'Open':         'open_price',
                'High':         'high_price',
                'Low':          'low_price',
                'Close':        'close_price',
                'Volume':       'volume',
                'Dividends':    'dividends',
                'Stock Splits': 'stock_splits'
            }, inplace=True)
            df['trade_date'] = pd.to_datetime(df['trade_date']).dt.date
            all_frames.append(df[[
                'trade_date','open_price','high_price','low_price',
                'close_price','volume','dividends','stock_splits',
                'ticker','sector'
            ]])
        except Exception as e:
            print(f'  ERROR on {ticker}: {e}')
    return pd.concat(all_frames, ignore_index=True)

def load_to_duckdb(df, db_path='financial_db.duckdb'):
    conn = duckdb.connect(db_path)
    conn.execute('CREATE SCHEMA IF NOT EXISTS raw')
    # Drop and recreate — safe to re-run
    conn.execute('DROP TABLE IF EXISTS raw.stock_prices')
    conn.execute('CREATE TABLE raw.stock_prices AS SELECT * FROM df')
    n = conn.execute('SELECT COUNT(*) FROM raw.stock_prices').fetchone()[0]
    print(f'  Loaded {n} rows into DuckDB raw.stock_prices')
    conn.close()

if __name__ == '__main__':
    print('Fetching TSX stock data...')
    df = fetch_all_stocks()
    print(f'Total rows fetched: {len(df)}')
    print('Writing to DuckDB...')
    load_to_duckdb(df)
    print('Done! financial_db.duckdb is ready.')
