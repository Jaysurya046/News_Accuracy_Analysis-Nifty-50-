import pandas as pd
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.config import SOURCES_3Y_DIR, find_file
except ImportError:
    from config import SOURCES_3Y_DIR, find_file

file_path = find_file('bloomberg_nifty50_3year.csv')
df = pd.read_csv(file_path)
df['Date'] = pd.to_datetime(df['Date'])

saturdays = (df['Date'].dt.dayofweek == 5).sum()
sundays = (df['Date'].dt.dayofweek == 6).sum()

print('Verification - bloomberg_nifty50_3year.csv (3-year):')
print(f'  Total records: {len(df)}')
print(f'  Saturdays: {saturdays}')
print(f'  Sundays: {sundays}')
print(f'  Date range: {df["Date"].min().date()} to {df["Date"].max().date()}')
print(f'  Sample dates:')
sample_indices = [0, 1, 2, 3, 4]
if len(df) > 100:
    sample_indices.extend([100, 200, len(df)-1])
for idx in sample_indices:
    date_obj = df['Date'].iloc[idx]
    day_name = date_obj.strftime('%A')
    print(f'    {date_obj.date()} ({day_name})')
