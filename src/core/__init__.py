"""
Core modules for Gold Digger trading analysis system.

This package contains the fundamental components for:
- Gold price data fetching and caching
- News data collection and processing
- Sentiment analysis and market intelligence
- Trading signal generation and analysis

All core modules are designed to work independently while sharing
common database and configuration infrastructure.
"""

from .gold_fetcher import GoldPriceFetcher
from .news_fetcher import GoldNewsFetcher
from .news_analyzer import GoldNewsAnalyzer
from .trading_analyzer import TradingAnalyzer

__all__ = [
    "GoldPriceFetcher",
    "GoldNewsFetcher",
    "GoldNewsAnalyzer",
    "TradingAnalyzer"
]

# Version information
__version__ = "1.0.0"
