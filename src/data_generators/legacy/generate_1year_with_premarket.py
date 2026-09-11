#!/usr/bin/env python3
"""
Generate 1 year of trade data with pre-market and early morning article data.
Combines intraday trade setups with early morning market sentiment and global cues.
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

GLOBAL_CUES = [
    'US Market Positive | Fed rates stable | Oil down 0.5%',
    'FII flows strong into India | Asia markets rallying',
    'European markets weak | Dollar index rising',
    'Crude oil up 2% | Dollar down 0.3%',
    'US inflation data mixed | Market cautious',
    'Tech stocks weak in US | But IT outlook positive',
    'Monsoon rains strong | Agriculture sector focus',
    'Q3 earnings season starts | Banking stocks in focus',
    'Global trade tensions ease | Risk-on sentiment',
    'China stimulus talks | Commodity prices rise',
]

SECTOR_FOCUS = [
    'Banking, IT',
    'Energy, Infrastructure',
    'Pharma, FMCG',
    'Auto, Metals',
    'Telecom, Realty',
    'Textiles, Defense',
    'Chemicals, Logistics',
    'Power, Renewable Energy',
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

def generate_year_data_with_premarket():
    """Generate 1 year of daily data with pre-market insights and trade setups."""
    trade_data = []
    premarket_data = []
    
    current_date = START_DATE
    
    while current_date <= END_DATE:
        date_str = current_date.strftime('%Y-%m-%d')
        
        # === PRE-MARKET DATA (6:00-9:30 AM) ===
        # Generate one pre-market report per day
        sentiment = random.choice(SENTIMENTS)
        global_cue = random.choice(GLOBAL_CUES)
        sector_focus = random.choice(SECTOR_FOCUS)
        
        # Determine expected opening movement based on sentiment
        if sentiment == 'BULLISH':
            expected_move = random.choice(['Nifty may open positive | Up 50-150 points', 'Strong opening expected | Buying momentum likely'])
        elif sentiment == 'BEARISH':
            expected_move = random.choice(['Nifty may open negative | Down 50-150 points', 'Weak opening expected | Profit-taking likely'])
        else:
            expected_move = 'Mixed signals | Range-bound opening expected'
        
        # Pre-market record for Mint
        premarket_data.append({
            'Date': date_str,
            'Time': '6:00-9:30 AM',
            'Source': 'Mint',
            'Report_Type': 'Pre-Market Update',
            'Market_Sentiment': sentiment,
            'Global_Cues': global_cue,
            'Sector_Focus': sector_focus,
            'Expected_Opening': expected_move,
            'Key_Triggers': 'Awaiting results, macro data, corporate news',
            'Article_URL': f'https://www.livemint.com/market/{current_date.strftime("%Y/%m/%d")}/premarket'
        })
        
        # Pre-market record for ET Now
        premarket_data.append({
            'Date': date_str,
            'Time': '6:00-9:30 AM',
            'Source': 'ET Now',
            'Report_Type': 'Market Open Analysis',
            'Market_Sentiment': sentiment,
            'Global_Cues': global_cue,
            'Sector_Focus': sector_focus,
            'Expected_Opening': expected_move,
            'Key_Triggers': 'Global market reaction, FIIs, DII flows',
            'Article_URL': f'https://www.etnownews.com/markets/{current_date.strftime("%Y/%m/%d")}/premarket'
        })
        
        # === INTRADAY TRADE SETUPS (9:30 AM onwards) ===
        # 1-3 trades per day
        num_trades = random.randint(1, 3)
        selected_stocks = random.sample(STOCKS, min(num_trades, len(STOCKS)))
        
        for stock in selected_stocks:
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
                'Time': '9:30 AM - Market Open',
                'Source': 'Mint',
                'Data_Type': 'Intraday Trade Setup',
                'Asset': stock,
                'Action': action,
                'Entry_Price': str(entry_price),
                'Target_Price': str(target_price),
                'Stop_Loss': str(stop_loss),
                'Market_Sentiment': sentiment,  # Link to pre-market sentiment
                'Article_URL': f'https://www.livemint.com/market/{current_date.strftime("%Y/%m/%d")}/{stock.lower().replace(" ", "-")}'
            })
        
        current_date += timedelta(days=1)
    
    return pd.DataFrame(trade_data), pd.DataFrame(premarket_data)

if __name__ == '__main__':
    print('Generating 1 year of data with pre-market insights...')
    
    trade_df, premarket_df = generate_year_data_with_premarket()
    
    # Save both datasets
    trade_output = 'mint_nifty_trades_1year_with_premarket.csv'
    premarket_output = 'mint_premarket_1year.csv'
    
    trade_df.to_csv(trade_output, index=False)
    premarket_df.to_csv(premarket_output, index=False)
    
    print(f'✅ Trade setups saved: {trade_output} ({len(trade_df)} records)')
    print(f'✅ Pre-market data saved: {premarket_output} ({len(premarket_df)} records)')
    
    print(f'\n📊 Trade Data Summary:')
    print(f'   Date range: {trade_df["Date"].min()} to {trade_df["Date"].max()}')
    print(f'   Unique assets: {trade_df["Asset"].nunique()}')
    print(f'   Buy/Sell split: {(trade_df["Action"]=="Buy").sum()} Buy, {(trade_df["Action"]=="Sell").sum()} Sell')
    print(f'   Sentiments: Bullish={len(trade_df[trade_df["Market_Sentiment"]=="BULLISH"])}, Bearish={len(trade_df[trade_df["Market_Sentiment"]=="BEARISH"])}, Neutral={len(trade_df[trade_df["Market_Sentiment"]=="NEUTRAL"])}')
    
    print(f'\n📊 Pre-Market Data Summary:')
    print(f'   Date range: {premarket_df["Date"].min()} to {premarket_df["Date"].max()}')
    print(f'   Sources: {premarket_df["Source"].unique().tolist()}')
    print(f'   Total reports: {len(premarket_df)}')
    
    print(f'\nSample Trade Data:')
    print(trade_df.head(5))
    print(f'\nSample Pre-Market Data:')
    print(premarket_df.head(5))
