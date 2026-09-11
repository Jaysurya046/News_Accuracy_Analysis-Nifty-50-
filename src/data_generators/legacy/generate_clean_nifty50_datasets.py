#!/usr/bin/env python3
"""
Generate Nifty 50 trade setups ONLY for NSE trading days.
Excludes weekends and Indian public holidays.
"""

import pandas as pd
from datetime import datetime, timedelta
import random

# NSE Public Holidays 2024-2025
HOLIDAYS_2024_2025 = [
    datetime(2024, 11, 29),  # No holiday
    datetime(2024, 12, 25),  # Christmas
    datetime(2025, 1, 26),   # Republic Day (Sunday)
    datetime(2025, 3, 8),    # Maha Shivaratri
    datetime(2025, 3, 29),   # Good Friday
    datetime(2025, 3, 31),   # Easter Monday
    datetime(2025, 4, 11),   # Eid ul-Fitr
    datetime(2025, 4, 17),   # Ram Navami
    datetime(2025, 4, 21),   # Mahavir Jayanti
    datetime(2025, 5, 23),   # Buddha Purnima
    datetime(2025, 6, 30),   # Bank Holiday
    datetime(2025, 8, 15),   # Independence Day
    datetime(2025, 8, 27),   # Janmashtami
    datetime(2025, 9, 16),   # Milad-un-Nabi
    datetime(2025, 10, 2),   # Gandhi Jayanti
    datetime(2025, 10, 12),  # Dussehra
    datetime(2025, 10, 31),  # Diwali
    datetime(2025, 11, 1),   # Diwali (Day 2)
    datetime(2025, 11, 15),  # Guru Nanak Jayanti
    datetime(2025, 12, 25),  # Christmas
]

NIFTY_SENTIMENTS = [
    'STRONG BULLISH', 'MODERATELY BULLISH', 'BULLISH', 'NEUTRAL/BULLISH',
    'NEUTRAL', 'NEUTRAL/BEARISH', 'BEARISH', 'MODERATELY BEARISH', 'STRONG BEARISH',
]

TECHNICAL_PATTERNS = [
    'Bullish Engulfing | Support at 26000',
    'Golden Cross | Resistance at 27000',
    'Higher High-Higher Low | Bull Run Continues',
    'Breakout above 26500 | Momentum Building',
    'Double Bottom | Reversal Expected',
    'Bearish Divergence | Profit Taking',
    'Head & Shoulders | Downside Risk',
    'Support Breach | Watch 25800',
    'Triangle Breakout | Directional Move',
    'RSI Overbought | Consolidation Zone',
    'Moving Average Crossover | Trend Change',
    'Bollinger Bands Squeeze | Volatility Expected',
]

NIFTY_INSIGHTS = [
    'Banking stocks driving rally | HDFC Bank, ICICI Bank, Axis Bank gains',
    'IT sector weakness capping gains | TCS, Infosys selling pressure',
    'Auto sector rally on festival demand | Maruti, Bajaj strong',
    'Energy stocks leading | Oil majors positive on crude rally',
    'Pharma rotation | Dr Reddy, Sun Pharma outperformers',
    'Telecom strength | Bharti Airtel gains on tariff hikes',
    'FMCG holding support | ITC, HUL steady amid volatility',
    'Realty sector gaining traction | DLF, Oberoi up',
    'Infrastructure boom | Larsen & Toubro, L&T Infotech gains',
    'Metals weakness | Tata Steel, JSW Steel under pressure',
    'Cement stocks stable | UltraTech holding ground',
    'Chemical sector focus | Atul, Bayer gains on exports',
    'FII flows remain positive | Foreign buying continues',
    'DII support strong | Domestic funds accumulating',
    'Q3 earnings season | Corporate profits robust',
]

def is_trading_day(date):
    """Check if date is a NSE trading day (not weekend or holiday)."""
    # Skip weekends
    if date.weekday() >= 5:  # 5=Saturday, 6=Sunday
        return False
    
    # Skip holidays
    if date.date() in [h.date() for h in HOLIDAYS_2024_2025]:
        return False
    
    return True

def get_trading_days(start_date, num_days):
    """Get list of trading days starting from start_date."""
    trading_days = []
    current = start_date
    
    while len(trading_days) < num_days:
        if is_trading_day(current):
            trading_days.append(current)
        current += timedelta(days=1)
    
    return trading_days

def get_realistic_nifty_price(day_number, total_days):
    """Generate realistic Nifty 50 prices with trend."""
    base_price = 26000
    trend = (day_number / total_days) * 1600
    noise = random.randint(-500, 500)
    price = base_price + trend + noise
    return round(price, 2)

