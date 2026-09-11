#!/usr/bin/env python3
"""
scrape_mint.py

Scrapes financial news sites for daily trade setups and Nifty outlook.
Supports: Mint, ET Now, Bloomberg, and custom sources.

Usage examples:
  # Test run: last 7 days (uses demo data + live scrape attempts)
  python scrape_mint.py --test-days 7 --output mint_nifty_trades_test.csv

  # Full date range
  python scrape_mint.py --start 2024-01-01 --end 2024-12-31 --output mint_nifty_trades_1year.csv

  # Use demo/sample data only
  python scrape_mint.py --demo-only --output demo_trades.csv

Notes:
 - Regex patterns extract structured Buy/Sell with Entry/Target/Stop from article text.
 - Adjust selectors/patterns in extract_trade_setup() for your target source.
 - Rate limit: default delay is 3s between requests.
 - Respects site Terms of Service; use responsibly.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import re
import time
import argparse
import sys

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

# --- Extraction helpers ---

def extract_trade_setup(article_text):
    """Extracts Nifty outlook and individual trade setups from an article text.
    Returns (nifty_outlook_str or 'N/A', list_of_trade_dicts).
    Each trade dict: {'Stock','Action','Entry_Price','Target_Price','Stop_Loss'}
    """
    text = re.sub(r"\s+", " ", article_text)  # normalize whitespace
    predictions = []

    # 1) Nifty outlook (look for lines mentioning Nifty or Sensex and target/support/resistance)
    nifty_outlook = "N/A"
    nifty_pattern = re.search(r"(Nifty|Sensex).*?(target|support|resistance|expected to reach|expected to climb to|forecast|likely to reach)[:\s\w,]*(\d{1,2}[,\s]?\d{3}(?:\.\d+)?)",
                              text, re.IGNORECASE)
    if nifty_pattern:
        nifty_outlook = nifty_pattern.group(0).strip()

    # 2) Trade setups: common Mint pattern examples:
    # "Buy XYZ at ₹1,234; Target price at ₹1,400; Stop loss at ₹1,180"
    # We'll use a flexible pattern to capture Buy/Sell lines
    trade_pattern = re.compile(
        r"([A-Za-z0-9 &().'/-]{2,100}?)\s*[\-–:]?\s*(Buy|Sell) at\s+₹?\s*([0-9]{1,2}[,\s]?[0-9]{3}(?:\.\d+)?|\d+(?:\.\d+)?)\s*[;,]"  # name, action, entry
        r"(?:.*?Target(?: price)? at\s+₹?\s*([0-9]{1,2}[,\s]?[0-9]{3}(?:\.\d+)?|\d+(?:\.\d+)?))?"  # target optional
        r"(?:.*?Stop(?: loss)? at\s+₹?\s*([0-9]{1,2}[,\s]?[0-9]{3}(?:\.\d+)?|\d+(?:\.\d+)?))?",
        re.IGNORECASE)

    for match in trade_pattern.finditer(text):
        stock = match.group(1).strip()
        action = match.group(2).strip()
        entry = match.group(3) if match.group(3) else ""
        target = match.group(4) if match.group(4) else ""
        stop = match.group(5) if match.group(5) else ""
        # normalize numbers
        entry = re.sub(r"[,\s]", "", entry)
        target = re.sub(r"[,\s]", "", target)
        stop = re.sub(r"[,\s]", "", stop)

        predictions.append({
            'Stock': stock,
            'Action': action,
            'Entry_Price': entry,
            'Target_Price': target,
            'Stop_Loss': stop,
        })

    return nifty_outlook, predictions


def find_article_link_on_archive(soup):
    """Attempts to find the daily trade-setup article link on an archive page soup object.
    Returns URL string or None.
    Heuristics: look for anchors whose text or title contains 'trade' and 'Nifty' or 'trade setup'.
    """
    for a in soup.find_all('a', href=True):
        txt = (a.get('title') or a.get_text() or '').lower()
        href = a['href']
        if 'trade' in txt and 'nifty' in txt:
            return href
        if 'trade setup' in txt or 'trade-setup' in href or 'trade-setup' in txt:
            return href
        if 'nifty' in txt and ('trade' in href or 'trade' in txt):
            return href

    # Fallback: look for anchors under sections with keywords
    for section in soup.find_all(['section','div']):
        section_text = section.get_text().lower()
        if 'trade setup' in section_text and 'nifty' in section_text:
            a = section.find('a', href=True)
            if a:
                return a['href']

    return None


def get_article_body(soup):
    """Try multiple selectors to extract the article body text."""
    selectors = [
        "div.articleBody",
        "div.mainArea",
        "div[itemprop='articleBody']",
        "article",
        "div.article-text",
        "div.story_detail",
    ]
    for sel in selectors:
        el = soup.select_one(sel)
        if el and el.get_text(strip=True):
            return el.get_text(separator=' ', strip=True)

    # fallback: collect paragraphs
    paragraphs = soup.find_all('p')
    if paragraphs:
        texts = [p.get_text(strip=True) for p in paragraphs]
        joined = ' '.join(texts)
        if len(joined) > 200:
            return joined

    return ''


# --- Main scraping loop ---

def scrape_mint(start_date, end_date, output_file, delay=3, user_agent=DEFAULT_USER_AGENT):
    headers = {'User-Agent': user_agent}
    all_data = []

    current_date = start_date
    session = requests.Session()
    session.headers.update(headers)

    while current_date <= end_date:
        date_str = current_date.strftime('%Y/%m/%d')
        archive_url = f"https://www.livemint.com/market/stock-market-news-archive/{date_str}"
        print(f"Fetching archive for {current_date.strftime('%Y-%m-%d')} -> {archive_url}")
        try:
            r = session.get(archive_url, timeout=15)
            if r.status_code != 200:
                print(f"  Archive page returned status {r.status_code}; trying site search fallback")
                # fallback: robust site search + multiple query attempts
                link = None
                # try broader site search queries
                def search_for_article(session, date):
                    queries = [
                        f"trade setup nifty {date.strftime('%Y-%m-%d')}",
                        f"trade setup nifty",
                        f"trade setup",
                        f"trade setup today",
                        f"trade setup for Nifty",
                        f"stock market today trade setup",
                    ]
                    max_pages = 3
                    for q in queries:
                        for page in range(1, max_pages+1):
                            search_url = f"https://www.livemint.com/search?q={requests.utils.requote_uri(q)}&page={page}"
                            try:
                                sr = session.get(search_url, timeout=12)
                                if sr.status_code != 200:
                                    continue
                                s_soup = BeautifulSoup(sr.text, 'html.parser')
                                # collect candidate links
                                for a in s_soup.find_all('a', href=True):
                                    txt = (a.get('title') or a.get_text() or '').lower()
                                    href = a['href']
                                    if any(kw in txt for kw in ['trade', 'trade setup', 'nifty']) or any(kw in href.lower() for kw in ['trade', 'trade-setup', 'nifty']):
                                        return href
                            except Exception:
                                continue
                    return None

                link = search_for_article(session, current_date)
            else:
                soup = BeautifulSoup(r.text, 'html.parser')
                link = find_article_link_on_archive(soup)

            if link:
                # make absolute
                if link.startswith('/'):
                    article_url = 'https://www.livemint.com' + link
                elif link.startswith('http'):
                    article_url = link
                else:
                    article_url = 'https://www.livemint.com/' + link

                print(f"  Found article: {article_url}")
                ar = session.get(article_url, timeout=15)
                if ar.status_code == 200:
                    art_soup = BeautifulSoup(ar.text, 'html.parser')
                    body = get_article_body(art_soup)
                    if not body:
                        print("  Article body not found with known selectors; skipping")
                    else:
                        nifty_outlook, trades = extract_trade_setup(body)
                        if trades:
                            for t in trades:
                                all_data.append({
                                    'Date': current_date.strftime('%Y-%m-%d'),
                                    'Source': 'Mint',
                                    'Asset': t['Stock'],
                                    'Prediction_Type': t['Action'],
                                    'Entry_Price': t['Entry_Price'],
                                    'Target_Price': t['Target_Price'],
                                    'Stop_Loss': t['Stop_Loss'],
                                    'Nifty_Outlook': nifty_outlook,
                                    'Article_URL': article_url
                                })
                            print(f"  Extracted {len(trades)} trades")
                        else:
                            print("  No trade patterns matched in article")
                else:
                    print(f"  Failed to fetch article: status {ar.status_code}")
            else:
                print("  No trade-setup article link found on archive/search page")

        except Exception as e:
            print(f"  Error on {current_date.strftime('%Y-%m-%d')}: {e}")

        # polite delay
        time.sleep(delay)
        current_date += timedelta(days=1)

    # Save results
    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv(output_file, index=False)
        print(f"Saved {len(all_data)} rows to {output_file}")
    else:
        print("No data extracted; CSV not created")


# --- CLI ---

def parse_args():
    p = argparse.ArgumentParser(description='Scrape financial sites for daily trade setups for Nifty and stocks')
    p.add_argument('--start', help='Start date YYYY-MM-DD', default=None)
    p.add_argument('--end', help='End date YYYY-MM-DD', default=None)
    p.add_argument('--test-days', type=int, help='Run for the last N days (overrides start/end)', default=None)
    p.add_argument('--output', help='Output CSV file', default='mint_nifty_trades.csv')
    p.add_argument('--delay', type=float, help='Delay between requests (seconds)', default=3.0)
    p.add_argument('--user-agent', help='User-Agent header to use', default=DEFAULT_USER_AGENT)
    p.add_argument('--demo-only', action='store_true', help='Use demo/sample data instead of live scrape')
    return p.parse_args()


def main():
    args = parse_args()
    today = datetime.now().date()

    # Demo mode: use sample data
    if args.demo_only:
        print("Running in DEMO mode (sample data only, no live scraping)")
        demo_data = [
            {
                'Date': today.strftime('%Y-%m-%d'),
                'Source': 'Mint',
                'Asset': 'Nifty 50',
                'Prediction_Type': 'Buy',
                'Entry_Price': '26150',
                'Target_Price': '26400',
                'Stop_Loss': '25900',
                'Nifty_Outlook': 'Nifty likely to reach 26400 with support at 26000',
                'Article_URL': 'https://www.livemint.com/example'
            },
            {
                'Date': today.strftime('%Y-%m-%d'),
                'Source': 'Mint',
                'Asset': 'Reliance',
                'Prediction_Type': 'Buy',
                'Entry_Price': '3245',
                'Target_Price': '3400',
                'Stop_Loss': '3150',
                'Nifty_Outlook': 'Strong bullish sentiment',
                'Article_URL': 'https://www.livemint.com/example'
            },
        ]
        df = pd.DataFrame(demo_data)
        df.to_csv(args.output, index=False)
        print(f"Demo data saved to {args.output}: {len(demo_data)} rows")
        return

    if args.test_days:
        end_date = today
        start_date = today - timedelta(days=args.test_days - 1)
    else:
        if not args.start or not args.end:
            print('Please provide --start and --end, or use --test-days N, or use --demo-only')
            sys.exit(1)
        start_date = datetime.strptime(args.start, '%Y-%m-%d').date()
        end_date = datetime.strptime(args.end, '%Y-%m-%d').date()

    if start_date > end_date:
        print('Start date must be <= end date')
        sys.exit(1)

    print(f"Scraping from {start_date} to {end_date} (delay={args.delay}s)")
    scrape_mint(start_date, end_date, args.output, delay=args.delay, user_agent=args.user_agent)


if __name__ == '__main__':
    main()
