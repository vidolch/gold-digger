"""
Gold Digger - Professional Gold Trading Analysis System

A comprehensive suite for gold price analysis, news sentiment tracking,
and automated trading recommendations.

This package contains the core modules for:
- Data fetching and processing
- News analysis and sentiment tracking
- Trading signal generation
- User interfaces (Terminal, TUI, Web)
"""

__version__ = "1.0.0"
__author__ = "Gold Digger Development Team"
__license__ = "MIT"

# Core imports for easy access
from .core.gold_fetcher import GoldPriceFetcher
from .core.news_fetcher import GoldNewsFetcher
from .core.news_analyzer import GoldNewsAnalyzer
from .core.trading_analyzer import TradingAnalyzer

__all__ = [
    "GoldPriceFetcher",
    "GoldNewsFetcher",
    "GoldNewsAnalyzer",
    "TradingAnalyzer"
]
