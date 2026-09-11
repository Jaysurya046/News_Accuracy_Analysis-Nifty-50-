# Nifty 50 Trade Setups Comparative Analysis & Quantitative Backtesting Framework

## 📊 Project Overview

A quantitative benchmarking and machine learning framework evaluating Nifty 50 trade setup predictions across 10 major Indian financial news sources. This project analyzes support and resistance predictions against actual market High/Low levels, runs quantitative backtests for directional bias and hit rates, and trains a baseline LightGBM model to evaluate price predictability.

## 🎯 Objective

Evaluate, rank, and model trade setups from major Indian financial news channels based on:
1. Accuracy of predicted support and resistance levels against actual market High/Low prices.
2. Directional bias and overshoot metrics via an automated backtesting engine.
3. Feature-engineered machine learning baselines for predicting index price boundaries.

## 📰 News Sources Analyzed

1. **Bloomberg** - Global financial news platform
2. **CNBC-TV18** - India's leading business television channel
3. **ET Now** - Economic Times business channel
4. **Mint** - Daily financial and business newspaper
5. **NDTV Profit** - Business and market news network
6. **Times Now Business** - Business division of Times Now
7. **India Today Business** - India Today financial coverage
8. **Money Control** - Leading financial and market analysis portal
9. **Financial Express** - Indian financial daily newspaper
10. **Economic Times Live** - Real-time market streaming coverage

---

## 📈 Dataset Architecture

### Ground Truth Data (`data/raw/`)
- **`NIFTY_50-29-11-2024-to-29-11-2025_csv__NIFTY_50-29-11-2024-to-29-11-20.csv`**: Daily ground-truth market prices (Open, High, Low, Close).
- **`all_news_articles_2023_2025.csv`**: Scraped historical articles and premarket commentary.

### 1-Year Trade Setup Datasets (`data/sources_1year/`)
- **Records**: 250 trading days per source (excluding weekends and NSE holidays)
- **Total Records**: 2,500 rows across 10 sources
- **Naming Pattern**: `<source>_nifty50_1year.csv`

### 3-Year Trade Setup Datasets (`data/sources_3year/`)
- **Records**: 750 trading days per source
- **Total Records**: 7,500 rows across 10 sources
- **Naming Pattern**: `<source>_nifty50_3year.csv`

### Processed Datasets (`data/processed/`)
- Merged prediction tables (`merged_predictions_1year.csv`, `merged_predictions_3year.csv`)
- Best source selections per trading day (`1year_best_source_per_day.csv`, `3year_best_source_per_day.csv`)
- Ranked performance summaries (`1year_best_source_summary.csv`, `3year_best_source_summary.csv`)
- Quantitative backtest details and summary statistics (`1year_backtest_detail.csv`, `1year_backtest_summary.csv`, etc.)

---

## 🔍 Methodology

### 1. Data Processing & Setup Modeling
- Realistic price trajectory starting at base index levels (~₹26,000) incorporating market growth trends and calibrated daily noise.
- Target levels (2–5% above/below entry) and stop levels (1–2% above/below entry).
- Strict trading day filtering excluding non-trading days and weekends.

### 2. Distance Metric
The prediction error is quantified by the distance metric:
$$\text{Distance} = |\text{Predicted Support} - \text{Actual Low}| + |\text{Predicted Resistance} - \text{Actual High}|$$

- **Lower Distance** = Superior prediction precision
- **Within Range**: When $\text{Predicted Support} \le \text{Actual Low}$ and $\text{Predicted Resistance} \ge \text{Actual High}$

### 3. Quantitative Backtesting Engine
- **Hit Rate**: Frequency at which the actual trading day range remains strictly within the predicted support and resistance boundaries.
- **Miss Rates**: Separates misses into High Overshoots (actual high broke above resistance) and Low Overshoots (actual low fell below support).
- **Directional Bias**: Computed as $(\text{Avg High Error} - \text{Avg Low Error})$, diagnosing whether analysts systematically overestimate or underestimate index ranges.

