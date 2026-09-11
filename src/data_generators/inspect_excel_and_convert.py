#!/usr/bin/env python3
import sys
import os
import pandas as pd

def safe_filename(name):
    return "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name).strip().replace(' ', '_')

if len(sys.argv) < 2:
    print('Usage: python inspect_excel_and_convert.py <excel-file-path>')
    sys.exit(1)

file_path = sys.argv[1]
if not os.path.isfile(file_path):
    print(f'File not found: {file_path}')
    sys.exit(1)

print(f'Inspecting: {file_path}')

try:
    xls = pd.ExcelFile(file_path)
except Exception as e:
    print('Error opening Excel file:', e)
    sys.exit(1)

sheets = xls.sheet_names
print('Sheets found:', sheets)

created_files = []
for sheet in sheets:
    try:
        df = xls.parse(sheet)
    except Exception as e:
        print(f'  Error reading sheet "{sheet}":', e)
        continue
    
    print(f'\nSheet: {sheet} — rows: {len(df)}, cols: {len(df.columns)}')
    print(df.head(5).to_string(index=False))
    
    base = os.path.splitext(os.path.basename(file_path))[0]
    out_name = f"{safe_filename(base)}__{safe_filename(sheet)}.csv"
    out_path = os.path.join(os.path.dirname(file_path), out_name)
    try:
        df.to_csv(out_path, index=False)
        created_files.append(out_path)
        print(f'  -> Written CSV: {out_path}')
    except Exception as e:
        print(f'  Error writing CSV for sheet "{sheet}":', e)

print('\nConversion complete.')
if created_files:
    print('Created files:')
    for f in created_files:
        print('  ', f)
else:
    print('No CSV files were created.')
