import pandas as pd

df = pd.read_csv('bloomberg_nifty50_trading_days.csv')
df['Date'] = pd.to_datetime(df['Date'])

saturdays = (df['Date'].dt.dayofweek == 5).sum()
sundays = (df['Date'].dt.dayofweek == 6).sum()

print('Verification - bloomberg_nifty50_trading_days.csv:')
print(f'  Total: {len(df)} records')
print(f'  Saturdays: {saturdays}')
print(f'  Sundays: {sundays}')
print(f'\nSample trading days:')
for idx, row in df.head(10).iterrows():
    date_obj = pd.to_datetime(row['Date'])
    day_name = date_obj.strftime('%A')
    print(f'  {str(date_obj.date())} ({day_name})')