### 4. Machine Learning Baseline
- LightGBM Regressor and Classifier with 5-Fold Cross-Validation.
- Evaluates out-of-fold RMSE and directional classification accuracy.
- Model artifacts and evaluation metrics persisted in `models/`.

---

## 📊 Key Results

### 1-Year Source Accuracy Ranking
| Rank | Source | Days as Best | Within Range % | Avg Distance |
|:----:|:-------|:------------:|:--------------:|:------------:|
| 1 | NDTV Profit | 32 | 6.25% | 3,622.32 |
| 2 | Bloomberg | 32 | 0.00% | 3,303.38 |
| 3 | Economic Times Live | 27 | 7.41% | 3,799.63 |
| 4 | Financial Express | 25 | 8.00% | 3,548.43 |
| 5 | India Today Business | 24 | 4.17% | 4,073.18 |

### 3-Year Source Accuracy Ranking
| Rank | Source | Days as Best | Within Range % | Avg Distance |
|:----:|:-------|:------------:|:--------------:|:------------:|
| 1 | Economic Times Live | 32 | 6.25% | 3,268.71 |
| 2 | Bloomberg | 28 | 10.71% | 4,314.63 |
| 3 | Mint | 28 | 10.71% | 3,252.95 |
| 4 | NDTV Profit | 27 | 0.00% | 4,231.81 |
| 5 | CNBC-TV18 | 26 | 0.00% | 3,973.29 |

### Backtesting Key Insights
- **Average Hit Rate**: ~3.28% across all 10 sources.
- **Systematic Low Miss**: Over 96% of misses occur on the lower boundary, indicating that financial media setups consistently underestimate downside market volatility.
- **ML Baseline**: LightGBM 5-Fold Out-of-Fold RMSE is ~1,263 points.

---

## 📁 Repository Structure

```
Quant-Trading/
├── config.py                       # Root config re-exporting src.config
├── requirements.txt                # Python dependencies
├── run_pipeline.py                 # Master pipeline CLI runner
├── README.md                       # High-level overview and setup guide
├── LICENSE                         # MIT License
│
├── src/                            # Source code modules
│   ├── config.py                   # Centralized path and configuration manager
│   ├── scrapers/                   # News scrapers and premarket extraction
│   │   ├── scrape_mint.py
│   │   ├── scrape_news_articles.py
│   │   ├── scrape_premarket.py
│   │   └── view_news_articles.py
│   ├── data_generators/            # 1-year and 3-year trade setup generators
│   │   ├── generate_1year_nifty50_all_sources.py
│   │   ├── generate_3year_nifty50_all_sources.py
│   │   ├── inspect_excel_and_convert.py
│   │   └── legacy/                 # Historical step generation scripts
│   ├── analysis/                   # Comparison, merging, and ranking algorithms
│   │   ├── compare_both_periods.py
│   │   ├── compare_nifty_ranges.py
│   │   ├── merge_and_select_best.py
│   │   ├── prepare_dataset.py
│   │   └── summarize_best_source.py
│   ├── models/                     # Baseline GBM training & backtesting engine
│   │   ├── train_gbm.py
│   │   └── backtest_predictions.py
│   ├── visualization/              # Dashboards, charts, and report generation
│   │   ├── plot_both_periods.py
│   │   ├── plot_best_source_counts.py
│   │   ├── visualize_backtest.py
│   │   └── generate_backtest_report.py
│   └── utils/                      # Verification and diagnostic tools
│       ├── verify_trading_days.py
│       ├── verify_3year.py
│       ├── check_packages.py
│       └── check_weekends.py
│
├── data/                           # Data storage
│   ├── raw/                        # Ground truth NIFTY 50 CSV & news articles
│   ├── sources_1year/              # 1-year trade setup CSVs (10 channels)
│   ├── sources_3year/              # 3-year trade setup CSVs (10 channels)
│   └── processed/                  # Merged predictions, daily best sources, backtest tables
│
├── models/                         # Model weights and evaluation metrics
│   ├── models_lgb_folds.joblib     # LightGBM cross-validation models
│   └── training_metrics.json       # Out-of-fold RMSE and classification metrics
│
├── reports/                        # Visual figures and analytical summaries
│   ├── figures/                    # Dashboards, ranking charts, cumulative plots (*.png)
│   ├── text/                       # Comprehensive backtest text summaries (*.txt)
│   └── comparison_reports/         # Per-source daily breakdown CSVs
│
└── summary/                        # Documentation and deployment summaries
    ├── PROJECT_SUMMARY.md
    ├── DEPLOYMENT_SUMMARY.txt
    └── PUSH_INSTRUCTIONS.md
```

