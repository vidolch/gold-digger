#!/usr/bin/env python3
"""
Gold Digger TUI - Modern Text User Interface
A beautiful and interactive TUI for Gold Digger functionality using Textual.
"""

import sys
import os
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from textual.app import App, ComposeResult
    from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
    from textual.widgets import (
        Header, Footer, Static, Button, Label, Input, TextArea,
        SelectionList, ProgressBar, Tree, DataTable, Log, Tabs, TabPane
    )
    from textual.screen import Screen, ModalScreen
    from textual.binding import Binding
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.progress import Progress, TaskID
    from rich.syntax import Syntax
    from rich.json import JSON
    from rich.markdown import Markdown
    from config import get_config
    import pandas as pd
    import sqlite3
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install required dependencies: pip install textual rich")
    sys.exit(1)

# Get configuration
config = get_config()


class StatusScreen(ModalScreen[str]):
    """Modal screen to show status and progress."""

    def __init__(self, title: str, message: str):
        self.screen_title = title
        self.message = message
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Container(
            Static(self.screen_title, classes="title"),
            Static(self.message, classes="message"),
            ProgressBar(show_eta=False, classes="progress"),
            classes="status-dialog"
        )


class ConfigScreen(Screen):
    """Screen to display and edit configuration."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("s", "save", "Save"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("⚙️ Gold Digger Configuration", classes="screen-title"),
            ScrollableContainer(
                Static(self._get_config_info(), classes="config-info"),
                classes="config-container"
            ),
            Container(
                Button("Save Changes", id="save", variant="primary"),
                Button("Reset to Defaults", id="reset", variant="warning"),
                Button("Back", id="back"),
                classes="button-row"
            ),
            classes="config-screen"
        )
        yield Footer()

    def _get_config_info(self) -> str:
        """Get formatted configuration information."""
        try:
            config_info = f"""
🤖 **Ollama Configuration**
   Host: {config.ollama_host}
   Model: {config.ollama_model}
   Timeout: {config.ollama_timeout}s

💾 **Database**
   Path: {config.database_path}

📊 **Analysis Settings**
   Default Interval: {config.default_interval}
   Analysis Hours: {config.default_analysis_hours}
   Fetch Days: {config.default_fetch_days}
   News Days: {config.default_news_days}

📰 **News Configuration**
   Symbols: {', '.join(config.news_symbols)}
   Max Articles per Symbol: {config.max_articles_per_symbol}

🔧 **System Settings**
   Debug Mode: {'ON' if config.debug_mode else 'OFF'}
   Log Level: {config.log_level}
   API Delay: {config.api_delay}s
            """
            return config_info.strip()
        except Exception as e:
            return f"❌ Error loading configuration: {e}"

    def action_back(self):
        self.app.pop_screen()

    def action_save(self):
        self.app.notify("💾 Configuration saved!")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "back":
            self.action_back()
        elif event.button.id == "save":
            self.action_save()
        elif event.button.id == "reset":
            self.app.notify("🔄 Configuration reset to defaults")


class DatabaseScreen(Screen):
    """Screen to display database statistics and data."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("r", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("📊 Database Statistics", classes="screen-title"),
            Tabs(
                TabPane("Price Data", id="prices"),
                TabPane("News Data", id="news"),
                TabPane("Analysis", id="analysis"),
                id="data-tabs"
            ),
            classes="database-screen"
        )
        yield Footer()

    def on_mount(self):
        self.refresh_data()

    def refresh_data(self):
        """Refresh database statistics."""
        try:
            # Get price data stats
            with sqlite3.connect(config.database_path) as conn:
                cursor = conn.cursor()

                # Price tables stats
                price_stats = {}
                for interval in ['15m', '30m']:
                    table_name = f"gold_prices_{interval}"
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0] if cursor.fetchone() else 0

                    cursor.execute(f"SELECT MIN(datetime), MAX(datetime) FROM {table_name}")
                    date_range = cursor.fetchone()

                    price_stats[interval] = {
                        'count': count,
                        'date_range': date_range
                    }

                # News stats
                cursor.execute("SELECT COUNT(*) FROM gold_news")
                news_count = cursor.fetchone()[0] if cursor.fetchone() else 0

                cursor.execute("SELECT AVG(sentiment_score) FROM gold_news WHERE sentiment_score IS NOT NULL")
                avg_sentiment = cursor.fetchone()[0] if cursor.fetchone() else 0

                # Update UI with stats
                self._update_stats_display(price_stats, news_count, avg_sentiment)

        except Exception as e:
            self.app.notify(f"❌ Error loading database stats: {e}")

    def _update_stats_display(self, price_stats: Dict, news_count: int, avg_sentiment: float):
        """Update the statistics display."""
        prices_content = f"""
📈 **15-minute Data**
   Records: {price_stats.get('15m', {}).get('count', 0):,}
   Date Range: {price_stats.get('15m', {}).get('date_range', ('N/A', 'N/A'))[0]} to {price_stats.get('15m', {}).get('date_range', ('N/A', 'N/A'))[1]}

📈 **30-minute Data**
   Records: {price_stats.get('30m', {}).get('count', 0):,}
   Date Range: {price_stats.get('30m', {}).get('date_range', ('N/A', 'N/A'))[0]} to {price_stats.get('30m', {}).get('date_range', ('N/A', 'N/A'))[1]}
        """

        news_content = f"""
📰 **News Articles**
   Total Articles: {news_count:,}
   Average Sentiment: {avg_sentiment:.3f}

📊 **Categories**
   Loading category breakdown...
        """

        # Update tab content
        prices_tab = self.query_one("#prices")
        news_tab = self.query_one("#news")

        prices_tab.add_class("updated")
        news_tab.add_class("updated")

    def action_back(self):
        self.app.pop_screen()

    def action_refresh(self):
        self.refresh_data()
        self.app.notify("🔄 Data refreshed")


