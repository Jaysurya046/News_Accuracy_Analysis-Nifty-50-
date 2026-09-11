#!/usr/bin/env python3
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

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

IN_FILE = str(find_file('best_source_summary.csv'))
OUT_IMG = os.path.join(FIGURES_DIR, 'best_source_counts.png')

if not os.path.isfile(IN_FILE):
    print('Input file not found:', IN_FILE)
    raise SystemExit(1)

df = pd.read_csv(IN_FILE)
# Sort by Count descending
plot_df = df.sort_values('Count', ascending=False).reset_index(drop=True)

# Create bar chart for Count and line for WithinPct
fig, ax = plt.subplots(figsize=(12,6))
ax.bar(plot_df['Best_Source'], plot_df['Count'], color='tab:blue')
ax.set_xlabel('News Source')
ax.set_ylabel('Best Count (number of days chosen as best)', color='tab:blue')
ax.tick_params(axis='y', labelcolor='tab:blue')
ax.set_xticklabels(plot_df['Best_Source'], rotation=45, ha='right')

# Secondary axis for WithinPct
ax2 = ax.twinx()
ax2.plot(plot_df['Best_Source'], plot_df['WithinPct'], color='tab:orange', marker='o')
ax2.set_ylabel('WithinRange % (of days chosen)', color='tab:orange')
ax2.tick_params(axis='y', labelcolor='tab:orange')

plt.title('Best Source Count and %WithinRange')
plt.tight_layout()
plt.savefig(OUT_IMG, dpi=150)
print('Wrote chart:', OUT_IMG)

# Print top source details
if len(plot_df) > 0:
    top = plot_df.iloc[0]
    print('\nTop source by Count:')
    print(' Source:', top['Best_Source'])
    print(' Count:', int(top['Count']))
    print(' WithinRange count:', int(top['WithinCount']))
    print(' WithinPct:', f"{top['WithinPct']:.2f}%")
else:
    print('No rows in summary file')