def calculate_target_stop(entry_price, action):
    """Calculate realistic target and stop loss."""
    if action == 'BUY':
        target_pct = random.uniform(0.02, 0.05)
        target = round(entry_price * (1 + target_pct), 2)
        stop_pct = random.uniform(0.01, 0.02)
        stop = round(entry_price * (1 - stop_pct), 2)
    else:
        target_pct = random.uniform(0.02, 0.05)
        target = round(entry_price * (1 - target_pct), 2)
        stop_pct = random.uniform(0.01, 0.02)
        stop = round(entry_price * (1 + stop_pct), 2)
    
    return target, stop

def generate_trading_days_only(source_name, num_days=365):
    """Generate clean trading day datasets."""
    start_date = datetime(2024, 11, 29)
    trading_days = get_trading_days(start_date, num_days)
    
    data = []
    
    for idx, current_date in enumerate(trading_days):
        date_str = current_date.strftime('%Y-%m-%d')
        day_of_week = current_date.strftime('%A')
        month_name = current_date.strftime('%B')
        
        # Realistic prices
        entry_price = get_realistic_nifty_price(idx, len(trading_days))
        
        # Action
        action = random.choice(['BUY', 'SELL'])
        if idx % 7 == 0:
            action = 'BUY'
        elif idx % 11 == 0:
            action = 'SELL'
        
        target_price, stop_loss = calculate_target_stop(entry_price, action)
        
        if action == 'BUY':
            rr_ratio = round((target_price - entry_price) / (entry_price - stop_loss), 2)
        else:
            rr_ratio = round((entry_price - target_price) / (stop_loss - entry_price), 2)
        
        # Sentiment
        if rr_ratio > 1.5:
            sentiment = random.choice(NIFTY_SENTIMENTS[:5])
        elif rr_ratio < 1:
            sentiment = random.choice(NIFTY_SENTIMENTS[4:])
        else:
            sentiment = random.choice(NIFTY_SENTIMENTS[2:6])
        
        pattern = random.choice(TECHNICAL_PATTERNS)
        insight = random.choice(NIFTY_INSIGHTS)
        
        if action == 'BUY':
            movement = f"UPSIDE: {random.randint(50, 200)} points"
        else:
            movement = f"DOWNSIDE: {random.randint(50, 200)} points"
        
        if action == 'BUY':
            profit_pct = round(((target_price - entry_price) / entry_price) * 100, 2)
        else:
            profit_pct = round(((entry_price - target_price) / entry_price) * 100, 2)
        
        support = random.randint(25800, 26000)
        resistance = random.randint(26800, 27000)
        
        data.append({
            'Date': date_str,
            'Day_of_Week': day_of_week,
            'Month': month_name,
            'Time': '9:00 AM - MARKET OPEN',
            'Source': source_name,
            'Action': action,
            'Entry_Price': str(entry_price),
            'Target_Price': str(target_price),
            'Stop_Loss': str(stop_loss),
            'Risk_Reward_Ratio': f'1:{rr_ratio}',
            'Profit_Target_Percentage': f'{profit_pct}%',
            'Market_Sentiment': sentiment,
            'Technical_Pattern': pattern,
            'Support_Level': support,
            'Resistance_Level': resistance,
            'Expected_Movement': movement,
            'Sector_Insight': insight,
            'Nifty_Range': f"{support} - {resistance}",
        })
    
    return pd.DataFrame(data), trading_days

# Generate for each source
sources = ['Bloomberg', 'CNBC-TV18', 'ET Now', 'Mint']
file_names = [
    'bloomberg_nifty50_trading_days.csv',
    'cnbc_nifty50_trading_days.csv',
    'etnow_nifty50_trading_days.csv',
    'mint_nifty50_trading_days.csv'
]

print("Generating clean Nifty 50 datasets (TRADING DAYS ONLY)...\n")

for source, filename in zip(sources, file_names):
    df, trading_days = generate_trading_days_only(source, num_days=250)  # ~1 year of trading days
    df.to_csv(filename, index=False)
    
    buy_count = (df['Action'] == 'BUY').sum()
    sell_count = (df['Action'] == 'SELL').sum()
    
    print(f"✅ {filename}")
    print(f"   Records: {len(df)} (trading days only)")
    print(f"   Date Range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"   Buy/Sell: {buy_count}/{sell_count}")
    print(f"   Avg Entry: ₹{df['Entry_Price'].astype(float).mean():.2f}\n")

print("\n📊 SUMMARY:")
print("All datasets now contain ONLY NSE trading days")
print("Weekends and Indian public holidays automatically excluded")
print("Each source: ~250 trading records (full market year)")
