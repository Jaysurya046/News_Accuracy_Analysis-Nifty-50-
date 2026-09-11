"""
Comprehensive backtest of news-source Nifty 50 predictions.
Calculates:
  - Range Coverage (Full Hit, High Miss, Low Miss)
  - Error metrics (High Error, Low Error, Avg Absolute Error)
  - Per-source rankings and directional bias
  - Overshoot analysis
Produces CSV reports and per-source summaries.
"""
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import json

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.config import PROCESSED_DATA_DIR, find_file
except ImportError:
    from config import PROCESSED_DATA_DIR, find_file

def run_backtest(merged_file, out_prefix):
    print(f"\n{'='*70}")
    print(f"Running backtest on {os.path.basename(merged_file)}")
    print(f"{'='*70}")
    
    df = pd.read_csv(merged_file, parse_dates=['Date'])
    df = df.sort_values('Date')
    
    # Drop rows missing market data
    df = df.dropna(subset=['Market_High', 'Market_Low'])
    
    # Rename columns for clarity
    df = df.rename(columns={'Support': 'Pred_Low', 'Resistance': 'Pred_High'})
    
    # === STEP 1: RANGE COVERAGE ===
    # Full Hit: actual low >= pred low AND actual high <= pred high
    df['Full_Hit'] = (df['Market_Low'] >= df['Pred_Low']) & (df['Market_High'] <= df['Pred_High'])
    
    # High Miss: actual high > pred high
    df['High_Miss'] = df['Market_High'] > df['Pred_High']
    
    # Low Miss: actual low < pred low
    df['Low_Miss'] = df['Market_Low'] < df['Pred_Low']
    
    # Both Miss
    df['Both_Miss'] = df['High_Miss'] & df['Low_Miss']
    
    # === STEP 2: ERROR METRICS ===
    # High Error (positive = market went higher than predicted)
    df['High_Error'] = df['Market_High'] - df['Pred_High']
    
    # Low Error (positive = market went lower than predicted)
    df['Low_Error'] = df['Pred_Low'] - df['Market_Low']
    
    # Absolute Errors
    df['Abs_High_Error'] = np.abs(df['High_Error'])
    df['Abs_Low_Error'] = np.abs(df['Low_Error'])
    df['Total_Error'] = df['Abs_High_Error'] + df['Abs_Low_Error']
    
    # Overshoot (only positive errors, i.e., when predictions were wrong)
    df['High_Overshoot'] = df['High_Error'].apply(lambda x: max(0, x))
    df['Low_Overshoot'] = df['Low_Error'].apply(lambda x: max(0, x))
    
    # === STEP 3: PER-SOURCE SUMMARY ===
    sources = df['Source'].unique()
    summary_rows = []
    
    for src in sorted(sources):
        src_df = df[df['Source'] == src]
        n_days = len(src_df)
        
        # Coverage
        hit_count = src_df['Full_Hit'].sum()
        hit_pct = (hit_count / n_days * 100) if n_days > 0 else 0
        high_miss_pct = (src_df['High_Miss'].sum() / n_days * 100) if n_days > 0 else 0
        low_miss_pct = (src_df['Low_Miss'].sum() / n_days * 100) if n_days > 0 else 0
        
        # Errors
        avg_high_error = src_df['High_Error'].mean()
        avg_low_error = src_df['Low_Error'].mean()
        avg_abs_high_error = src_df['Abs_High_Error'].mean()
        avg_abs_low_error = src_df['Abs_Low_Error'].mean()
        avg_total_error = src_df['Total_Error'].mean()
        
        # Overshoot (only when wrong)
        high_overshoots = src_df[src_df['High_Overshoot'] > 0]['High_Overshoot']
        low_overshoots = src_df[src_df['Low_Overshoot'] > 0]['Low_Overshoot']
        avg_high_overshoot = high_overshoots.mean() if len(high_overshoots) > 0 else 0
        avg_low_overshoot = low_overshoots.mean() if len(low_overshoots) > 0 else 0
        
        # Directional Bias
        # Positive avg_high_error = channel underestimates the high (biased low)
        # Positive avg_low_error = channel overestimates the low (biased high)
        bias = avg_high_error - avg_low_error  # positive = biased low overall
        
        summary_rows.append({
            'Source': src,
            'N_Days': n_days,
            'Hit_Count': int(hit_count),
            'Hit_Rate_%': round(hit_pct, 2),
            'High_Miss_%': round(high_miss_pct, 2),
            'Low_Miss_%': round(low_miss_pct, 2),
            'Avg_High_Error_pts': round(avg_high_error, 2),
            'Avg_Low_Error_pts': round(avg_low_error, 2),
            'Avg_Abs_High_Error_pts': round(avg_abs_high_error, 2),
            'Avg_Abs_Low_Error_pts': round(avg_abs_low_error, 2),
            'Avg_Total_Error_pts': round(avg_total_error, 2),
            'Avg_High_Overshoot_pts': round(avg_high_overshoot, 2),
            'Avg_Low_Overshoot_pts': round(avg_low_overshoot, 2),
            'Directional_Bias': round(bias, 2)
        })
    
    summary_df = pd.DataFrame(summary_rows)
    summary_df = summary_df.sort_values('Hit_Rate_%', ascending=False)
    
    # Save detailed backtest results and summary
    detail_file = os.path.join(PROCESSED_DATA_DIR, f'{out_prefix}_backtest_detail.csv')
    summary_file = os.path.join(PROCESSED_DATA_DIR, f'{out_prefix}_backtest_summary.csv')
    
    df.to_csv(detail_file, index=False)
    summary_df.to_csv(summary_file, index=False)
    
    print(f'\n✅ Saved detailed backtest: {os.path.basename(detail_file)}')
    print(f'✅ Saved summary: {os.path.basename(summary_file)}')
    
    # Print summary
    print(f'\n📊 BACKTEST SUMMARY ({out_prefix}):')
    print(summary_df.to_string(index=False))
    
    # Overall statistics
    print(f'\n📈 OVERALL STATISTICS:')
    print(f"  Total days tested: {len(df)}")
    print(f"  Average Hit Rate across all sources: {df['Full_Hit'].mean() * 100:.2f}%")
    print(f"  Average High Miss Rate: {df['High_Miss'].mean() * 100:.2f}%")
    print(f"  Average Low Miss Rate: {df['Low_Miss'].mean() * 100:.2f}%")
    print(f"  Avg Abs High Error: {df['Abs_High_Error'].mean():.2f} pts")
    print(f"  Avg Abs Low Error: {df['Abs_Low_Error'].mean():.2f} pts")
    
    # Top and Bottom performers
    print(f'\n🏆 TOP 3 SOURCES (by Hit Rate):')
    for idx, row in summary_df.head(3).iterrows():
        print(f"  {row['Source']}: {row['Hit_Rate_%']:.2f}% hit rate, {row['Hit_Count']}/{row['N_Days']} days")
    
    print(f'\n⚠️  BOTTOM 3 SOURCES (by Hit Rate):')
    for idx, row in summary_df.tail(3).iterrows():
        print(f"  {row['Source']}: {row['Hit_Rate_%']:.2f}% hit rate, {row['Hit_Count']}/{row['N_Days']} days")
    
    return df, summary_df

if __name__ == '__main__':
    # Run backtest for both 1-year and 3-year
    df_1yr, summary_1yr = run_backtest(
        str(find_file('merged_predictions_1year.csv')),
        '1year'
    )
    
    df_3yr, summary_3yr = run_backtest(
        str(find_file('merged_predictions_3year.csv')),
        '3year'
    )
    
    print(f"\n{'='*70}")
    print("✅ BACKTEST COMPLETE")
    print(f"{'='*70}")
