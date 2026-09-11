#!/usr/bin/env python3
"""
Generate comparison charts for both 1-year and 3-year datasets.
"""
import matplotlib.pyplot as plt
import pandas as pd
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.config import FIGURES_DIR, PROCESSED_DATA_DIR, find_file
except ImportError:
    from config import FIGURES_DIR, PROCESSED_DATA_DIR, find_file

def plot_period(summary_file, out_file, title):
    df = pd.read_csv(find_file(summary_file))
    df = df.sort_values('Count', ascending=False)
    
    fig, ax1 = plt.subplots(figsize=(14, 6), dpi=100)
    
    x = range(len(df))
    counts = df['Count'].values
    within_pcts = df['WithinPct'].values
    
    color1 = '#1f77b4'
    ax1.bar(x, counts, color=color1, alpha=0.7, label='Times Selected as Best')
    ax1.set_xlabel('Source', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Count', fontsize=11, fontweight='bold', color=color1)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_xticks(x)
    ax1.set_xticklabels([s.replace('_nifty50_', '_').replace('.csv', '') for s in df['Best_Source'].values], 
                         rotation=45, ha='right', fontsize=9)
    
    ax2 = ax1.twinx()
    color2 = '#ff7f0e'
    ax2.plot(x, within_pcts, marker='o', color=color2, linewidth=2, markersize=6, label='Within Range %')
    ax2.set_ylabel('Within Range %', fontsize=11, fontweight='bold', color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)
    
    ax1.set_title(f'{title}\n(Count of times each source was closest to actual High/Low)', 
                  fontsize=12, fontweight='bold', pad=15)
    
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, out_file), dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f'✅ {out_file} generated')
    print(f'   Top source: {df.iloc[0]["Best_Source"]} (Count={int(df.iloc[0]["Count"])}, WithinRange={df.iloc[0]["WithinPct"]:.2f}%)')

plot_period('1year_best_source_summary.csv', '1year_best_source_counts.png', '1-Year Nifty 50 Source Comparison')
plot_period('3year_best_source_summary.csv', '3year_best_source_counts.png', '3-Year Nifty 50 Source Comparison')

print('\n✅ Both comparison charts generated successfully!')
