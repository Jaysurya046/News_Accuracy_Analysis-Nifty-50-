import pandas as pd
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.config import ALL_NEWS_FILE, find_file
except ImportError:
    from config import ALL_NEWS_FILE, find_file

news_path = find_file('all_news_articles_2023_2025.csv')
df = pd.read_csv(news_path)

print("="*80)
print("NEWS ARTICLES SUMMARY")
print("="*80)
print(f"Total Articles: {len(df)}")
print(f"Date Range: {df['date'].min()} to {df['date'].max()}")
print(f"\nArticles by Source:")
print(df['source'].value_counts())
print(f"\nAverage Content Length: {df['content_length'].mean():.0f} words")
print(f"Min/Max Content Length: {df['content_length'].min()} / {df['content_length'].max()} words")

print("\n" + "="*80)
print("SAMPLE ARTICLES (First 10)")
print("="*80)
for idx, row in df.head(10).iterrows():
    print(f"\n[{idx+1}] Date: {row['date']} | Source: {row['source']}")
    print(f"    Topic: {row['topic']}")
    print(f"    Content: {row['content'][:150]}...")
    print(f"    Length: {row['content_length']} words")

print("\n" + "="*80)
print(f"File size: {df.memory_usage(deep=True).sum() / 1024:.2f} KB")
print("="*80)