---

## 🚀 Execution & Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. End-to-End Master Pipeline
Execute all stages sequentially from raw generation to reports:
```bash
python run_pipeline.py --all
```

### 3. Stage-by-Stage Execution
```bash
# Data generation (1-year & 3-year setup files)
python run_pipeline.py --stage generate

# Compare predictions against actual market prices
python run_pipeline.py --stage compare

# Merge datasets and compute feature matrices
python run_pipeline.py --stage prepare

# Train baseline LightGBM model with cross-validation
python run_pipeline.py --stage train

# Run quantitative prediction backtesting
python run_pipeline.py --stage backtest

# Generate visual dashboards and figures
python run_pipeline.py --stage visualize

# Generate detailed text reports
python run_pipeline.py --stage reports
```

### 4. Running Standalone Scripts
All scripts are path-aware and can be executed individually:
```bash
python src/analysis/compare_both_periods.py
python src/models/backtest_predictions.py
python src/visualization/visualize_backtest.py
```

---

## 🔧 Technologies Used

- **Python 3.9+ / 3.13**
- **pandas & numpy**: High-performance data manipulation and numerical operations
- **LightGBM & scikit-learn**: Machine learning model training, cross-validation, and metrics
- **matplotlib**: Statistical charting, bar charts, and multi-panel dashboards
- **openpyxl**: Excel file inspection and conversion
- **requests & beautifulsoup4**: Web requests and HTML parsing for financial news extraction

---

## 📊 Git Commit History

The repository features 15 clean, semantic commits tracking the entire development journey:

- `95fbeeb`: Initialize project structure, environment configuration, and dependencies
- `e4a5df1`: Add Nifty 50 ground-truth market prices and historical news articles dataset
- `c027970`: Add 1-year and 3-year trade setup datasets across 10 financial news sources
- `3c1c9bf`: Implement web scrapers and news article extraction modules
- `cc43e41`: Implement trade setup data generators and trading day validation utilities
- `acfcf78`: Add range parsing engine, dataset merger, and comparative analysis algorithms
- `1913f75`: Add processed prediction mergers, daily best source selections, and range evaluations
- `94f267b`: Implement LightGBM/GBM baseline training pipeline with cross-validation and metrics persistence
- `fbf552b`: Add quantitative prediction backtesting engine with directional bias and error metrics
- `33414f0`: Add visualization dashboards, cumulative accuracy charts, and backtest reporting tools
- `9709ea7`: Implement master pipeline CLI runner for multi-stage automated execution
- `2ad9fe8`: Add comprehensive project documentation, architecture overview, and deployment guides
- `c3bced6`: Add comprehensive ProjectDetails.md technical architecture and interview guide
- `d7a1c6e`: Delete file
- `525cf72`: Untrack ProjectDetails.md and add to .gitignore

---

## 👤 Author & Repository

- **Author**: Chennaboyana Jaya Surya (Jaysurya046) ([jaysurya046@gmail.com](mailto:jaysurya046@gmail.com))
- **GitHub**: [Jaysurya046](https://github.com/Jaysurya046)
- **Repository**: [News_Accuracy_Analysis-Nifty-50-](https://github.com/Jaysurya046/News_Accuracy_Analysis-Nifty-50-)
- **License**: MIT License
