"""Prepare merged dataset: merge each source's predictions with ground-truth NIFTY High/Low.
Saves `merged_predictions_1year.csv` and `merged_predictions_3year.csv` in workspace.
"""
import os
import glob
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.config import (
        get_nifty_file, SOURCES_1Y_DIR, SOURCES_3Y_DIR, PROCESSED_DATA_DIR,
        get_1year_sources, get_3year_sources
    )
except ImportError:
    from config import (
        get_nifty_file, SOURCES_1Y_DIR, SOURCES_3Y_DIR, PROCESSED_DATA_DIR,
        get_1year_sources, get_3year_sources
    )

NIFTY_FILE = get_nifty_file()

def load_nifty(path):
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    date_col = None
    for c in df.columns:
        if 'date' in c.lower():
            date_col = c
            break
    if date_col is None:
        raise RuntimeError('No date-like column found in NIFTY file')
    df['Date'] = pd.to_datetime(df[date_col], errors='coerce').dt.date
    # find high/low
    high_col = None; low_col = None
    for c in df.columns:
        if c.lower() == 'high': high_col = c
        if c.lower() == 'low': low_col = c
    if high_col is None or low_col is None:
        for c in df.columns:
            if 'high' in c.lower(): high_col = c; break
        for c in df.columns:
            if 'low' in c.lower(): low_col = c; break
    df = df.rename(columns={high_col: 'Market_High', low_col: 'Market_Low'})
    return df[['Date','Market_High','Market_Low']].set_index('Date')


def parse_support_resistance_from_row(row):
    # try common column names
    for k in ['Support','Support_Level','support','support_level']:
        if k in row.index and pd.notna(row[k]):
            try:
                s = float(str(row[k]).replace(',',''))
            except:
                s = None
            break
    else:
        s = None
    for k in ['Resistance','Resistance_Level','resistance','resistance_level']:
        if k in row.index and pd.notna(row[k]):
            try:
                r = float(str(row[k]).replace(',',''))
            except:
                r = None
            break
    else:
        r = None
    return s, r


def process_glob(pattern, out_name):
    nifty = load_nifty(NIFTY_FILE)
    if '1year' in pattern:
        files = [str(p) for p in get_1year_sources()]
    else:
        files = [str(p) for p in get_3year_sources()]
    if not files:
        files = sorted(glob.glob(os.path.join(PROJECT_ROOT, pattern)))
    rows = []
    for f in files:
        src = os.path.basename(f)
        df = pd.read_csv(f)
        df.columns = [c.strip() for c in df.columns]
        if 'Date' not in df.columns:
            for c in df.columns:
                if 'date' in c.lower():
                    df = df.rename(columns={c:'Date'})
                    break
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
        for _, r in df.iterrows():
            s, res = parse_support_resistance_from_row(r)
            if s is None or res is None:
                # try parsing a single column like "25800 - 27000"
                for c in df.columns:
                    if 'range' in c.lower():
                        val = str(r[c])
                        if '-' in val:
                            parts = val.replace(',', '').split('-')
                            try:
                                s = float(parts[0])
                                res = float(parts[1])
                            except:
                                pass
                        break
            if s is None or res is None:
                continue
            date = r['Date']
            market_high = None; market_low = None
            if date in nifty.index:
                market_high = float(nifty.loc[date, 'Market_High'])
                market_low = float(nifty.loc[date, 'Market_Low'])
            rows.append({'Date': date, 'Source': src, 'Support': s, 'Resistance': res,
                         'RangeWidth': res - s, 'RangeMid': (s+res)/2,
                         'Market_High': market_high, 'Market_Low': market_low})
    out = pd.DataFrame(rows)
    out = out.sort_values('Date')
    out.to_csv(os.path.join(PROCESSED_DATA_DIR, out_name), index=False)
    print('Saved', out_name, 'rows=', len(out))

if __name__ == '__main__':
    process_glob('*_1year.csv', 'merged_predictions_1year.csv')
    process_glob('*_3year.csv', 'merged_predictions_3year.csv')
