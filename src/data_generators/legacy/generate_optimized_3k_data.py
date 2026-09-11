#!/usr/bin/env python3
"""
Generate 1 year of data with multiple pre-market updates (6 AM - 9 AM)
and ONE trade setup per day at 9 AM market open.

Target: ~3000 total records
- Pre-market: 6-9 AM (multiple entries per day from different sources/times)
- Trade Setup: ONE at 9 AM sharp

This gives realistic multiple pre-market signals before the single daily trade recommendation.
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
SENTIMENTS = ['BULLISH', 'BEARISH', 'NEUTRAL']

PREMARKET_TIMES = [
    ('6:00 AM', 'Market Pre-Open'),
    ('6:30 AM', 'Global Market Reaction'),
    ('7:00 AM', 'FII/DII Flows'),
    ('7:30 AM', 'Technical Analysis'),
    ('8:00 AM', 'Sector Updates'),
    ('8:30 AM', 'Final Market Call'),
]

PREMARKET_HEADLINES = [
    'Global markets rally on positive cues | FII buying continues',
    'Crude oil rises | Rupee weakens against dollar',
    'Q3 earnings mixed | Banking stocks under pressure',
    'Tech stocks strong on AI optimism | IT hiring plans',
    'Monsoon rains boost agriculture sector | Food inflation eases',
    'Telecom operators hike rates | Bharti Airtel gains',
    'RBI keeps rates on hold | Inflation concerns ease',
    'Reliance Q3 profit beats estimates | Refinery margins strong',
    'HDFC Bank loan growth accelerates | NPA ratio improves',
    'Infosys wins mega deal | TCS raises guidance',
    'Asian markets rally on China stimulus | Risk appetite returns',
    'US inflation data weak | Dollar weakness supports EM',
    'Fed signals slower pace of hikes | Bond yields fall',
    'Pharma stocks rally on new approvals | Dr Reddy gains',
    'Auto sector strong on festival demand | Maruti rally',
]

GLOBAL_CUES = [
    'US Market: Positive | Fed hawkish stance eases',
    'Asia Markets: Mixed | China stimulus talks',
    'Europe: Weak | ECB keeps rates steady',
    'Crude: Up 1.5% | Geopolitical concerns',
    'FII Inflows: Strong | DII buying selective',
    'Rupee: Stable at 83.50 | Oil imports rising',
    'Bond Yields: 6.5% | Inflation cooling',
    'Dollar Index: Down 0.3% | EM flows strong',
]

SECTOR_FOCUS_OPTIONS = [
    'Banking, IT',
    'Energy, Infrastructure',
    'Pharma, FMCG',
    'Auto, Metals',
    'Telecom, Realty',
    'Textiles, Defense',
    'Chemicals, Logistics',
    'Power, Renewable',
]

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

def generate_year_data_optimized():
    """
    Generate optimized 1-year dataset:
    - Multiple pre-market updates (6 AM - 9 AM): ~4 per day
    - ONE trade setup per day at 9 AM
    
    Target: ~1460 pre-market + ~365 trades = ~1825 records
    (Can be scaled to ~3000 by adding more pre-market variations)
    """
    premarket_data = []
    trade_data = []
    
    current_date = START_DATE
    day_counter = 0
    
    while current_date <= END_DATE:
        date_str = current_date.strftime('%Y-%m-%d')
        day_counter += 1
        
        # === PRE-MARKET UPDATES (6:00 AM - 9:00 AM) ===
        # Generate 4-6 pre-market updates throughout the morning
        sentiment = random.choice(SENTIMENTS)
        global_cue = random.choice(GLOBAL_CUES)
        sector = random.choice(SECTOR_FOCUS_OPTIONS)
        headline = random.choice(PREMARKET_HEADLINES)
        
        # 4-6 pre-market entries per day (different times and angles)
        num_premarket = random.randint(4, 6)
        selected_times = random.sample(PREMARKET_TIMES, min(num_premarket, len(PREMARKET_TIMES)))
        
        for time_str, report_type in selected_times:
            premarket_data.append({
                'Date': date_str,
                'Time': time_str,
                'Source': random.choice(['Mint', 'ET Now']),
                'Report_Type': report_type,
                'Headline': headline,
                'Market_Sentiment': sentiment,
                'Global_Cues': global_cue,
                'Sector_Focus': sector,
                'Key_Update': f'Update at {time_str}: {random.choice(["FII buying", "DII selling", "Technical breakout", "Earnings reaction", "Macro data release"])}',
                'Article_URL': f'https://www.livemint.com/market/{current_date.strftime("%Y/%m/%d")}/{time_str.replace(":", "").lower()}'
            })
        
        # === SINGLE TRADE SETUP AT 9:00 AM ===
        # One recommended trade per day at market open
        stock = random.choice(STOCKS)
        action = random.choice(ACTIONS)
        min_price, max_price = PRICE_RANGES.get(stock, (100, 5000))
        
        entry_price = round(random.uniform(min_price, max_price), 2)
        
        if action == 'Buy':
            target_pct = random.uniform(0.03, 0.08)
            target_price = round(entry_price * (1 + target_pct), 2)
            stop_pct = random.uniform(0.02, 0.05)
            stop_loss = round(entry_price * (1 - stop_pct), 2)
        else:
            target_pct = random.uniform(0.03, 0.08)
            target_price = round(entry_price * (1 - target_pct), 2)
            stop_pct = random.uniform(0.02, 0.05)
            stop_loss = round(entry_price * (1 + stop_pct), 2)
        
        trade_data.append({
            'Date': date_str,
            'Time': '9:00 AM - MARKET OPEN',
            'Source': 'Mint',
            'Report_Type': 'DAILY TRADE SETUP',
            'Asset': stock,
            'Action': action,
            'Entry_Price': str(entry_price),
            'Target_Price': str(target_price),
            'Stop_Loss': str(stop_loss),
            'Risk_Reward_Ratio': f"1:{round((target_price - entry_price) / (entry_price - stop_loss) if action == 'Buy' else (entry_price - target_price) / (stop_loss - entry_price), 2)}",
            'Market_Sentiment': sentiment,
            'Supporting_Headline': headline,
            'Article_URL': f'https://www.livemint.com/market/{current_date.strftime("%Y/%m/%d")}/daily-trade-setup'
        })
        
        current_date += timedelta(days=1)
    
    return pd.DataFrame(premarket_data), pd.DataFrame(trade_data)

if __name__ == '__main__':
    print('Generating optimized 1-year dataset...')
    print('  - Pre-market updates: 6:00 AM - 9:00 AM (multiple per day)')
    print('  - Trade setups: ONE per day at 9:00 AM')
    print()
    
    premarket_df, trade_df = generate_year_data_optimized()
    
    # Save datasets
    premarket_output = 'mint_premarket_before9am.csv'
    trade_output = 'mint_daily_trade_setup_9am.csv'
    
    premarket_df.to_csv(premarket_output, index=False)
    trade_df.to_csv(trade_output, index=False)
    
    print(f'✅ Pre-market data saved: {premarket_output}')
    print(f'   Records: {len(premarket_df)}')
    print(f'   Time range: 6:00 AM - 9:00 AM')
    print(f'   Avg per day: {len(premarket_df) // 365:.1f} updates')
    print()
    print(f'✅ Trade setups saved: {trade_output}')
    print(f'   Records: {len(trade_df)}')
    print(f'   Time: 9:00 AM (ONE per day)')
    print(f'   Buy/Sell: {(trade_df["Action"]=="Buy").sum()} Buy, {(trade_df["Action"]=="Sell").sum()} Sell')
    print()
    print(f'📊 TOTAL RECORDS: {len(premarket_df) + len(trade_df)}')
    print(f'   Pre-market (6-9 AM): {len(premarket_df)}')
    print(f'   Trade setup (9 AM): {len(trade_df)}')
    print()
    
    # Sample output
    print('Sample Pre-Market Updates (first 3):')
    print(premarket_df.head(3).to_string())
    print()
    print('Sample Daily Trade Setup (first 3):')
    print(trade_df.head(3).to_string())
    print()
    print('Date range:', premarket_df['Date'].min(), 'to', premarket_df['Date'].max())
