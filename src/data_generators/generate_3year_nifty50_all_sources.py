#!/usr/bin/env python3
"""
Generate 3 years of Nifty 50 trade setups for all 10 news sources.
Excludes weekends and Indian public holidays (2024-2026).
~750-760 trading days per source = ~7,500 total records.
"""

import pandas as pd
from datetime import datetime, timedelta
import random
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.config import SOURCES_3Y_DIR
except ImportError:
    from config import SOURCES_3Y_DIR

# NSE Public Holidays 2024-2026
HOLIDAYS_2024_2026 = [
    # 2024
    datetime(2024, 12, 25),  # Christmas
    # 2025
    datetime(2025, 1, 26),   # Republic Day (Sunday - skip)
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
    # 2026
    datetime(2026, 1, 26),   # Republic Day
    datetime(2026, 3, 25),   # Holi
    datetime(2026, 3, 29),   # Good Friday (Sunday)
    datetime(2026, 4, 2),    # Ram Navami
    datetime(2026, 4, 10),   # Mahavir Jayanti
    datetime(2026, 4, 14),   # Ambedkar Jayanti
    datetime(2026, 5, 15),   # Eid ul-Fitr
    datetime(2026, 5, 26),   # Buddha Purnima
    datetime(2026, 7, 17),   # Muharram
    datetime(2026, 8, 15),   # Independence Day
    datetime(2026, 9, 2),    # Janmashtami
    datetime(2026, 10, 2),   # Gandhi Jayanti
    datetime(2026, 10, 5),   # Dussehra
    datetime(2026, 10, 24),  # Diwali
    datetime(2026, 11, 11),  # Guru Nanak Jayanti
    datetime(2026, 12, 25),  # Christmas
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
    """Check if date is NSE trading day."""
    if date.weekday() >= 5:  # Saturday=5, Sunday=6
        return False
    if date in HOLIDAYS_2024_2026:
        return False
    return True

def get_trading_days(start_date, num_days):
    """Get list of trading days."""
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
    trend = (day_number / total_days) * 2400  # Trend over 3 years
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

def generate_nifty_setups_3yr(source_name, num_days=750):
    """Generate 3-year Nifty 50 trade setups for a source."""
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

# Sources
sources = [
    ('Bloomberg', 'bloomberg_nifty50.csv'),
    ('CNBC-TV18', 'cnbc_nifty50.csv'),
    ('ET Now', 'etnow_nifty50.csv'),
    ('Mint', 'mint_nifty50.csv'),
    ('NDTV Profit', 'ndtvprofit_nifty50.csv'),
    ('Times Now Business', 'timesnowbusiness_nifty50.csv'),
    ('India Today Business', 'indiatodaybusiness_nifty50.csv'),
    ('Money Control', 'moneycontrol_nifty50.csv'),
    ('Financial Express', 'financialexpress_nifty50.csv'),
    ('Economic Times Live', 'economictimeslive_nifty50.csv'),
]

print("Generating 3-year Nifty 50 trade setups (no weekends/holidays)...\n")

total_records = 0

for source_name, filename in sources:
    df, trading_days = generate_nifty_setups_3yr(source_name, num_days=750)
    filepath = os.path.join(SOURCES_3Y_DIR, filename)
    df.to_csv(filepath, index=False)
    
    buy_count = (df['Action'] == 'BUY').sum()
    sell_count = (df['Action'] == 'SELL').sum()
    
    print(f"✅ {filename}")
    print(f"   Records: {len(df)} trading days (3 years)")
    print(f"   Date Range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"   Buy/Sell: {buy_count}/{sell_count}\n")
    
    total_records += len(df)

print("=" * 70)
print(f"🎯 COMPLETE 3-YEAR PORTFOLIO (10 SOURCES)")
print("=" * 70)
print(f"Total records: {total_records} (avg {total_records//10} per source)")
print(f"Total sources: 10 major Indian financial news channels")
print(f"Trading days per source: ~750 (3 years, no weekends/holidays)")
print("=" * 70)
