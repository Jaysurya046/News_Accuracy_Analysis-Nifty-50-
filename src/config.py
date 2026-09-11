"""
Centralized configuration and path management for Quant-Trading project.
Provides canonical paths across all modules to ensure reliable script execution.
"""
from pathlib import Path
import os
import sys
import glob

# Ensure UTF-8 output encoding for Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Project Root Directory
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent

# Data Directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
SOURCES_1Y_DIR = DATA_DIR / "sources_1year"
SOURCES_3Y_DIR = DATA_DIR / "sources_3year"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Model & Metrics Directory
MODELS_DIR = PROJECT_ROOT / "models"

# Reports & Visualizations
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
TEXT_REPORTS_DIR = REPORTS_DIR / "text"
COMPARISON_REPORTS_DIR = REPORTS_DIR / "comparison_reports"

# Canonical Files
NIFTY_FILENAME = "NIFTY_50-29-11-2024-to-29-11-2025_csv__NIFTY_50-29-11-2024-to-29-11-20.csv"
NIFTY_FILE = RAW_DATA_DIR / NIFTY_FILENAME
ALL_NEWS_FILE = RAW_DATA_DIR / "all_news_articles_2023_2025.csv"

# Web Scraper Headers & API Settings
API_KEYS = {}
HOST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def ensure_dirs():
    """Ensure all required output directories exist."""
    for d in [RAW_DATA_DIR, SOURCES_1Y_DIR, SOURCES_3Y_DIR, PROCESSED_DATA_DIR,
              MODELS_DIR, FIGURES_DIR, TEXT_REPORTS_DIR, COMPARISON_REPORTS_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def find_file(filename: str) -> Path:
    """Find a file in the project by searching standard locations with fallback."""
    search_dirs = [
        PROCESSED_DATA_DIR,
        RAW_DATA_DIR,
        SOURCES_1Y_DIR,
        SOURCES_3Y_DIR,
        FIGURES_DIR,
        TEXT_REPORTS_DIR,
        MODELS_DIR,
        COMPARISON_REPORTS_DIR,
        PROJECT_ROOT
    ]
    for d in search_dirs:
        candidate = d / filename
        if candidate.exists():
            return candidate
    return PROCESSED_DATA_DIR / filename

def get_nifty_file() -> Path:
    """Get path to the NIFTY ground truth file."""
    if NIFTY_FILE.exists():
        return NIFTY_FILE
    root_fallback = PROJECT_ROOT / NIFTY_FILENAME
    if root_fallback.exists():
        return root_fallback
    return NIFTY_FILE

def get_1year_sources():
    """Return sorted list of Path objects for 1-year source CSVs."""
    files = sorted(list(SOURCES_1Y_DIR.glob("*_1year.csv")))
    if not files:
        files = sorted(list(PROJECT_ROOT.glob("*_1year.csv")))
    return files

def get_3year_sources():
    """Return sorted list of Path objects for 3-year source CSVs."""
    files = sorted(list(SOURCES_3Y_DIR.glob("*_3year.csv")))
    if not files:
        files = sorted(list(PROJECT_ROOT.glob("*_3year.csv")))
    return files

# Auto-ensure directories on import
ensure_dirs()