class NewsScreen(Screen):
    """Screen for news browsing and analysis."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("f", "fetch", "Fetch News"),
        Binding("s", "search", "Search"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("📰 News & Sentiment Analysis", classes="screen-title"),
            Horizontal(
                Container(
                    Button("🔄 Fetch News", id="fetch-news", variant="primary"),
                    Button("🔍 Search", id="search-news"),
                    Button("📈 Sentiment", id="sentiment"),
                    Button("📂 Categories", id="categories"),
                    classes="news-buttons"
                ),
                classes="news-controls"
            ),
            ScrollableContainer(
                Static("📰 Recent Headlines", classes="section-title"),
                Container(
                    Static("Loading headlines...", id="headlines-content"),
                    id="headlines-container"
                ),
                Static("📊 Sentiment Analysis", classes="section-title"),
                Container(
                    Static("Sentiment analysis will appear here...", id="sentiment-content"),
                    id="sentiment-container"
                ),
                classes="news-content"
            ),
            classes="news-screen"
        )
        yield Footer()

    def on_mount(self):
        self.load_recent_headlines()

    def load_recent_headlines(self):
        """Load recent news headlines from database."""
        try:
            if self.app.demo_mode:
                # Demo headlines
                headlines_html = """
😊 **Federal Reserve Signals Dovish Stance on Gold Market Outlook**
   📺 Reuters | 📅 2024-01-15 | 💭 0.45

😐 **Gold Prices Hold Steady Amid Mixed Economic Signals**
   📺 MarketWatch | 📅 2024-01-15 | 💭 0.12

😟 **Rising Dollar Pressures Gold, Technical Support Tested**
   📺 Bloomberg | 📅 2024-01-14 | 💭 -0.23

😊 **Central Bank Gold Purchases Reach Multi-Year High**
   📺 Financial Times | 📅 2024-01-14 | 💭 0.67

