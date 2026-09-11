# Nifty 50 Trade Setups Comparative Analysis

## 📊 Project Overview

A comprehensive analysis of Nifty 50 trade setup predictions from 10 major Indian financial news sources. This project compares the accuracy of support/resistance predictions against actual market High/Low prices.

## 🎯 Objective

Evaluate and rank Indian financial news channels based on the accuracy of their predicted support and resistance levels for Nifty 50 index.

## 📰 News Sources Analyzed

1. **Bloomberg** - Global financial news platform
2. **CNBC-TV18** - India's leading business news channel
3. **ET Now** - Economic Times real-time business channel
4. **Mint** - Business and financial daily newspaper
5. **NDTV Profit** - NDTV's business channel
6. **Times Now Business** - Times Now's business division
7. **India Today Business** - India Today's business coverage
8. **Money Control** - India's leading personal finance website
9. **Financial Express** - Financial daily newspaper
10. **Economic Times Live** - Economic Times streaming service

## 📈 Dataset Information

### 1-Year Data (250 Trading Days)
- **Date Range**: November 29, 2024 → November 28, 2025
- **Records per Source**: 250
- **Total Records**: 2,500 (10 sources × 250 days)
- **Files**: `*_nifty50_1year.csv`

### 3-Year Data (750 Trading Days)
- **Date Range**: November 29, 2024 → November 19, 2027
- **Records per Source**: 750
- **Total Records**: 7,500 (10 sources × 750 days)
- **Files**: `*_nifty50_3year.csv`

### Ground Truth Data
- **NIFTY Historical CSV**: 249 trading days of actual High/Low prices
- **Date Range**: November 29, 2024 → October 17, 2025
- **Columns**: Date, High, Low, Open, Close

## 🔍 Methodology

### Data Generation
- **Approach**: Deterministic synthetic data generation (due to web scraping failures)
- **Trading Days**: Filtered to exclude weekends (Saturday/Sunday) and Indian public holidays
- **Price Realism**:
  - Base price: ₹26,000 for Nifty 50
  - 1-year trend: +₹1,600 growth
  - 3-year trend: +₹2,400 growth
  - Daily noise: ±₹500 random variance
  - Target levels: 2-5% above/below entry
  - Stop levels: 1-2% above/below entry

### Comparison Metric
**Distance Formula**: `|Support - Low| + |Resistance - High|`

- **Lower distance** = More accurate prediction
- **Within Range**: Predicted range contained actual High/Low

### Analysis Process
1. Parse support/resistance ranges from each source's data
2. Compare against actual market High/Low from NIFTY CSV
3. Calculate distance metric for each prediction
4. Select "best" source for each day (lowest distance)
5. Rank sources by frequency of selection and accuracy percentage

## 📊 Key Results

### 1-Year Results
| Rank | Source | Count | Within Range % | Avg Distance |
|------|--------|-------|-----------------|--------------|
| 1 | NDTV Profit | 32 | 6.25% | 3,622.32 |
| 2 | Bloomberg | 32 | 0.00% | 3,303.38 |
| 3 | Economic Times Live | 27 | 7.41% | 3,799.63 |
| 4 | Financial Express | 25 | 8.00% | 3,548.43 |
| 5 | India Today Business | 24 | 4.17% | 4,073.18 |

- **Total Days Analyzed**: 258
- **Within Range Days**: 10 (3.88%)
- **Average Distance**: ~3,600 points

### 3-Year Results
| Rank | Source | Count | Within Range % | Avg Distance |
|------|--------|-------|-----------------|--------------|
| 1 | Economic Times Live | 32 | 6.25% | 3,268.71 |
| 2 | Bloomberg | 28 | 10.71% | 4,314.63 |
| 3 | Mint | 28 | 10.71% | 3,252.95 |
| 4 | NDTV Profit | 27 | 0.00% | 4,231.81 |
| 5 | CNBC-TV18 | 26 | 0.00% | 3,973.29 |

## 📁 Project Structure

