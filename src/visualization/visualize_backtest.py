"""
Visualization dashboards for backtest results.
Produces charts for:
  - Per-source hit rates (comparison)
  - Error distributions (box plots)
  - Directional bias (bar chart)
  - Time-series of cumulative hits
  - Overshoot analysis
"""
import os
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.config import FIGURES_DIR, PROCESSED_DATA_DIR, find_file
except ImportError:
    from config import FIGURES_DIR, PROCESSED_DATA_DIR, find_file

sns.set_style("whitegrid")

def create_dashboards(detail_file, summary_file, out_prefix):
    print(f"\n📊 Creating visualizations for {out_prefix}...")
    
    detail_df = pd.read_csv(detail_file, parse_dates=['Date'])
    summary_df = pd.read_csv(summary_file)
    
    # Sort for consistent plotting
    summary_df = summary_df.sort_values('Hit_Rate_%', ascending=False)
    
    # Create a figure with subplots (2x2 grid)
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f'Nifty 50 Prediction Backtest Results ({out_prefix.upper()})', fontsize=16, fontweight='bold')
    
    # Plot 1: Hit Rate Comparison (Top Left)
    ax = axes[0, 0]
    sources_short = [s.replace('_nifty50_', '_').replace('.csv', '').replace(f'_{out_prefix}', '') for s in summary_df['Source']]
    colors = ['green' if h > 4 else 'orange' if h > 3 else 'red' for h in summary_df['Hit_Rate_%']]
    ax.barh(sources_short, summary_df['Hit_Rate_%'], color=colors, alpha=0.7)
    ax.set_xlabel('Hit Rate (%)', fontsize=11, fontweight='bold')
    ax.set_title('Hit Rate by Source', fontsize=12, fontweight='bold')
    ax.axvline(x=summary_df['Hit_Rate_%'].mean(), color='blue', linestyle='--', linewidth=2, label='Average')
    ax.legend()
    ax.grid(axis='x', alpha=0.3)
    
    # Plot 2: Error Magnitudes (Top Right)
    ax = axes[0, 1]
    x_pos = np.arange(len(summary_df))
    width = 0.35
    ax.bar(x_pos - width/2, summary_df['Avg_Abs_High_Error_pts'], width, label='Avg Abs High Error', alpha=0.8)
    ax.bar(x_pos + width/2, summary_df['Avg_Abs_Low_Error_pts'], width, label='Avg Abs Low Error', alpha=0.8)
    ax.set_ylabel('Error (pts)', fontsize=11, fontweight='bold')
    ax.set_title('Average Absolute Errors by Source', fontsize=12, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(sources_short, rotation=45, ha='right', fontsize=9)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # Plot 3: Directional Bias (Bottom Left)
    ax = axes[1, 0]
    bias_colors = ['red' if b < 0 else 'blue' for b in summary_df['Directional_Bias']]
    ax.barh(sources_short, summary_df['Directional_Bias'], color=bias_colors, alpha=0.7)
    ax.set_xlabel('Bias (pts)', fontsize=11, fontweight='bold')
    ax.set_title('Directional Bias (Negative = Underestimates High)', fontsize=12, fontweight='bold')
    ax.axvline(x=0, color='black', linestyle='-', linewidth=1)
    ax.grid(axis='x', alpha=0.3)
    
    # Plot 4: Miss Rate Breakdown (Bottom Right)
    ax = axes[1, 1]
    miss_data = summary_df[['High_Miss_%', 'Low_Miss_%']].head(10)  # top 10
    x_pos = np.arange(len(miss_data))
    width = 0.35
    ax.bar(x_pos - width/2, miss_data['High_Miss_%'], width, label='High Miss %', alpha=0.8, color='coral')
    ax.bar(x_pos + width/2, miss_data['Low_Miss_%'], width, label='Low Miss %', alpha=0.8, color='skyblue')
    ax.set_ylabel('Miss Rate (%)', fontsize=11, fontweight='bold')
    ax.set_title('Miss Rate Breakdown (Top 10 Sources)', fontsize=12, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(sources_short[:10], rotation=45, ha='right', fontsize=9)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    out_file = os.path.join(FIGURES_DIR, f'{out_prefix}_backtest_dashboard.png')
    plt.savefig(out_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'✅ Saved dashboard: {os.path.basename(out_file)}')
    
    # Create a second figure: Time-series of cumulative hits
    fig, axes = plt.subplots(2, 1, figsize=(16, 10))
    fig.suptitle(f'Cumulative Hit Analysis ({out_prefix.upper()})', fontsize=16, fontweight='bold')
    
    # Top sources only (top 3)
    top_sources = summary_df.head(3)['Source'].values
    
    # Plot 1: Cumulative hits over time (Top)
    ax = axes[0]
    for src in top_sources:
        src_data = detail_df[detail_df['Source'] == src].sort_values('Date')
        src_data['Cumulative_Hits'] = src_data['Full_Hit'].astype(int).cumsum()
        src_short = src.replace('_nifty50_', '_').replace('.csv', '').replace(f'_{out_prefix}', '')
        ax.plot(src_data['Date'], src_data['Cumulative_Hits'], marker='o', markersize=2, label=src_short, linewidth=2)
    
    ax.set_ylabel('Cumulative Hit Count', fontsize=11, fontweight='bold')
    ax.set_title('Cumulative Hits Over Time (Top 3 Sources)', fontsize=12, fontweight='bold')
    ax.legend(loc='upper left')
    ax.grid(alpha=0.3)
    
    # Plot 2: Daily errors over time (Bottom) - for best source
    ax = axes[1]
    best_source = summary_df.iloc[0]['Source']
    best_data = detail_df[detail_df['Source'] == best_source].sort_values('Date')
    best_short = best_source.replace('_nifty50_', '_').replace('.csv', '').replace(f'_{out_prefix}', '')
    
    ax.plot(best_data['Date'], best_data['Total_Error'], marker='.', markersize=3, label='Total Error', linewidth=1.5, color='red', alpha=0.7)
    ax.axhline(y=best_data['Total_Error'].mean(), color='red', linestyle='--', linewidth=2, label=f'Average Error ({best_data["Total_Error"].mean():.0f} pts)')
    ax.fill_between(best_data['Date'], best_data['Total_Error'], alpha=0.3, color='red')
    
    ax.set_ylabel('Daily Error (pts)', fontsize=11, fontweight='bold')
    ax.set_xlabel('Date', fontsize=11, fontweight='bold')
    ax.set_title(f'Daily Total Error Over Time - {best_short} (Best Source)', fontsize=12, fontweight='bold')
    ax.legend(loc='upper left')
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    out_file = os.path.join(FIGURES_DIR, f'{out_prefix}_cumulative_analysis.png')
    plt.savefig(out_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'✅ Saved cumulative analysis: {os.path.basename(out_file)}')

if __name__ == '__main__':
    create_dashboards(
        str(find_file('1year_backtest_detail.csv')),
        str(find_file('1year_backtest_summary.csv')),
        '1year'
    )
    
    create_dashboards(
        str(find_file('3year_backtest_detail.csv')),
        str(find_file('3year_backtest_summary.csv')),
        '3year'
    )
    
    print('\n✅ All visualizations complete!')
