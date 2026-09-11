import pandas as pd
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.config import PROCESSED_DATA_DIR, find_file
except ImportError:
    from config import PROCESSED_DATA_DIR, find_file

BEST_FILE = str(find_file('best_source_per_day.csv'))
OUT_SUM = os.path.join(PROCESSED_DATA_DIR, 'best_source_summary.csv')

if not os.path.isfile(BEST_FILE):
    print('best_source_per_day.csv not found')
    raise SystemExit(1)

df = pd.read_csv(BEST_FILE)
# Normalize Best_Source strings

df['Best_Source'] = df['Best_Source'].fillna('NONE')
# Convert Best_WithinRange to boolean if string
if df['Best_WithinRange'].dtype == object:
    df['Best_WithinRange'] = df['Best_WithinRange'].map({'True': True, 'False': False}).fillna(df['Best_WithinRange'])

# Group by source
group = df.groupby('Best_Source')
summary = group.agg(
    Count=('Best_Source','count'),
    WithinCount=('Best_WithinRange', lambda s: s.astype(bool).sum()),
    AvgDistance=('Best_Distance', lambda s: pd.to_numeric(s, errors='coerce').mean())
).reset_index()
summary['Pct'] = (summary['Count'] / len(df)) * 100
summary['WithinPct'] = (summary['WithinCount'] / summary['Count']) * 100
summary = summary.sort_values(['Count','WithinPct'], ascending=[False, False])

summary.to_csv(OUT_SUM, index=False)
print('Wrote', OUT_SUM)
print('\nTop sources:')
print(summary.head(10).to_string(index=False))

# Also print overall stats
print('\nOverall days:', len(df))
within_total = df['Best_WithinRange'].astype(bool).sum()
print('Days where best source was within reported range:', within_total, f'({within_total/len(df)*100:.2f}%)')
