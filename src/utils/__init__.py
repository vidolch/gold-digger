"""
Utility modules for Gold Digger trading analysis system.

This package contains utility functions and helper modules for:
- Data export and formatting
- HTML report generation
- Database query examples
- Web data initialization
- General purpose utilities

These utilities support the main Gold Digger functionality by providing
common operations, data transformation, and maintenance tasks.
"""

from .export_news_html import *
from .query_example import *
from .init_web_data import *

__all__ = [
    "export_news_html",
    "query_example",
    "init_web_data"
]

# Version information
__version__ = "1.0.0"
