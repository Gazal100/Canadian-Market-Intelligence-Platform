# 🇨🇦 Canadian Market Intelligence Platform

> An institutional-grade financial analytics system with ML-powered anomaly detection, built entirely on free and open-source tools.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![dbt](https://img.shields.io/badge/dbt-1.7+-orange?logo=dbt)](https://getdbt.com)
[![DuckDB](https://img.shields.io/badge/DuckDB-0.10+-yellow)](https://duckdb.org)
[![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-gold?logo=powerbi)](https://powerbi.microsoft.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 Business Problem

Canadian equity markets generate thousands of trading signals daily. Traditional analysis struggles to flag unusual price and volume behaviour in real time — anomalies that often precede significant market moves.

This platform ingests 2 years of daily OHLCV data for 10 major TSX-listed equities, processes it through a modern data pipeline, applies dual-method machine learning to detect anomalies, and surfaces actionable insights through an interactive Power BI dashboard with automated alerting.

---

## 🏗️ Architecture

```
Yahoo Finance API
      │
      ▼
Python Ingestion (yfinance)
      │
      ▼
DuckDB  ──►  dbt Transformations  ──►  ML Anomaly Detection
                    │                        │
              Rolling Metrics          Isolation Forest
              MA-20 / MA-50              +  Z-Score
              Volatility 20D                │
              Volume Surge Ratio            ▼
                                   Composite Anomaly Score
                                           │
                                           ▼
                                   Power BI Dashboard
                                           │
                                           ▼
                                  Power Automate Alerts
```

---

## 🛠️ Tech Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| **Data Source** | Yahoo Finance API (yfinance) | Live TSX stock data — free, no account needed |
| **Storage** | DuckDB | Local analytical database — columnar, zero cost |
| **Transformation** | dbt Core + dbt-duckdb | SQL models, data quality tests, lineage |
| **ML Detection** | Python — scikit-learn | Isolation Forest + Z-Score anomaly detection |
| **Visualization** | Power BI Desktop + Service | 4-page interactive dashboard |
| **Alerting** | Power Automate | Automated email alerts on anomaly spikes |
| **Version Control** | GitHub | Full pipeline version-controlled |

---

## 📈 Stocks Covered

| Ticker | Company | Sector |
|--------|---------|--------|
| RY.TO | Royal Bank of Canada | Financials |
| TD.TO | TD Bank | Financials |
| BMO.TO | Bank of Montreal | Financials |
| SU.TO | Suncor Energy | Energy |
| CNQ.TO | Canadian Natural Resources | Energy |
| ENB.TO | Enbridge | Energy |
| SHOP.TO | Shopify | Technology |
| CP.TO | Canadian Pacific Railway | Industrials |
| BCE.TO | BCE Inc | Telecom |
| ATD.TO | Alimentation Couche-Tard | Consumer |

---

## 🤖 Anomaly Detection Methodology

Two independent methods are applied to each ticker. A trading day is flagged as anomalous if **either** method catches it — reducing false negatives.

### Method 1 — Z-Score (Statistical)
- Standardizes 4 features: daily return %, volume surge ratio, 20-day volatility, daily price range %
- Flags any day where **one or more features** exceeds 2.5 standard deviations from the mean

### Method 2 — Isolation Forest (Machine Learning)
- Unsupervised ML with no distributional assumptions
- Builds random partition trees and measures isolation speed
- Anomalies get isolated faster — `contamination=0.05` (expects ~5% anomaly rate)

### Composite Anomaly Score
- Raw Isolation Forest scores normalized to **0–100** (higher = more anomalous)
- Severity classification: **Low** (0–40) | **Medium** (40–70) | **High** (70–100)

---

## 📊 Dashboard Pages

### Page 1 — Market Overview
KPI cards, sector price trends, anomaly heat map by ticker and month, anomalies by sector donut chart.

### Page 2 — Anomaly Intelligence
Scatter plot (return % vs volume surge, colored by anomaly), flagged event log table, anomalies by stock bar chart, volume surge alert card.

### Page 3 — Stock Deep Dive
Close price with MA-20 and MA-50 overlay, volume bars (red on surge days), anomaly score gauge, signal cards.

### Page 4 — Sector Risk Dashboard
Sector risk treemap, volatility ranking by stock, anomaly trend by sector over time, sector summary table.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Power BI Desktop (free from microsoft.com/power-bi)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/canadian-market-intelligence.git
cd canadian-market-intelligence

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Pipeline

```bash
# Step 1 — Ingest TSX stock data into DuckDB
python ingestion/fetch_stocks.py

# Step 2 — Run dbt transformations
cd financial_intelligence
dbt run
dbt test
cd ..

# Step 3 — Run ML anomaly detection and export CSVs
python ml/anomaly_detection.py
```

### Open Power BI
1. Open Power BI Desktop
2. Get Data → Text/CSV → load both files from `outputs/`
3. Build data model relationships as described in `/docs/data_model.md`

---

## 📁 Project Structure

```
canadian-market-intelligence/
│
├── ingestion/
│   └── fetch_stocks.py          # Yahoo Finance → DuckDB ingestion
│
├── ml/
│   └── anomaly_detection.py     # Isolation Forest + Z-Score detection
│
├── financial_intelligence/      # dbt project
│   ├── models/
│   │   ├── staging/
│   │   │   └── stg_stock_prices.sql
│   │   └── marts/
│   │       ├── fct_stock_metrics.sql
│   │       └── schema.yml
│   ├── dbt_project.yml
│   └── profiles.yml
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 📦 Requirements

```
yfinance>=0.2.40
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
duckdb>=0.10.0
dbt-core>=1.7.0
dbt-duckdb>=1.7.0
python-dotenv>=1.0.0
```

---

## 📊 Results

- **5,020 rows** of daily OHLCV data across 10 TSX equities over 2 years
- **~235 anomalies detected** (~4.8% anomaly rate)
- **~62 high-severity** anomaly events flagged
- **4 dashboard pages** with 12 DAX measures and Row-Level Security

---

## 🧠 Skills Demonstrated

`Python` `DuckDB` `dbt` `Machine Learning` `Isolation Forest` `scikit-learn` `Power BI` `DAX` `Power Query` `Power Automate` `Data Modeling` `ETL Pipeline` `Row-Level Security` `Time Intelligence` `SQL Window Functions` `Data Quality Testing`

---

## 📬 Contact

**Gazal** — Data Analyst & BI Developer  
📧 gazalgarg8065@gmail.com  
🔗 [LinkedIn](https://www.linkedin.com/in/gazal-garg-15aba8215/)  
💼 [Upwork Profile](https://www.upwork.com/freelancers/~013739ff7d81df48d1?mp_source=share)

---

*Built with Python, DuckDB, dbt, and Power BI — 100% free and open source.*