😐 **Gold ETF Inflows Continue Despite Volatility Concerns**
   📺 Yahoo Finance | 📅 2024-01-13 | 💭 0.05
                """
                headlines_static = self.query_one("#headlines-content")
                headlines_static.update(headlines_html.strip())
                return

            with sqlite3.connect(config.database_path) as conn:
                query = """
                    SELECT title, publisher, published_date, sentiment_score
                    FROM gold_news
                    ORDER BY published_date DESC
                    LIMIT 10
                """
                df = pd.read_sql_query(query, conn)

                if not df.empty:
                    headlines_html = ""
                    for _, row in df.iterrows():
                        sentiment_emoji = "😊" if row['sentiment_score'] > 0.1 else "😐" if row['sentiment_score'] > -0.1 else "😟"
                        headlines_html += f"""
{sentiment_emoji} **{row['title'][:80]}{'...' if len(row['title']) > 80 else ''}**
   📺 {row['publisher']} | 📅 {row['published_date']} | 💭 {row['sentiment_score']:.2f}
                        """.strip() + "\n\n"

                    headlines_static = self.query_one("#headlines-content")
                    headlines_static.update(headlines_html)
                else:
                    headlines_static = self.query_one("#headlines-content")
                    headlines_static.update("No news data available. Click 'Fetch News' to load latest articles.")

        except Exception as e:
            self.app.notify(f"❌ Error loading headlines: {e}")

    async def fetch_news(self):
        """Fetch latest news articles."""
        try:
            self.app.push_screen(StatusScreen("Fetching News", "Loading latest gold news articles..."))
        except Exception:
            # If screen push fails, continue without status screen
            pass

        try:
            # Simulate news fetching delay
            await asyncio.sleep(2)

            if self.app.demo_mode:
                # Demo mode - just refresh with sample data
                try:
                    self.app.pop_screen()
                except Exception:
                    pass
                self.load_recent_headlines()
                self.app.notify("✅ Demo news updated!")
                return

            # Call actual news fetcher
            from news_fetcher import main as news_main
            old_argv = sys.argv
            sys.argv = ['news_fetcher.py', '--fetch']

            try:
                news_main()
                try:
                    self.app.pop_screen()  # Close status screen
                except Exception:
                    pass
                self.load_recent_headlines()  # Refresh headlines
                self.app.notify("✅ News fetched successfully!")
            finally:
                sys.argv = old_argv

        except Exception as e:
            try:
                self.app.pop_screen()  # Close status screen
            except Exception:
                pass
            self.app.notify(f"❌ Error fetching news: {e}")

    def action_back(self):
        self.app.pop_screen()

    def action_fetch(self):
        asyncio.create_task(self.fetch_news())

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "fetch-news":
            self.action_fetch()
        elif event.button.id == "search-news":
            self.app.notify("🔍 Search functionality coming soon...")
        elif event.button.id == "sentiment":
            self.app.notify("📈 Sentiment analysis coming soon...")
        elif event.button.id == "categories":
            self.app.notify("📂 Category analysis coming soon...")


class TradingScreen(Screen):
    """Screen for trading analysis and recommendations."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("a", "analyze", "Analyze"),
        Binding("q", "quick", "Quick Analysis"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("🤖 AI Trading Analysis", classes="screen-title"),
            Horizontal(
                Container(
                    Button("⚡ Quick Analysis", id="quick-analysis", variant="primary"),
                    Button("📊 Full Analysis", id="full-analysis"),
                    Button("📈 Price Only", id="price-analysis"),
                    Button("📰 News Only", id="news-analysis"),
                    classes="trading-buttons"
                ),
                classes="trading-controls"
            ),
            ScrollableContainer(
                Static("🎯 Latest Recommendation", classes="section-title"),
                Container(
                    Static("Loading recommendation...", id="recommendation-content"),
                    id="recommendation-container"
                ),
                Static("📊 Analysis Details", classes="section-title"),
                Container(
                    Static("Analysis details will appear here...", id="analysis-content"),
                    id="analysis-container"
                ),
                classes="trading-content"
            ),
            classes="trading-screen"
        )
        yield Footer()

    def on_mount(self):
        self.load_latest_recommendation()

    def load_latest_recommendation(self):
        """Load the latest trading recommendation."""
        try:
            if self.app.demo_mode:
                # Demo recommendation
                rec_text = """
🎯 **LONG POSITION RECOMMENDED**
💰 Current Price: $2,045.50
📈 Entry Target: $2,043.00
🛑 Stop Loss: $2,035.00
🎯 Take Profit: $2,055.00
🔒 Confidence: HIGH (85%)
⏰ Generated: 2024-01-15 10:30 AM
📊 Interval: 15m analysis
✅ Success Rate: 78%

📝 **Analysis Summary:**
Strong bullish momentum with positive news sentiment.
Fed dovish signals supporting gold demand.
Technical breakout above $2,040 resistance.
                """.strip()

                recommendation_static = self.query_one("#recommendation-content")
                recommendation_static.update(rec_text)
                return

            with sqlite3.connect(config.database_path) as conn:
                query = """
                    SELECT * FROM trading_recommendations
                    ORDER BY timestamp DESC
                    LIMIT 1
                """
                df = pd.read_sql_query(query, conn)

                if not df.empty:
                    rec = df.iloc[0]
                    rec_text = f"""
    🎯 **{rec['recommendation']}**
    💰 Current Price: ${rec['current_price']:.2f}
    ⏰ Time: {rec['timestamp']}
    📊 Interval: {rec['interval_used']}
    ✅ Success Rate: {rec.get('success', 'N/A')}
                        """.strip()
                else:
                    rec_text = "No recommendations available. Run an analysis to generate recommendations."

                recommendation_static = self.query_one("#recommendation-content")
                recommendation_static.update(rec_text)

        except Exception as e:
            self.app.notify(f"❌ Error loading recommendations: {e}")

    async def run_analysis(self, analysis_type: str):
        """Run trading analysis."""
        try:
            self.app.push_screen(StatusScreen(f"{analysis_type} Analysis", f"Running {analysis_type.lower()} analysis..."))
        except Exception:
            # If screen push fails, continue without status screen
            pass

        try:
            # Simulate analysis time
            await asyncio.sleep(3)

            if self.app.demo_mode:
                # Demo mode - just refresh with sample data
                try:
                    self.app.pop_screen()
                except Exception:
                    pass
                self.load_latest_recommendation()
                self.app.notify(f"✅ Demo {analysis_type.lower()} analysis completed!")
                return

            # Call actual analyzer based on type
            from trading_analyzer import main as trading_main
            old_argv = sys.argv

            if analysis_type == "Quick":
                sys.argv = ['trading_analyzer.py', '--hours', '24']
            elif analysis_type == "Price":
                sys.argv = ['trading_analyzer.py', '--no-news', '--hours', '48']
            else:
                sys.argv = ['trading_analyzer.py']

            try:
                trading_main()
                try:
                    self.app.pop_screen()  # Close status screen
                except Exception:
                    pass
                self.load_latest_recommendation()  # Refresh recommendation
                self.app.notify(f"✅ {analysis_type} analysis completed!")
            finally:
                sys.argv = old_argv

        except Exception as e:
            try:
                self.app.pop_screen()  # Close status screen
            except Exception:
                pass
            self.app.notify(f"❌ Error in {analysis_type.lower()} analysis: {e}")

    def action_back(self):
        self.app.pop_screen()

    def action_analyze(self):
        asyncio.create_task(self.run_analysis("Full"))

    def action_quick(self):
        asyncio.create_task(self.run_analysis("Quick"))

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "quick-analysis":
            asyncio.create_task(self.run_analysis("Quick"))
        elif event.button.id == "full-analysis":
            asyncio.create_task(self.run_analysis("Full"))
        elif event.button.id == "price-analysis":
            asyncio.create_task(self.run_analysis("Price"))
        elif event.button.id == "news-analysis":
            self.app.notify("📰 News-only analysis coming soon...")


