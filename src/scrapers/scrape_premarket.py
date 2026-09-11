#!/usr/bin/env python3
"""
scrape_premarket.py

Scrapes pre-market data and early morning market articles.
Fetches data from financial news sources before market open (6 AM - 9:30 AM IST).

Usage:
  python scrape_premarket.py --output premarket_data.csv
  python scrape_premarket.py --days 7 --output premarket_week.csv
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import re
import time
import argparse
import sys

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Pre-market sources to scrape
PREMARKET_SOURCES = {
    'Mint': 'https://www.livemint.com/market',
    'ET Now': 'https://www.etnownews.com/markets',
    'Bloomberg': 'https://www.bloomberg.com/markets',
    'Economic Times': 'https://economictimes.indiatimes.com/markets',
}

def extract_premarket_sentiment(text):
    """Extract market sentiment from pre-market articles."""
    text_lower = text.lower()
    
    # Sentiment scoring
    bullish_keywords = ['bullish', 'strong', 'surge', 'rally', 'jump', 'gain', 'upsurge', 'surge', 'climb', 'positive']
    bearish_keywords = ['bearish', 'weak', 'decline', 'fall', 'loss', 'downturn', 'slump', 'slide', 'negative', 'pressure']
    
    bullish_count = sum(1 for kw in bullish_keywords if kw in text_lower)
    bearish_count = sum(1 for kw in bearish_keywords if kw in text_lower)
    
    if bullish_count > bearish_count:
        sentiment = 'BULLISH'
    elif bearish_count > bullish_count:
        sentiment = 'BEARISH'
    else:
        sentiment = 'NEUTRAL'
    
    return sentiment

def extract_global_cues(text):
    """Extract global market cues (US, Asia, Europe)."""
    cues = []
    
    # Look for US market mentions
    if re.search(r'(dow|nasdaq|s&p|wall street|us market)', text, re.IGNORECASE):
        if re.search(r'(up|positive|gain|surge)', text, re.IGNORECASE):
            cues.append('US: Positive')
        elif re.search(r'(down|negative|fall|decline)', text, re.IGNORECASE):
            cues.append('US: Negative')
    
    # Look for Asia market mentions
    if re.search(r'(shanghai|hong kong|tokyo|asia)', text, re.IGNORECASE):
        if re.search(r'(up|positive|gain)', text, re.IGNORECASE):
            cues.append('Asia: Positive')
        elif re.search(r'(down|negative|fall)', text, re.IGNORECASE):
            cues.append('Asia: Negative')
    
    # Look for Europe market mentions
    if re.search(r'(london|paris|europe|ftse|dax|cac)', text, re.IGNORECASE):
        if re.search(r'(up|positive|gain)', text, re.IGNORECASE):
            cues.append('Europe: Positive')
        elif re.search(r'(down|negative|fall)', text, re.IGNORECASE):
            cues.append('Europe: Negative')
    
    return ' | '.join(cues) if cues else 'No global cues'

def extract_sector_focus(text):
    """Extract which sectors are in focus."""
    sectors = []
    sector_keywords = {
        'Banking': ['bank', 'npa', 'credit', 'deposit', 'lending'],
        'IT': ['it', 'tech', 'software', 'infosys', 'tcs', 'wipro', 'hcl'],
        'Energy': ['oil', 'gas', 'power', 'coal', 'renewable', 'ntpc'],
        'Pharma': ['pharma', 'drug', 'medical', 'healthcare'],
        'Auto': ['auto', 'automobile', 'two-wheeler', 'maruti', 'bajaj'],
        'Telecom': ['telecom', 'jio', 'airtel', 'vodafone', '5g'],
        'Metals': ['steel', 'metal', 'mining', 'aluminium', 'copper'],
    }
    
    for sector, keywords in sector_keywords.items():
        if any(kw in text.lower() for kw in keywords):
            sectors.append(sector)
    
    return ', '.join(sectors) if sectors else 'General'

def scrape_mint_premarket(date_str, session):
    """Scrape Mint pre-market section."""
    url = f"https://www.livemint.com/market"
    try:
        r = session.get(url, timeout=12)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            # Find pre-market / market open articles
            articles = soup.find_all('a', limit=10)
            if articles:
                # Get first article text
                first_article = articles[0]
                text = first_article.get_text()
                return {
                    'Headline': text[:100],
                    'Sentiment': extract_premarket_sentiment(text),
                    'URL': first_article.get('href', '')
                }
    except Exception as e:
        print(f"Error scraping Mint: {e}")
    
    return None

def scrape_et_now_premarket(date_str, session):
    """Scrape ET Now pre-market section."""
    url = "https://www.etnownews.com/markets"
    try:
        r = session.get(url, timeout=12)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            articles = soup.find_all('a', limit=10)
            if articles:
                first_article = articles[0]
                text = first_article.get_text()
                return {
                    'Headline': text[:100],
                    'Sentiment': extract_premarket_sentiment(text),
                    'URL': first_article.get('href', '')
                }
    except Exception as e:
        print(f"Error scraping ET Now: {e}")
    
    return None

def generate_premarket_report(dates, output_file, delay=2):
    """Generate pre-market reports for given dates."""
    data = []
    session = requests.Session()
    session.headers.update({'User-Agent': DEFAULT_USER_AGENT})
    
    for date in dates:
        date_str = date.strftime('%Y-%m-%d')
        print(f"\n[{date_str}] Fetching pre-market data...")
        
        # Fetch from Mint
        mint_data = scrape_mint_premarket(date_str, session)
        if mint_data:
            data.append({
                'Date': date_str,
                'Time': '6:00-9:30 AM',
                'Source': 'Mint',
                'Headline': mint_data['Headline'],
                'Market_Sentiment': mint_data['Sentiment'],
                'Global_Cues': 'Awaiting market open',
                'Sector_Focus': 'General',
                'Expected_Movement': 'TBD',
                'Article_URL': mint_data['URL']
            })
            print(f"  ✓ Mint: {mint_data['Sentiment']}")
        
        time.sleep(delay)
        
        # Fetch from ET Now
        et_data = scrape_et_now_premarket(date_str, session)
        if et_data:
            data.append({
                'Date': date_str,
                'Time': '6:00-9:30 AM',
                'Source': 'ET Now',
                'Headline': et_data['Headline'],
                'Market_Sentiment': et_data['Sentiment'],
                'Global_Cues': 'Awaiting market open',
                'Sector_Focus': 'General',
                'Expected_Movement': 'TBD',
                'Article_URL': et_data['URL']
            })
            print(f"  ✓ ET Now: {et_data['Sentiment']}")
        
        time.sleep(delay)
    
    # Save to CSV
    if data:
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False)
        print(f"\n✅ Pre-market report saved: {output_file}")
        print(f"   Total records: {len(data)}")
        return df
    else:
        print("\n⚠ No pre-market data fetched")
        return None

def generate_demo_premarket(days=7):
    """Generate demo pre-market data for testing."""
    data = []
    sentiments = ['BULLISH', 'BEARISH', 'NEUTRAL']
    global_cues_list = [
        'US: Positive | Asia: Positive',
        'US: Negative | Asia: Mixed',
        'Europe: Positive | Commodities: Rising',
        'FII Inflows positive | Global yield easing',
        'Crude Oil up 1% | Dollar Index down 0.5%'
    ]
    sector_focus_list = ['Banking, IT', 'Energy, Pharma', 'Auto, Telecom', 'Metals, Pharma', 'General']
    
    end_date = datetime.now().date()
    for i in range(days):
        date = end_date - timedelta(days=i)
        
        for source in ['Mint', 'ET Now']:
            data.append({
                'Date': date.strftime('%Y-%m-%d'),
                'Time': '6:00-9:30 AM',
                'Source': source,
                'Headline': f'{source} Pre-Market Report for {date.strftime("%B %d, %Y")}',
                'Market_Sentiment': sentiments[i % len(sentiments)],
                'Global_Cues': global_cues_list[i % len(global_cues_list)],
                'Sector_Focus': sector_focus_list[i % len(sector_focus_list)],
                'Expected_Movement': f'Nifty expected to move 50-100 points {"UP" if (i % 2 == 0) else "DOWN"}',
                'Article_URL': f'https://www.livemint.com/market/{date.strftime("%Y/%m/%d")}/premarket'
            })
    
    return pd.DataFrame(data)

def parse_args():
    p = argparse.ArgumentParser(description='Scrape pre-market and early morning market data')
    p.add_argument('--days', type=int, help='Number of days to fetch (default: 7)', default=7)
    p.add_argument('--output', help='Output CSV file', default='premarket_data.csv')
    p.add_argument('--demo-only', action='store_true', help='Use demo data instead of live scraping')
    p.add_argument('--delay', type=float, help='Delay between requests (seconds)', default=2.0)
    return p.parse_args()

def main():
    args = parse_args()
    
    if args.demo_only:
        print(f"Generating demo pre-market data for last {args.days} days...")
        df = generate_demo_premarket(days=args.days)
        df.to_csv(args.output, index=False)
        print(f"✅ Demo data saved to {args.output}")
        print(df.head(10))
        return
    
    # Generate date range
    end_date = datetime.now().date()
    dates = [end_date - timedelta(days=i) for i in range(args.days)]
    
    print(f"Fetching pre-market data for {args.days} days...")
    df = generate_premarket_report(dates, args.output, delay=args.delay)
    
    if df is not None:
        print("\nSample data:")
        print(df.head())

if __name__ == '__main__':
    main()
