#!/usr/bin/env python3
"""
Merge support/resistance ranges from all news-source Nifty CSVs, compare to actual
NIFTY high/low, compute closeness metric, select best (closest) source per date,
and write `merged_range_comparison.csv` plus a short summary CSV `best_source_per_day.csv`.
"""
import pandas as pd
import glob
import os
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.config import get_nifty_file, SOURCES_1Y_DIR, PROCESSED_DATA_DIR, get_1year_sources
except ImportError:
    from config import get_nifty_file, SOURCES_1Y_DIR, PROCESSED_DATA_DIR, get_1year_sources

NIFTY_FILE = get_nifty_file()

range_re = re.compile(r"(\d+[\.,]?\d*)\s*[-–to]+\s*(\d+[\.,]?\d*)")


def parse_range_from_row(row):
    # row is a Series
    # try Support_Level and Resistance_Level
    keys = {k.lower(): k for k in row.index}
    try_keys = []
    if 'support_level' in keys and 'resistance_level' in keys:
        try_keys.append((keys['support_level'], keys['resistance_level']))
    if 'support' in keys and 'resistance' in keys:
        try_keys.append((keys['support'], keys['resistance']))
    # Nifty range variants
    for cand in ['nifty_range', 'nifty_range_today', 'nifty_rangetoday', 'nifty_range_today']:
        if cand in keys:
            try_keys.append((keys[cand],))
    # try to parse any column that contains 'range'
    for k in row.index:
        if 'range' in k.lower():
            try_keys.append((k,))

    s = r = None
    for tk in try_keys:
        if len(tk) == 2:
            a = row.get(tk[0])
            b = row.get(tk[1])
            try:
                s = float(str(a).replace(',', ''))
                r = float(str(b).replace(',', ''))
                return s, r
            except:
                continue
        else:
            raw = str(row.get(tk[0], ''))
            m = range_re.search(raw)
            if m:
                try:
                    s = float(m.group(1).replace(',', ''))
                    r = float(m.group(2).replace(',', ''))
                    return s, r
                except:
                    continue
    return None, None


def load_nifty_history(path):
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    # find date/high/low columns
    col_map = {c.lower(): c for c in df.columns}
    date_col = None
    for candidate in ['date', 'trade_date']:
        if candidate in col_map:
            date_col = col_map[candidate]
            break
    if date_col is None:
        for c in df.columns:
            if 'date' in c.lower():
                date_col = c
                break
    high_col = None
    low_col = None
    for c in df.columns:
        if c.lower() == 'high':
            high_col = c
        if c.lower() == 'low':
            low_col = c
    if high_col is None:
        for c in df.columns:
            if 'high' in c.lower():
                high_col = c
                break
    if low_col is None:
        for c in df.columns:
            if 'low' in c.lower():
                low_col = c
                break
    if date_col is None:
        raise ValueError('No date column in NIFTY file')
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce').dt.date
    if high_col:
        df[high_col] = pd.to_numeric(df[high_col], errors='coerce')
    if low_col:
        df[low_col] = pd.to_numeric(df[low_col], errors='coerce')
    rename_map = {date_col: 'Date'}
    if high_col:
        rename_map[high_col] = 'High'
    if low_col:
        rename_map[low_col] = 'Low'
    df = df.rename(columns=rename_map)
    return df[['Date', 'High', 'Low']]


def main():
    nifty = load_nifty_history(NIFTY_FILE)
    nifty = nifty.set_index('Date')

    # find source files
    files = [str(p) for p in get_1year_sources()]
    if not files:
        files = sorted([f for f in glob.glob(os.path.join(PROJECT_ROOT, '*nifty50*.csv')) if os.path.basename(f) != os.path.basename(NIFTY_FILE)])
    # Ensure we have the 10 files
    print('Source files:', [os.path.basename(f) for f in files])

    per_source = {}
    dates = set(nifty.index.tolist())

    for f in files:
        df = pd.read_csv(f)
        # normalize columns
        df.columns = [c.strip() for c in df.columns]
        if 'Date' not in df.columns and 'date' in [c.lower() for c in df.columns]:
            # find actual case
            for c in df.columns:
                if c.lower() == 'date':
                    df = df.rename(columns={c: 'Date'})
                    break
        if 'Date' not in df.columns:
            print('Skipping', f, 'no Date column')
            continue
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
        df = df.set_index('Date')

        # extract support/resistance per date
        supports = {}
        resistances = {}
        for idx, row in df.iterrows():
            s, r = parse_range_from_row(row)
            if s is not None and r is not None:
                supports[idx] = s
                resistances[idx] = r
        per_source[os.path.basename(f)] = {'support': supports, 'resistance': resistances}
        dates.update(supports.keys())
        dates.update(resistances.keys())

    all_dates = sorted(dates)

    # Build merged rows
    rows = []
    for d in all_dates:
        market = nifty.loc[d] if d in nifty.index else None
        row = {'Date': d}
        if market is not None:
            row['Market_High'] = market['High']
            row['Market_Low'] = market['Low']
        else:
            row['Market_High'] = None
            row['Market_Low'] = None
        # for each source, add support, resistance and compute distance metric
        distances = {}
        for src, data in per_source.items():
            s = data['support'].get(d)
            r = data['resistance'].get(d)
            row[f'{src}_Support'] = s
            row[f'{src}_Resistance'] = r
            if s is None or r is None or row['Market_High'] is None or row['Market_Low'] is None:
                distances[src] = None
            else:
                # distance metric: sum abs diffs
                dist = abs(s - row['Market_Low']) + abs(r - row['Market_High'])
                distances[src] = dist
                row[f'{src}_Distance'] = dist
        # select best source with minimal distance (non-null)
        best = None
        best_dist = None
        for src, dist in distances.items():
            if dist is None:
                continue
            if best_dist is None or dist < best_dist:
                best = src
                best_dist = dist
        row['Best_Source'] = best
        row['Best_Distance'] = best_dist
        rows.append(row)

    merged_df = pd.DataFrame(rows)
    out1 = os.path.join(PROCESSED_DATA_DIR, 'merged_range_comparison.csv')
    merged_df.to_csv(out1, index=False)

    # Create summary: per-date best source and its distance, plus flag if within range
    summary_rows = []
    for idx, r in merged_df.iterrows():
        best = r['Best_Source']
        dist = r['Best_Distance']
        date = r['Date']
        market_low = r['Market_Low']
        market_high = r['Market_High']
        within = None
        if best:
            s = r.get(f'{best}_Support')
            res = r.get(f'{best}_Resistance')
            if s is not None and res is not None and market_low is not None and market_high is not None:
                within = (market_low >= s and market_high <= res)
        summary_rows.append({'Date': date, 'Best_Source': best, 'Best_Distance': dist, 'Best_WithinRange': within})

    summary_df = pd.DataFrame(summary_rows)
    out2 = os.path.join(PROCESSED_DATA_DIR, 'best_source_per_day.csv')
    summary_df.to_csv(out2, index=False)

    print('\nWrote:')
    print(' -', out1)
    print(' -', out2)
    print('\nTop 10 best sources:')
    print(summary_df.head(10).to_string(index=False))

if __name__ == '__main__':
    main()