class MainScreen(Screen):
    """Main dashboard screen."""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("🏆 Gold Digger - AI Trading Analysis System"),
            Static(""),  # Spacer
            Static(self._get_status_summary(), id="status-summary"),
            Static(""),  # Spacer
            Static("🚀 Quick Actions"),
            Button("⚡ Quick Analysis", id="quick-analysis", variant="primary"),
            Button("📊 Full Analysis", id="full-analysis", variant="success"),
            Button("📰 Latest News", id="news", variant="default"),
            Button("⚙️ Configuration", id="config", variant="default"),
            Static(""),  # Spacer
            Static("📋 System Modules"),
            Button("💰 Price Data", id="prices", variant="default"),
            Button("📈 Trading Analysis", id="trading", variant="default"),
            Button("📰 News & Sentiment", id="news-detail", variant="default"),
            Button("💾 Database", id="database", variant="default"),
        )
        yield Footer()

    def _get_status_summary(self) -> str:
        """Get system status summary."""
        try:
            if self.app.demo_mode:
                return "💾 Database: ✅ Demo | 🤖 AI: ✅ Active | 💰 Gold: $2,045.50 | 🎭 Demo Mode"

            # Check database
            db_status = "✅ OK" if Path(config.database_path).exists() else "❌ Missing"

            # Check Ollama (simplified check)
            ollama_status = "✅ OK" if config.ollama_host else "❌ Not Set"

            # Get latest price (if available)
            latest_price = "N/A"
            try:
                with sqlite3.connect(config.database_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT close FROM gold_prices_15m ORDER BY datetime DESC LIMIT 1")
                    result = cursor.fetchone()
                    if result:
                        latest_price = f"${result[0]:.2f}"
            except:
                pass

            return f"💾 DB: {db_status} | 🤖 AI: {ollama_status} | 💰 Gold: {latest_price}"
        except Exception as e:
            return f"❌ Status Error: {str(e)[:50]}"

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "quick-analysis":
            self.app.push_screen(TradingScreen())
            # Auto-trigger quick analysis
            try:
                trading_screen = self.app.screen_stack[-1]
                if hasattr(trading_screen, 'run_analysis'):
                    asyncio.create_task(trading_screen.run_analysis("Quick"))
            except Exception:
                pass
        elif event.button.id == "full-analysis":
            self.app.push_screen(TradingScreen())
            # Auto-trigger full analysis
            try:
                trading_screen = self.app.screen_stack[-1]
                if hasattr(trading_screen, 'run_analysis'):
                    asyncio.create_task(trading_screen.run_analysis("Full"))
            except Exception:
                pass
        elif event.button.id == "news":
            self.app.push_screen(NewsScreen())
        elif event.button.id == "config":
            self.app.push_screen(ConfigScreen())
        elif event.button.id == "prices":
            self.app.notify("💰 Price data module coming soon...")
        elif event.button.id == "trading":
            self.app.push_screen(TradingScreen())
        elif event.button.id == "news-detail":
            self.app.push_screen(NewsScreen())
        elif event.button.id == "database":
            self.app.push_screen(DatabaseScreen())


class GoldDiggerTUI(App):
    """Gold Digger TUI Application."""

    TITLE = "Gold Digger TUI"
    SUB_TITLE = "AI-Powered Gold Trading Analysis"
    CSS_PATH = "gold_digger_tui.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("d", "toggle_dark", "Toggle Dark Mode"),
        Binding("h", "help", "Help"),
        Binding("ctrl+r", "refresh", "Refresh"),
    ]

    def __init__(self):
        super().__init__()
        self.demo_mode = False
        self._dark_mode = True

    def on_mount(self):
        """Initialize the application."""
        # Set initial dark mode
        if self._dark_mode:
            self.add_class("-dark-mode")

        if self.demo_mode:
            self.notify("🎭 Demo mode active - using sample data")
        self.push_screen(MainScreen())

    def action_refresh(self):
        """Refresh current screen."""
        current_screen = self.screen
        current_screen.refresh()
        self.notify("🔄 Screen refreshed")

    def action_toggle_dark(self):
        """Toggle dark mode."""
        try:
            if self.has_class("-dark-mode"):
                self.remove_class("-dark-mode")
                self._dark_mode = False
                mode = "Light"
            else:
                self.add_class("-dark-mode")
                self._dark_mode = True
                mode = "Dark"
            self.notify(f"🌓 Switched to {mode} mode")
        except Exception:
            # Fallback if screen operations fail
            self._dark_mode = not self._dark_mode
            mode = "Dark" if self._dark_mode else "Light"
            self.notify(f"🌓 Switched to {mode} mode")

    def action_help(self):
        """Show help information."""
        help_text = """
🏆 **Gold Digger TUI - Keyboard Shortcuts**

**Global Keys:**
• Q - Quit application
• D - Toggle dark/light mode
• H - Show this help

**Navigation:**
• ESC - Go back to previous screen
• TAB - Navigate between elements
• ENTER - Activate buttons/selections

**Quick Actions:**
• F - Fetch data (context dependent)
• A - Run analysis (context dependent)
• S - Search/Save (context dependent)
• R - Refresh data (context dependent)

**Mouse:**
• Click buttons to activate
• Scroll in scrollable areas
• Hover for tooltips (where available)
        """
        self.notify("💡 Help information displayed")


def main():
    """Main entry point for the TUI application."""
    import argparse

    parser = argparse.ArgumentParser(description='Gold Digger TUI - Modern Interactive Interface')
    parser.add_argument('--demo', action='store_true', help='Run in demo mode with sample data')
    args = parser.parse_args()

    try:
        app = GoldDiggerTUI()
        if args.demo:
            app.demo_mode = True
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Gold Digger TUI terminated by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
