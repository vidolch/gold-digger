"""
User Interface modules for Gold Digger trading analysis system.

This package contains various user interface implementations:
- Terminal-based command-line interface
- Text-based User Interface (TUI) using Textual
- News viewer and interactive components
- Launcher utilities

Each UI module provides a different way to interact with the Gold Digger
core functionality, from simple command-line operations to rich interactive
terminal applications.
"""

from .terminal import *
from .news_viewer import *

__all__ = [
    "terminal",
    "tui",
    "news_viewer",
    "tui_launcher"
]

# Version information
__version__ = "1.0.0"
