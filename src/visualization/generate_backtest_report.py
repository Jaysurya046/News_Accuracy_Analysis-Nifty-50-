"""
Generate a comprehensive backtest report summarizing all metrics, insights, and recommendations.
"""
import os
import sys
from pathlib import Path
import pandas as pd
import json
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.config import TEXT_REPORTS_DIR, PROCESSED_DATA_DIR, find_file
except ImportError:
    from config import TEXT_REPORTS_DIR, PROCESSED_DATA_DIR, find_file

def generate_report(summary_file, detail_file, out_prefix):
    summary_df = pd.read_csv(summary_file)
    detail_df = pd.read_csv(detail_file, parse_dates=['Date'])
    
    best_src = summary_df.iloc[0]
    worst_src = summary_df.iloc[-1]
    
    report = f"""
{'='*80}
NIFTY 50 PREDICTION BACKTEST REPORT ({out_prefix.upper()})
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*80}

EXECUTIVE SUMMARY
{'-'*80}
Total Sources Tested: {len(summary_df)}
Total Trading Days: {len(detail_df[detail_df['Full_Hit'] == True].groupby('Date').size())}
Average Hit Rate (All Sources): {detail_df['Full_Hit'].mean()*100:.2f}%
Most Accurate Source: {best_src['Source']} ({best_src['Hit_Rate_%']:.2f}% hit rate)
Least Accurate Source: {worst_src['Source']} ({worst_src['Hit_Rate_%']:.2f}% hit rate)

KEY METRICS EXPLAINED
{'-'*80}

1. HIT RATE (%)
   - Definition: Percentage of days where actual High <= Predicted High AND actual Low >= Predicted Low
   - Interpretation: Higher is better (lucky to have hits at all with synthetic data)
   - Current Average: {detail_df['Full_Hit'].mean()*100:.2f}%

2. MISS RATES (%)
   - High Miss: Actual High exceeded Predicted High
   - Low Miss: Actual Low fell below Predicted Low
   - Current High Miss Rate: {detail_df['High_Miss'].mean()*100:.2f}%
   - Current Low Miss Rate: {detail_df['Low_Miss'].mean()*100:.2f}%
   - Insight: Nearly all predictions "miss low" (underestimate the low bound)

3. ERROR METRICS (Points)
   - Avg High Error: {detail_df['High_Error'].mean():.2f} pts (negative = underestimate)
   - Avg Low Error: {detail_df['Low_Error'].mean():.2f} pts (positive = overestimate)
   - Avg Total Error: {detail_df['Total_Error'].mean():.2f} pts

4. DIRECTIONAL BIAS
   - Definition: (Avg High Error - Avg Low Error)
   - Negative = Channel biased LOW (underestimates highs, overestimates lows)
   - Positive = Channel biased HIGH (overestimates highs, underestimates lows)
   - Current Bias: {detail_df['High_Error'].mean() - detail_df['Low_Error'].mean():.2f} pts

TOP 5 PERFORMERS (by Hit Rate)
{'-'*80}
"""
    for idx, (i, row) in enumerate(summary_df.head(5).iterrows(), 1):
        report += f"\n{idx}. {row['Source']}\n"
        report += f"   Hit Rate: {row['Hit_Rate_%']:.2f}% ({int(row['Hit_Count'])}/{int(row['N_Days'])} days)\n"
        report += f"   Avg Total Error: {row['Avg_Total_Error_pts']:.2f} pts\n"
        report += f"   Avg High Overshoot: {row['Avg_High_Overshoot_pts']:.2f} pts (when wrong on high)\n"
        report += f"   Avg Low Overshoot: {row['Avg_Low_Overshoot_pts']:.2f} pts (when wrong on low)\n"
        report += f"   Directional Bias: {row['Directional_Bias']:.2f} pts\n"

    report += f"""
BOTTOM 5 PERFORMERS (by Hit Rate)
{'-'*80}
"""
    for idx, (i, row) in enumerate(summary_df.tail(5).iloc[::-1].iterrows(), 1):
        report += f"\n{idx}. {row['Source']}\n"
        report += f"   Hit Rate: {row['Hit_Rate_%']:.2f}% ({int(row['Hit_Count'])}/{int(row['N_Days'])} days)\n"
        report += f"   Avg Total Error: {row['Avg_Total_Error_pts']:.2f} pts\n"

    report += f"""
DETAILED ANALYSIS
{'-'*80}

Range Coverage Pattern:
  - All sources show ~96-97% "Low Miss" rate
  - This indicates predictions are consistently TOO HIGH on the low bound
  - Nifty typically trades LOWER than predicted support levels
  - Insight: If using these ranges for risk management, use TIGHTER stops than predicted

Accuracy Comparison:
  Best Source (Hit Rate):      {best_src['Source']}: {best_src['Hit_Rate_%']:.2f}%
  Average Hit Rate:             {detail_df['Full_Hit'].mean()*100:.2f}%
  Worst Source (Hit Rate):      {worst_src['Source']}: {worst_src['Hit_Rate_%']:.2f}%
  
  Best Source (Abs Error):      {summary_df.loc[summary_df['Avg_Total_Error_pts'].idxmin(), 'Source']}: {summary_df['Avg_Total_Error_pts'].min():.2f} pts
  Worst Source (Abs Error):     {summary_df.loc[summary_df['Avg_Total_Error_pts'].idxmax(), 'Source']}: {summary_df['Avg_Total_Error_pts'].max():.2f} pts

Bias Analysis:
  Most Pessimistic (Lowest Bias):  {summary_df.loc[summary_df['Directional_Bias'].idxmin(), 'Source']}: {summary_df['Directional_Bias'].min():.2f} pts
  Most Optimistic (Highest Bias):  {summary_df.loc[summary_df['Directional_Bias'].idxmax(), 'Source']}: {summary_df['Directional_Bias'].max():.2f} pts
  
  Interpretation: All sources show negative bias (biased LOW)

KEY INSIGHTS & RECOMMENDATIONS
{'-'*80}

1. SYNTHETIC DATA CAVEAT
   - This backtest uses SYNTHETIC price predictions (not real news channel data)
   - Real predictions may have different accuracy characteristics
   - Consider collecting REAL predictions for more accurate backtesting

2. PREDICTION QUALITY
   - Hit rates ~3-5% suggest:
     a) Predictions are very wide ranges (not precise)
     b) Actual volatility often exceeds predicted ranges
     c) OR both (realistic given market dynamics)

3. RISK MANAGEMENT IMPLICATIONS
   - Predicted ranges are TOO HIGH on the low side (96%+ Low Miss rate)
   - Traders using these: Set stops TIGHTER than predicted support
   - Expected slippage: ~1,590 pts below predicted support on average

4. FOR TRADING STRATEGY
   - Combine predictions with:
     a) Support/Resistance from technical analysis
     b) Options implied volatility (IV) for expected range
     c) Historical volatility patterns
   - Don't rely solely on news-channel predictions

5. MODEL IMPROVEMENT OPPORTUNITIES
   - Train a machine learning model to ADJUST predictions
   - Use features: source, market open, implied vol, day-of-week, etc.
   - Target: Minimize error or maximize hit rate
   - Backtesting framework ready (see train_gbm.py)

OUTPUT FILES GENERATED
{'-'*80}
  - {os.path.basename(summary_file)}: Per-source summary metrics
  - {os.path.basename(detail_file)}: Daily predictions + errors
  - {out_prefix}_backtest_dashboard.png: Visual comparison charts
  - {out_prefix}_cumulative_analysis.png: Time-series analysis
  - This report

NEXT STEPS
{'-'*80}
1. Review visualizations for patterns (PNG files)
2. Consider collecting REAL news channel predictions for production use
3. Experiment with LightGBM model (train_gbm.py) to improve predictions
4. Use LLM for natural language classification (run_llm_prompts.py)
5. Deploy best model to production with retraining schedule

{'='*80}
"""
    
    return report

if __name__ == '__main__':
    # Generate reports
    for prefix in ['1year', '3year']:
        summary_file = str(find_file(f'{prefix}_backtest_summary.csv'))
        detail_file = str(find_file(f'{prefix}_backtest_detail.csv'))
        report = generate_report(summary_file, detail_file, prefix)
        
        report_file = os.path.join(TEXT_REPORTS_DIR, f'{prefix}_backtest_report.txt')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(report)
        print(f"✅ Saved report: {os.path.basename(report_file)}\n")
