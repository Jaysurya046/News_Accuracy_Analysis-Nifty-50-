import pandas as pd

files = [
    'bloomberg_nifty50_9am_365days.csv',
    'cnbc_nifty50_9am_360days.csv',
    'etnow_nifty50_9am_365days.csv',
    'mint_nifty50_9am_360days.csv'
]

for file in files:
    df = pd.read_csv(file)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Count weekends
    saturdays = (df['Date'].dt.dayofweek == 5).sum()
    sundays = (df['Date'].dt.dayofweek == 6).sum()
    
    print(f'\n{file}:')
    print(f'  Total records: {len(df)}')
    print(f'  Saturdays: {saturdays}')
    print(f'  Sundays: {sundays}')
    print(f'  Sample dates with day names:')
    for idx, row in df.head(10).iterrows():
        date_obj = pd.to_datetime(row['Date'])
        day_name = date_obj.strftime('%A')
        print(f'    {str(date_obj.date())} ({day_name})')
