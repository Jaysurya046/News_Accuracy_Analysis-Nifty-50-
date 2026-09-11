#!/usr/bin/env python3
"""
Generate 1 year of sample Nifty trade setup data for demonstration.
Creates realistic daily predictions with varying assets and market conditions.
"""

import pandas as pd
from datetime import datetime, timedelta
import random

# Configuration
START_DATE = datetime(2024, 11, 29)
END_DATE = datetime(2025, 11, 29)
STOCKS = [
    'Nifty 50', 'Sensex', 'Reliance', 'HDFC Bank', 'Infosys', 'TCS', 'Axis Bank',
    'ITC', 'Bajaj Auto', 'LT', 'SBI', 'ICICI Bank', 'Wipro', 'HCL Tech',
    'Asian Paints', 'Maruti', 'NTPC', 'Coal India', 'Power Grid', 'Gail',
    'Bharti Airtel', 'Jio Financial', 'Kotak Bank', 'Sundar Pharma', 'Dr Reddy',
]

ACTIONS = ['Buy', 'Sell']

# Realistic ranges for prices (INR)
PRICE_RANGES = {
    'Nifty 50': (24000, 28000),
    'Sensex': (79000, 92000),
    'Reliance': (3000, 3800),
    'HDFC Bank': (1600, 2000),
    'Infosys': (4000, 4800),
    'TCS': (3900, 4600),
    'Axis Bank': (2000, 2500),
    'ITC': (400, 550),
    'Bajaj Auto': (8000, 10000),
    'LT': (2200, 2700),
    'SBI': (700, 900),
    'ICICI Bank': (1100, 1400),
    'Wipro': (500, 650),
    'HCL Tech': (1900, 2400),
    'Asian Paints': (3000, 3800),
    'Maruti': (12000, 15000),
    'NTPC': (300, 400),
    'Coal India': (500, 700),
    'Power Grid': (300, 400),
    'Gail': (200, 280),
    'Bharti Airtel': (1450, 1850),
    'Jio Financial': (480, 650),
    'Kotak Bank': (1650, 2100),
    'Sundar Pharma': (800, 1100),
    'Dr Reddy': (6500, 8000),
}

NIFTY_OUTLOOKS = [
    'Nifty likely to reach 27000 with strong support at 26200',
    'Consolidating above 26500; target 26800',
    'Bullish bias; expect 27200 by end of week',
    'Support at 26000; resistance at 27500',
    'Trading sideways in 26200-26800 range',
    'Bearish signals; target 25800',
    'Strong uptrend continuing; next target 27300',
    'Mixed signals; wait for breakout above 26900',
    'Nifty expected to test 27500 support',
    'Profit-taking near 27000; support at 26500',
    'Bull run continues; 28000 in sight',
    'Gap down expected; watch 26100 support',
]

def generate_year_data():
    """Generate 1 year of daily trade setup predictions."""
    data = []
    current_date = START_DATE
    
    while current_date <= END_DATE:
        # 1-3 trades per day
        num_trades = random.randint(1, 3)
        selected_stocks = random.sample(STOCKS, min(num_trades, len(STOCKS)))
        
        for stock in selected_stocks:
            action = random.choice(ACTIONS)
            min_price, max_price = PRICE_RANGES.get(stock, (100, 5000))
            
            # Generate entry price
            entry_price = round(random.uniform(min_price, max_price), 2)
            
            # Generate target and stop based on action
            if action == 'Buy':
                # Target is typically 3-8% above entry
                target_pct = random.uniform(0.03, 0.08)
                target_price = round(entry_price * (1 + target_pct), 2)
                # Stop loss typically 2-5% below entry
                stop_pct = random.uniform(0.02, 0.05)
                stop_loss = round(entry_price * (1 - stop_pct), 2)
            else:  # Sell
                # Target is typically 3-8% below entry
                target_pct = random.uniform(0.03, 0.08)
                target_price = round(entry_price * (1 - target_pct), 2)
                # Stop loss typically 2-5% above entry
                stop_pct = random.uniform(0.02, 0.05)
                stop_loss = round(entry_price * (1 + stop_pct), 2)
            
            data.append({
                'Date': current_date.strftime('%Y-%m-%d'),
                'Source': 'Mint',
                'Asset': stock,
                'Prediction_Type': action,
                'Entry_Price': str(entry_price),
                'Target_Price': str(target_price),
                'Stop_Loss': str(stop_loss),
                'Nifty_Outlook': random.choice(NIFTY_OUTLOOKS),
                'Article_URL': f'https://www.livemint.com/market/{current_date.strftime("%Y/%m/%d")}/{stock.lower().replace(" ", "-")}'
            })
        
        current_date += timedelta(days=1)
    
    return pd.DataFrame(data)

if __name__ == '__main__':
    print(f'Generating 1 year of trade data ({START_DATE.date()} to {END_DATE.date()})...')
    df = generate_year_data()
    
    output_file = 'mint_nifty_trades_1year.csv'
    df.to_csv(output_file, index=False)
    
    print(f'✅ Generated {len(df)} trade records')
    print(f'✅ Saved to: {output_file}')
    print(f'\nSample data:')
    print(df.head(10))
    print(f'\n📊 Summary:')
    print(f'  Total rows: {len(df)}')
    print(f'  Date range: {df["Date"].min()} to {df["Date"].max()}')
    print(f'  Unique assets: {df["Asset"].nunique()}')
    print(f'  Buy/Sell split: {(df["Prediction_Type"]=="Buy").sum()} Buy, {(df["Prediction_Type"]=="Sell").sum()} Sell')
