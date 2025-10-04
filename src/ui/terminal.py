#!/usr/bin/env python3
"""
Gold Digger Terminal - Unified Interactive Application
A comprehensive terminal interface for all Gold Digger functionality.
"""

import sys
import os
import logging
from datetime import datetime
import argparse
from typing import Optional, Dict, Any

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config import get_config
    import pandas as pd
    # Import other modules as needed in functions to avoid circular imports
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all dependencies are installed and the current directory is correct.")
    sys.exit(1)

# Get configuration
config = get_config()
logger = logging.getLogger(__name__)


class GoldDiggerTerminal:
    """Unified terminal application for Gold Digger functionality."""

    def __init__(self):
        self.config = config
        self.running = True
        self.price_fetcher = None
        self.trading_analyzer = None
        self.news_fetcher = None
        self.news_analyzer = None
        self.news_viewer = None
        self.data_analyzer = None

    def initialize_components(self):
        """Initialize all component instances."""
        try:
            # Initialize basic components - others will be imported as needed
            from query_example import GoldDataAnalyzer
            self.data_analyzer = GoldDataAnalyzer()
            return True
        except Exception as e:
            print(f"❌ Error initializing components: {e}")
            return False

    def print_header(self):
        """Print the main application header."""
        print("\n" + "=" * 80)
        print("🏆 GOLD DIGGER TERMINAL - Unified Trading Analysis System")
        print("📊 Price Data • 📰 News Intelligence • 🤖 AI Analysis • ⚙️ Complete Automation")
        print("=" * 80)

    def print_menu(self):
        """Print the main menu options."""
        menu_options = [
            ("📊 PRICE DATA & ANALYSIS", [
                ("1", "Fetch Gold Prices (15m/30m intervals)"),
                ("2", "Run AI Trading Analysis"),
                ("3", "View Price Data Summary"),
                ("4", "Export Price Data to CSV")
            ]),
            ("📰 NEWS & SENTIMENT", [
                ("5", "Fetch Latest Gold News"),
                ("6", "View News Summary"),
                ("7", "Interactive News Browser"),
                ("8", "News Sentiment Analysis"),
                ("9", "Search News by Keyword"),
                ("10", "Export News to HTML")
            ]),
            ("🤖 COMPREHENSIVE ANALYSIS", [
                ("11", "Complete Analysis (All Features)"),
                ("12", "Quick Analysis (Price + News + AI)"),
                ("13", "News-Only Analysis"),
                ("14", "Price-Only Analysis")
            ]),
            ("📋 DATA EXPLORATION", [
                ("15", "Database Query Examples"),
                ("16", "View Database Statistics"),
                ("17", "Recent Headlines"),
                ("18", "Category Analysis")
            ]),
            ("⚙️ CONFIGURATION & SETUP", [
                ("19", "View Current Configuration"),
                ("20", "Run Setup Wizard"),
                ("21", "Test System Setup"),
                ("22", "Install Dependencies")
            ]),
            ("🔧 UTILITIES", [
                ("0", "Exit Application"),
                ("h", "Show This Menu"),
                ("c", "Clear Screen")
            ])
        ]

        print("\n📋 MAIN MENU")
        print("-" * 50)

        for category, options in menu_options:
            print(f"\n{category}")
            for key, description in options:
                print(f"  {key:2s}) {description}")

        print("\n" + "-" * 50)

    def get_user_input(self, prompt: str = "Enter your choice", default: str = None) -> str:
        """Get user input with optional default."""
        if default:
            full_prompt = f"{prompt} [{default}]: "
        else:
            full_prompt = f"{prompt}: "

        try:
            user_input = input(full_prompt).strip()
            return user_input if user_input else (default or "")
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 Goodbye!")
            self.running = False
            return ""

    def get_numeric_input(self, prompt: str, default: int = None, min_val: int = None, max_val: int = None) -> Optional[int]:
        """Get numeric input with validation."""
        while True:
            try:
                value_str = self.get_user_input(prompt, str(default) if default else None)
                if not value_str and default is not None:
                    return default

                value = int(value_str)
                if min_val is not None and value < min_val:
                    print(f"❌ Value must be at least {min_val}")
                    continue
                if max_val is not None and value > max_val:
                    print(f"❌ Value must be at most {max_val}")
                    continue

                return value
            except ValueError:
                print("❌ Please enter a valid number")
            except (EOFError, KeyboardInterrupt):
                return None

    def pause(self, message: str = "Press Enter to continue..."):
        """Pause execution and wait for user input."""
        try:
            input(f"\n{message}")
        except (EOFError, KeyboardInterrupt):
            pass

    def handle_price_fetch(self):
        """Handle gold price fetching."""
        print("\n📊 GOLD PRICE FETCHER")
        print("-" * 40)

        days = self.get_numeric_input("Days to fetch", config.default_fetch_days, 1, 365)
        if days is None:
            return

        print(f"🔄 Fetching {days} days of gold price data...")
        try:
            from gold_fetcher import main as price_main
            import sys

            old_argv = sys.argv
            sys.argv = ['gold_fetcher.py', '--days', str(days)]

            try:
                price_main()
                print("✅ Price data fetched successfully!")
            finally:
                sys.argv = old_argv
        except Exception as e:
            print(f"❌ Error fetching prices: {e}")

        self.pause()

    def handle_trading_analysis(self):
        """Handle AI trading analysis."""
        print("\n🤖 AI TRADING ANALYSIS")
        print("-" * 40)

        interval = self.get_user_input("Interval (15m/30m)", config.default_interval)
        hours = self.get_numeric_input("Hours to analyze", config.default_analysis_hours, 1, 168)

        if hours is None:
            return

        print(f"🔄 Running AI trading analysis...")
        print(f"   Interval: {interval}")
        print(f"   Hours: {hours}")

        try:
            from trading_analyzer import main as trading_main
            import sys

            old_argv = sys.argv
            sys.argv = ['trading_analyzer.py', '--interval', interval, '--hours', str(hours)]

            try:
                trading_main()
            finally:
                sys.argv = old_argv
        except Exception as e:
            print(f"❌ Error in trading analysis: {e}")

        self.pause()

    def handle_price_summary(self):
        """Handle price data summary."""
        print("\n📈 PRICE DATA SUMMARY")
        print("-" * 40)

        try:
            self.data_analyzer.get_latest_prices()
            print()
            self.data_analyzer.get_daily_summary()
        except Exception as e:
            print(f"❌ Error getting price summary: {e}")

        self.pause()

    def handle_export_prices(self):
        """Handle price data export."""
        print("\n📤 EXPORT PRICE DATA")
        print("-" * 40)

        interval = self.get_user_input("Interval (15m/30m)", "15m")
        days = self.get_numeric_input("Days to export", 7, 1, 365)

        if days is None:
            return

        try:
            filename = f"gold_{interval}_{days}days.csv"
            # Export logic using direct database query
            import sqlite3
            table_name = f"gold_prices_{interval}"
            with sqlite3.connect("gold_prices.db") as conn:
                query = f"""
                    SELECT * FROM {table_name}
                    WHERE datetime >= date('now', '-{days} days')
                    ORDER BY datetime DESC
                """
                df = pd.read_sql_query(query, conn)
                df.to_csv(filename, index=False)
            print(f"✅ Data exported to {filename}")
        except Exception as e:
            print(f"❌ Export error: {e}")

        self.pause()

    def handle_news_fetch(self):
        """Handle news fetching."""
        print("\n📰 GOLD NEWS FETCHER")
        print("-" * 40)

        print("🔄 Fetching latest gold news...")
        try:
            # Call the main function from news_fetcher
            from news_fetcher import main as news_main
            import sys
            from io import StringIO

            # Capture output
            old_argv = sys.argv
            sys.argv = ['news_fetcher.py', '--fetch']

            try:
                news_main()
                print("✅ News fetched successfully!")

                # Show summary
                sys.argv = ['news_fetcher.py', '--summary']
                news_main()
            finally:
                sys.argv = old_argv
        except Exception as e:
            print(f"❌ Error fetching news: {e}")

        self.pause()

    def handle_news_summary(self):
        """Handle news summary display."""
        print("\n📊 NEWS SUMMARY")
        print("-" * 40)

        try:
            from news_fetcher import main as news_main
            import sys

            old_argv = sys.argv
            sys.argv = ['news_fetcher.py', '--summary']

            try:
                news_main()
            finally:
                sys.argv = old_argv
        except Exception as e:
            print(f"❌ Error displaying news summary: {e}")

        self.pause()

    def handle_interactive_news(self):
        """Handle interactive news browser."""
        print("\n🔍 INTERACTIVE NEWS BROWSER")
        print("-" * 40)
        print("Available commands: stats, browse [n], search <keyword>, article <id>, quit")

        try:
            from news_viewer import main as viewer_main
            import sys

            old_argv = sys.argv
            sys.argv = ['news_viewer.py', '--interactive']

            try:
                viewer_main()
            finally:
                sys.argv = old_argv
        except Exception as e:
            print(f"❌ Error in interactive news browser: {e}")

    def handle_sentiment_analysis(self):
        """Handle news sentiment analysis."""
        print("\n📈 NEWS SENTIMENT ANALYSIS")
        print("-" * 40)

        days = self.get_numeric_input("Days to analyze", 7, 1, 30)
        if days is None:
            return

        try:
            from news_analyzer import main as analyzer_main
            import sys

            old_argv = sys.argv
            sys.argv = ['news_analyzer.py', '--sentiment', '--days', str(days)]

            try:
                analyzer_main()
            finally:
                sys.argv = old_argv
        except Exception as e:
            print(f"❌ Error in sentiment analysis: {e}")

        self.pause()

    def handle_search_news(self):
        """Handle news search."""
        print("\n🔍 SEARCH NEWS")
        print("-" * 40)

        keyword = self.get_user_input("Enter search keyword")
        if not keyword:
            return

        try:
            from news_viewer import main as viewer_main
            import sys

            old_argv = sys.argv
            sys.argv = ['news_viewer.py', '--search', keyword, '--details']

            try:
                viewer_main()
            finally:
                sys.argv = old_argv
        except Exception as e:
            print(f"❌ Search error: {e}")

        self.pause()

    def handle_export_news(self):
        """Handle news export to HTML."""
        print("\n📤 EXPORT NEWS TO HTML")
        print("-" * 40)

        days = self.get_numeric_input("Days to include", 7, 1, 30)
        filename = self.get_user_input("Output filename", "gold_news_report.html")

        if days is None:
            return

        try:
            from export_news_html import main as export_main
            import sys

            old_argv = sys.argv
            sys.argv = ['export_news_html.py', '--days', str(days), '--output', filename]

            try:
                export_main()
            finally:
                sys.argv = old_argv
            print(f"✅ News exported to {filename}")
        except Exception as e:
            print(f"❌ Export error: {e}")

        self.pause()

    def handle_complete_analysis(self):
        """Handle complete analysis workflow."""
        print("\n🏆 COMPLETE ANALYSIS")
        print("-" * 40)

        days = self.get_numeric_input("Days of data to analyze", config.default_fetch_days, 1, 30)
        if days is None:
            return

        print("🔄 Running complete analysis workflow...")

        try:
            # Fetch prices
            print("📊 1. Fetching price data...")
            from gold_fetcher import main as price_main
            import sys

            old_argv = sys.argv
            sys.argv = ['gold_fetcher.py', '--days', str(days)]

            try:
                price_main()
            finally:
                sys.argv = old_argv

            # Fetch news
            print("📰 2. Fetching news data...")
            from news_fetcher import main as news_main
            sys.argv = ['news_fetcher.py', '--fetch']

            try:
                news_main()
            finally:
                sys.argv = old_argv

            # Run analysis
            print("🤖 3. Running AI analysis...")
            from trading_analyzer import main as trading_main
            import sys

            old_argv = sys.argv
            sys.argv = ['trading_analyzer.py']

            try:
                trading_main()
            finally:
                sys.argv = old_argv

            print("📈 4. Analyzing sentiment...")
            from news_analyzer import main as analyzer_main
            sys.argv = ['news_analyzer.py', '--sentiment', '--days', str(days)]

            try:
                analyzer_main()
            finally:
                sys.argv = old_argv

            print("\n✅ Complete analysis finished!")

        except Exception as e:
            print(f"❌ Error in complete analysis: {e}")

        self.pause()

    def handle_quick_analysis(self):
        """Handle quick analysis."""
        print("\n⚡ QUICK ANALYSIS")
        print("-" * 40)

        print("🔄 Running quick analysis (price + news + AI)...")

        try:
            # Quick price fetch (fewer days)
            from gold_fetcher import main as price_main
            import sys

            old_argv = sys.argv
            sys.argv = ['gold_fetcher.py', '--days', '3']

            try:
                price_main()
            finally:
                sys.argv = old_argv

            # Quick news fetch
            from news_fetcher import main as news_main
            sys.argv = ['news_fetcher.py', '--fetch']

            try:
                news_main()
            finally:
                sys.argv = old_argv

            # Quick AI analysis
            from trading_analyzer import main as trading_main
            import sys

            old_argv = sys.argv
            sys.argv = ['trading_analyzer.py', '--hours', '24']

            try:
                trading_main()
            finally:
                sys.argv = old_argv

            print("\n✅ Quick analysis complete!")

        except Exception as e:
            print(f"❌ Error in quick analysis: {e}")

        self.pause()

    def handle_news_only_analysis(self):
        """Handle news-only analysis."""
        print("\n📰 NEWS-ONLY ANALYSIS")
        print("-" * 40)

        days = self.get_numeric_input("Days to analyze", 7, 1, 30)
        if days is None:
            return

        try:
            print("🔄 Fetching and analyzing news...")
            from news_fetcher import main as news_main
            import sys

            old_argv = sys.argv
            sys.argv = ['news_fetcher.py', '--fetch']

            try:
                news_main()
            finally:
                sys.argv = old_argv

            print("📊 News Summary:")
            from news_fetcher import main as news_main
            import sys

            old_argv = sys.argv
            sys.argv = ['news_fetcher.py', '--summary']

            try:
                news_main()
            finally:
                sys.argv = old_argv

            print("📈 Sentiment Analysis:")
            from news_analyzer import main as analyzer_main
            sys.argv = ['news_analyzer.py', '--sentiment', '--days', str(days)]

            try:
                analyzer_main()
            finally:
                sys.argv = old_argv

            print("📂 Category Analysis:")
            sys.argv = ['news_analyzer.py', '--categories']

            try:
                analyzer_main()
            finally:
                sys.argv = old_argv

        except Exception as e:
            print(f"❌ Error in news analysis: {e}")

        self.pause()

    def handle_price_only_analysis(self):
        """Handle price-only analysis."""
        print("\n📊 PRICE-ONLY ANALYSIS")
        print("-" * 40)

        days = self.get_numeric_input("Days to analyze", config.default_fetch_days, 1, 30)
        if days is None:
            return

        try:
            print("🔄 Fetching and analyzing prices...")
            from gold_fetcher import main as price_main
            import sys

            old_argv = sys.argv
            sys.argv = ['gold_fetcher.py', '--days', str(days)]

            try:
                price_main()
            finally:
                sys.argv = old_argv

            print("📈 Price Summary:")
            self.data_analyzer.get_latest_prices()
            self.data_analyzer.get_daily_summary()

            print("🤖 Technical Analysis:")
            from trading_analyzer import main as trading_main
            import sys

            old_argv = sys.argv
            sys.argv = ['trading_analyzer.py', '--no-news', '--hours', '48']

            try:
                trading_main()
            finally:
                sys.argv = old_argv

        except Exception as e:
            print(f"❌ Error in price analysis: {e}")

        self.pause()

    def handle_database_queries(self):
        """Handle database query examples."""
        print("\n📋 DATABASE QUERY EXAMPLES")
        print("-" * 40)

        try:
            self.data_analyzer.get_latest_prices()
            print()
            self.data_analyzer.get_daily_summary()
            print()
            self.data_analyzer.get_volatility_analysis()
        except Exception as e:
            print(f"❌ Error running database queries: {e}")

        self.pause()

    def handle_database_stats(self):
        """Handle database statistics."""
        print("\n📊 DATABASE STATISTICS")
        print("-" * 40)

        try:
            from news_viewer import main as viewer_main
            import sys

            old_argv = sys.argv
            sys.argv = ['news_viewer.py', '--stats']

            try:
                viewer_main()
            finally:
                sys.argv = old_argv
        except Exception as e:
            print(f"❌ Error getting database stats: {e}")

        self.pause()

    def handle_recent_headlines(self):
        """Handle recent headlines display."""
        print("\n📰 RECENT HEADLINES")
        print("-" * 40)

        count = self.get_numeric_input("Number of headlines", 10, 1, 50)
        if count is None:
            return

        try:
            from news_viewer import main as viewer_main
            import sys

            old_argv = sys.argv
            sys.argv = ['news_viewer.py', '--browse', '--limit', str(count)]

            try:
                viewer_main()
            finally:
                sys.argv = old_argv
        except Exception as e:
            print(f"❌ Error getting headlines: {e}")

        self.pause()

    def handle_category_analysis(self):
        """Handle news category analysis."""
        print("\n📂 CATEGORY ANALYSIS")
        print("-" * 40)

        try:
            from news_analyzer import main as analyzer_main
            import sys

            old_argv = sys.argv
            sys.argv = ['news_analyzer.py', '--categories']

            try:
                analyzer_main()
            finally:
                sys.argv = old_argv
        except Exception as e:
            print(f"❌ Error in category analysis: {e}")

        self.pause()

    def handle_view_config(self):
        """Handle configuration display."""
        print("\n⚙️ CURRENT CONFIGURATION")
        print("-" * 40)

        try:
            config.print_config_summary()
        except Exception as e:
            print(f"❌ Error displaying configuration: {e}")

        self.pause()

    def handle_setup_wizard(self):
        """Handle setup wizard."""
        print("\n🔧 SETUP WIZARD")
        print("-" * 40)

        try:
            from configure import main as config_main
            import sys

            old_argv = sys.argv
            sys.argv = ['configure.py', '--quick']

            try:
                config_main()
                print("✅ Setup completed!")
            finally:
                sys.argv = old_argv
        except Exception as e:
            print(f"❌ Setup error: {e}")

        self.pause()

    def handle_test_setup(self):
        """Handle setup testing."""
        print("\n🧪 TESTING SYSTEM SETUP")
        print("-" * 40)

        try:
            from configure import main as config_main
            import sys

            old_argv = sys.argv
            sys.argv = ['configure.py', '--test']

            try:
                config_main()
                print("✅ All tests passed!")
            finally:
                sys.argv = old_argv
        except Exception as e:
            print(f"❌ Test error: {e}")

        self.pause()

    def handle_install_dependencies(self):
        """Handle dependency installation."""
        print("\n📦 INSTALLING DEPENDENCIES")
        print("-" * 40)

        try:
            from configure import main as config_main
            import sys

            old_argv = sys.argv
            sys.argv = ['configure.py', '--install-deps']

            try:
                config_main()
                print("✅ Dependencies installed!")
            finally:
                sys.argv = old_argv
        except Exception as e:
            print(f"❌ Installation error: {e}")

        self.pause()

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def run(self):
        """Run the main application loop."""
        self.clear_screen()
        self.print_header()

        # Initialize components
        print("🔄 Initializing system components...")
        if not self.initialize_components():
            print("❌ Failed to initialize. Please check your setup.")
            return

        print("✅ System ready!")

        while self.running:
            self.print_menu()
            choice = self.get_user_input("Enter your choice").lower()

            if not choice or not self.running:
                break

            if choice == '0':
                self.running = False
                continue
            elif choice == 'h':
                continue  # Show menu again
            elif choice == 'c':
                self.clear_screen()
                self.print_header()
                continue

            # Handle menu choices
            handlers = {
                '1': self.handle_price_fetch,
                '2': self.handle_trading_analysis,
                '3': self.handle_price_summary,
                '4': self.handle_export_prices,
                '5': self.handle_news_fetch,
                '6': self.handle_news_summary,
                '7': self.handle_interactive_news,
                '8': self.handle_sentiment_analysis,
                '9': self.handle_search_news,
                '10': self.handle_export_news,
                '11': self.handle_complete_analysis,
                '12': self.handle_quick_analysis,
                '13': self.handle_news_only_analysis,
                '14': self.handle_price_only_analysis,
                '15': self.handle_database_queries,
                '16': self.handle_database_stats,
                '17': self.handle_recent_headlines,
                '18': self.handle_category_analysis,
                '19': self.handle_view_config,
                '20': self.handle_setup_wizard,
                '21': self.handle_test_setup,
                '22': self.handle_install_dependencies,
            }

            handler = handlers.get(choice)
            if handler:
                try:
                    handler()
                except KeyboardInterrupt:
                    print("\n⚠️ Operation cancelled by user")
                    self.pause()
                except Exception as e:
                    print(f"\n❌ Unexpected error: {e}")
                    self.pause()
            else:
                print(f"❌ Invalid choice: {choice}")
                self.pause()

        print("\n👋 Thank you for using Gold Digger Terminal!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Gold Digger Terminal - Unified Interactive Application')
    parser.add_argument('--test', action='store_true', help='Test system setup and exit')
    parser.add_argument('--config', action='store_true', help='Show configuration and exit')
    parser.add_argument('--quick-analysis', action='store_true', help='Run quick analysis and exit')

    args = parser.parse_args()

    if args.test:
        try:
            from configure import main as config_main

            old_argv = sys.argv
            sys.argv = ['configure.py', '--test']
            config_main()
            sys.exit(0)
        except Exception as e:
            print(f"❌ Test error: {e}")
            sys.exit(1)

    if args.config:
        try:
            config.print_config_summary()
            sys.exit(0)
        except Exception as e:
            print(f"❌ Config error: {e}")
            sys.exit(1)

    if args.quick_analysis:
        terminal = GoldDiggerTerminal()
        terminal.initialize_components()
        terminal.handle_quick_analysis()
        sys.exit(0)

    # Run interactive terminal
    terminal = GoldDiggerTerminal()
    try:
        terminal.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