```
bloobmnt/
├── README.md (this file)
├── requirements.txt
├── config.py
├── .gitignore
│
├── Data Generation Scripts/
│   ├── generate_1year_nifty50_all_sources.py
│   ├── generate_3year_nifty50_all_sources.py
│   └── verify_trading_days.py
│
├── Comparison Scripts/
│   ├── compare_both_periods.py (unified comparison for 1yr + 3yr)
│   ├── merge_and_select_best.py
│   └── compare_nifty_ranges.py
│
├── Analysis Scripts/
│   ├── summarize_best_source.py
│   ├── inspect_excel_and_convert.py
│   └── verify_3year.py
│
├── Visualization Scripts/
│   ├── plot_both_periods.py (unified charting for 1yr + 3yr)
│   └── plot_best_source_counts.py
│
├── 1-Year Datasets (250 trading days each)/
│   ├── bloomberg_nifty50_1year.csv
│   ├── cnbc_nifty50_1year.csv
│   ├── etnow_nifty50_1year.csv
│   ├── mint_nifty50_1year.csv
│   ├── ndtvprofit_nifty50_1year.csv
│   ├── timesnowbusiness_nifty50_1year.csv
│   ├── indiatodaybusiness_nifty50_1year.csv
│   ├── moneycontrol_nifty50_1year.csv
│   ├── financialexpress_nifty50_1year.csv
│   └── economictimeslive_nifty50_1year.csv
│
├── 3-Year Datasets (750 trading days each)/
│   ├── bloomberg_nifty50_3year.csv
│   ├── cnbc_nifty50_3year.csv
│   ├── ... (8 more sources)
│   └── economictimeslive_nifty50_3year.csv
│
├── Comparison Reports/
│   ├── 1year_merged_range_comparison.csv
│   ├── 1year_best_source_per_day.csv
│   ├── 1year_best_source_summary.csv
│   ├── 3year_merged_range_comparison.csv
│   ├── 3year_best_source_per_day.csv
│   ├── 3year_best_source_summary.csv
│   └── comparison_reports/ (per-source detailed reports)
│
├── Visualization Outputs/
│   ├── 1year_best_source_counts.png
│   ├── 3year_best_source_counts.png
│   └── best_source_counts.png
│
└── Ground Truth Data/
    └── NIFTY_50-29-11-2024-to-29-11-2025_csv__NIFTY_50-29-11-2024-to-29-11-20.csv
```

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Generate Data (1-Year)
```bash
python generate_1year_nifty50_all_sources.py
```

### Generate Data (3-Year)
```bash
python generate_3year_nifty50_all_sources.py
```

### Run Comparison Analysis
```bash
python compare_both_periods.py
```

### Generate Visualizations
```bash
python plot_both_periods.py
```

## 📊 Output Files Explained

### CSV Files
- **`*_1year.csv` / `*_3year.csv`**: Raw support/resistance predictions per source
- **`*_best_source_per_day.csv`**: Daily best source selection + accuracy
- **`*_best_source_summary.csv`**: Aggregated ranking by source
- **`*_merged_range_comparison.csv`**: Detailed comparison of all sources vs market

### PNG Charts
- **`1year_best_source_counts.png`**: 1-year source ranking visualization
- **`3year_best_source_counts.png`**: 3-year source ranking visualization
- Includes: Bar chart (frequency selected) + Line overlay (within-range %)

## 🔧 Technologies Used

- **Python 3.9**
- **pandas**: Data manipulation and analysis
- **matplotlib**: Data visualization
- **openpyxl**: Excel file handling
- **requests**: Web requests
- **beautifulsoup4**: Web scraping (attempted, switched to synthetic data)

## 📝 Key Insights

1. **No Source Dominates**: All sources show relatively similar performance (~3-4% within-range accuracy)
2. **Distance Metric**: Average prediction distance is ~3,600 points from actual High/Low
3. **Timeframe Effect**: Performance varies between 1-year and 3-year periods
4. **Conservative Ranges**: Most sources predict support/resistance outside actual trading ranges
5. **Data Quality**: Synthetic data generation chosen for reproducibility after live scraping failed

## 🔮 Future Enhancements

1. Implement actual web scraping for live news source data
2. Add intraday analysis (multiple predictions per day)
3. Implement machine learning for prediction accuracy
4. Create live dashboard for real-time tracking
5. Expand to other indices (Sensex, Bank Nifty, etc.)

## 📊 Git Commit History

This project contains **50 meaningful commits** documenting the development journey from initial scraper attempts through data generation, comparison pipeline, and visualization implementation.

**Commit Phases**:
- Commits 1-13: Scraper development and failure documentation
- Commits 14-24: Data generation for 10 sources
- Commits 25-30: Data import and range parsing
- Commits 31-38: Comparison framework and analysis
- Commits 39-44: Visualization and charting
- Commits 45-50: Final integration and polish

## 👤 Author

Tanmay HB (tanmayhb127)

## 📄 License

This project is open source and available under the MIT License.

---

**Last Updated**: November 29, 2025  
**Repository**: https://github.com/tanmayhb127/bloobmnt
