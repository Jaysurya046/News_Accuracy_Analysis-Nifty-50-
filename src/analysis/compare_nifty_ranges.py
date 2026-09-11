#!/usr/bin/env python3
"""
Compare support/resistance ranges from news-source Nifty CSVs with actual High/Low
from the uploaded NIFTY CSV. Produce per-source comparison CSVs and a summary printout.
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
    from src.config import (
        get_nifty_file, SOURCES_1Y_DIR, COMPARISON_REPORTS_DIR, get_1year_sources
    )
except ImportError:
    from config import (
        get_nifty_file, SOURCES_1Y_DIR, COMPARISON_REPORTS_DIR, get_1year_sources
    )

NIFTY_FILE = get_nifty_file()

# Helpers to parse ranges
range_re = re.compile(r"(\d+[\.,]?\d*)\s*[-–to]+\s*(\d+[\.,]?\d*)")


def parse_range_field(df_row):
    """Return (support, resistance) if present in row dict-like; otherwise (None, None)."""
    # Check multiple possible column names
    keys = {k.lower(): k for k in df_row.keys()}
    # Priority: Support_Level & Resistance_Level, then Support & Resistance, then Nifty_Range or Nifty_Range_Today
    if 'support_level' in keys and 'resistance_level' in keys:
        try:
            s = float(str(df_row[keys['support_level']]).replace(',', ''))
            r = float(str(df_row[keys['resistance_level']]).replace(',', ''))
            return s, r
        except:
            pass
    if 'support' in keys and 'resistance' in keys:
        try:
            s = float(str(df_row[keys['support']]).replace(',', ''))
            r = float(str(df_row[keys['resistance']]).replace(',', ''))
            return s, r
        except:
            pass
    for candidate in ['nifty_range', 'nifty_rangetoday', 'nifty_range_today', 'nifty_range_today'.lower()]:
        if candidate in keys:
            raw = str(df_row[keys[candidate]])
            m = range_re.search(raw)
            if m:
                try:
                    s = float(m.group(1).replace(',', ''))
                    r = float(m.group(2).replace(',', ''))
                    return s, r
                except:
                    pass
    # Try 'Support' or 'Support_Level' spelled differently
    for k in keys:
        if 'support' in k and 'resistance' in k:
            # unlikely both in same key, skip
            pass
    return None, None


def load_nifty_history(path):
    df = pd.read_csv(path)
    # Normalize column names first (strip whitespace)
    df.columns = [c.strip() for c in df.columns]

    # Find the date/high/low columns case-insensitively
    col_map = {c.lower(): c for c in df.columns}
    date_col = None
    for candidate in ['date', 'trade_date']:
        if candidate in col_map:
            date_col = col_map[candidate]
            break
    if date_col is None:
        # try to find any column that contains 'date'
        for c in df.columns:
            if 'date' in c.lower():
                date_col = c
                break

    high_col = None
    low_col = None
    for c in df.columns:
        lc = c.lower()
        if lc == 'high' or 'high' == lc:
            high_col = c
        if lc == 'low' or 'low' == lc:
            low_col = c

    # fallback: try to match common variants
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
        raise ValueError(f"No date column found in NIFTY file: {path}")

    # Parse date column
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce').dt.date

    # Ensure numeric types for high/low if present
    if high_col is not None:
        df[high_col] = pd.to_numeric(df[high_col], errors='coerce')
    if low_col is not None:
        df[low_col] = pd.to_numeric(df[low_col], errors='coerce')

    # Standardize column names to 'Date','High','Low' for downstream code
    rename_map = {}
    rename_map[date_col] = 'Date'
    if high_col is not None:
        rename_map[high_col] = 'High'
    if low_col is not None:
        rename_map[low_col] = 'Low'
    df = df.rename(columns=rename_map)

    return df


def compare_for_file(news_path, nifty_df, out_dir):
    df = pd.read_csv(news_path)
    if 'Date' not in df.columns:
        print(f"Skipping {news_path}: no Date column")
        return None
    df['Date'] = pd.to_datetime(df['Date']).dt.date

    # Prepare columns for parsed support/resistance
    supports = []
    resistances = []
    for idx, row in df.iterrows():
        s, r = parse_range_field(row)
        supports.append(s)
        resistances.append(r)
    df['Support'] = supports
    df['Resistance'] = resistances

    # Merge with nifty history
    merged = pd.merge(df, nifty_df, on='Date', how='left', suffixes=('', '_market'))

    # Evaluate flags
    def flag_row(row):
        s = row.get('Support')
        r = row.get('Resistance')
        low = row.get('Low')
        high = row.get('High')
        if pd.isna(s) or pd.isna(r) or pd.isna(low) or pd.isna(high):
            return 'NO_DATA'
        below_support = low < s
        above_resistance = high > r
        if below_support and above_resistance:
            return 'BOTH_BREACH'
        if below_support:
            return 'BREACHED_BELOW'
        if above_resistance:
            return 'BREACHED_ABOVE'
        return 'WITHIN_RANGE'

    merged['Range_Flag'] = merged.apply(flag_row, axis=1)

    # Summarize
    summary = merged['Range_Flag'].value_counts(dropna=False).to_dict()

    # Write per-source report
    base = os.path.splitext(os.path.basename(news_path))[0]
    out_csv = os.path.join(out_dir, f'comparison_{base}.csv')
    merged.to_csv(out_csv, index=False)

    return {'file': news_path, 'out_csv': out_csv, 'summary': summary, 'rows_compared': len(merged)}


def main():
    news_files = [str(p) for p in get_1year_sources()]
    if not news_files:
        patterns = ['*nifty50*.csv', '*nifty_50*.csv']
        for pat in patterns:
            news_files.extend(glob.glob(os.path.join(PROJECT_ROOT, pat)))
        news_files = [f for f in news_files if os.path.basename(f) != os.path.basename(NIFTY_FILE)]
        news_files = sorted(set(news_files))

    if not os.path.isfile(NIFTY_FILE):
        print('NIFTY historical CSV not found:', NIFTY_FILE)
        return

    nifty_df = load_nifty_history(NIFTY_FILE)
    out_dir = str(COMPARISON_REPORTS_DIR)

    results = []
    for news in news_files:
        print('Comparing:', os.path.basename(news))
        res = compare_for_file(news, nifty_df, out_dir)
        if res:
            results.append(res)

    # Print summary
    print('\nComparison complete. Summary:')
    total_rows = 0
    for r in results:
        print('\nSource file:', os.path.basename(r['file']))
        print(' Report:', r['out_csv'])
        print(' Rows compared:', r['rows_compared'])
        print(' Flags:')
        for k, v in r['summary'].items():
            print(f'  {k}: {v}')
        total_rows += r['rows_compared']

    print(f'\nReports written to: {out_dir}')
    print(f'Total rows compared across all sources: {total_rows}')

if __name__ == '__main__':
    main()
