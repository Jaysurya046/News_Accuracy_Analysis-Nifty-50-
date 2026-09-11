# Financial Markets: News Accuracy Analysis (Nifty 50)

> Quantitative benchmark and backtesting framework evaluating Nifty 50 trade setup predictions and support/resistance accuracy across 10 major Indian financial news sources.

---

## 📰 Analyzed News Sources
1. **Bloomberg**
2. **CNBC-TV18**
3. **ET Now**
4. **Mint**
5. **NDTV Profit**
6. **Times Now Business**
7. **India Today Business**
8. **Money Control**
9. **Financial Express**
10. **Economic Times Live**

---

## 📁 Repository Structure

```
Quant-Trading/
├── config.py                       # Root config re-exporting src.config
├── requirements.txt                # Python dependencies
├── run_pipeline.py                 # Master pipeline CLI runner
│
├── src/                            # Source code modules
│   ├── config.py                   # Central path & configuration manager
│   ├── scrapers/                   # News scraping & premarket scripts
│   ├── data_generators/            # 1-year and 3-year setup generators
│   │   └── legacy/                 # Historical step generators
│   ├── analysis/                   # Comparison, merging, and ranking algorithms
│   ├── models/                     # Baseline GBM training & backtesting engine
│   ├── visualization/              # Dashboard, chart, and report generators
│   └── utils/                      # Verification and diagnostic utilities
│
├── data/                           # Data storage
│   ├── raw/                        # Ground truth NIFTY 50 CSV & raw news articles
│   ├── sources_1year/              # 1-year trade setup CSVs (10 channels)
│   ├── sources_3year/              # 3-year trade setup CSVs (10 channels)
│   └── processed/                  # Merged predictions, daily best sources, backtest tables
│
├── models/                         # Model weights and evaluation metrics
│   ├── models_lgb_folds.joblib
│   └── training_metrics.json
│
├── reports/                        # Visual figures and analytical summaries
│   ├── figures/                    # Backtest dashboards and comparison plots (*.png)
│   ├── text/                       # Comprehensive text reports (*.txt)
│   └── comparison_reports/         # Per-source daily breakdown CSVs
│
└── summary/                        # Project summaries and deployment guides
    ├── PROJECT_SUMMARY.md
    ├── DEPLOYMENT_SUMMARY.txt
    └── PUSH_INSTRUCTIONS.md
```

---

## 🚀 Quick Start

### 1. Requirements
Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Master Pipeline Runner
Run the entire analytical pipeline end-to-end:
```bash
python run_pipeline.py --all
```

Or run individual pipeline stages:
```bash
# Data Generation
python run_pipeline.py --stage generate

# Accuracy Comparison & Best Source Selection
python run_pipeline.py --stage compare

# Dataset Preparation
python run_pipeline.py --stage prepare

# Baseline Model Training
python run_pipeline.py --stage train

# Prediction Backtesting
python run_pipeline.py --stage backtest

# Charts & Dashboards
python run_pipeline.py --stage visualize

# Text Reports
python run_pipeline.py --stage reports
```

### 3. Running Standalone Scripts
All scripts can also be executed directly from anywhere:
```bash
python src/analysis/compare_both_periods.py
python src/models/backtest_predictions.py
python src/visualization/visualize_backtest.py
```
Output figures will be saved in `reports/figures/`, reports in `reports/text/`, and processed tables in `data/processed/`.
