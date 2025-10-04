#!/usr/bin/env python3
"""
Gold Digger - Main Entry Point
A professional gold trading analysis system with multiple interfaces.

Usage:
    python main.py [command] [options]

Commands:
    terminal    - Launch terminal interface
    tui         - Launch text-based UI (interactive)
    web         - Launch web interface
    fetch       - Fetch latest gold prices and news
    analyze     - Run complete analysis
    config      - Configure the application

Examples:
    python main.py web              # Start web interface
    python main.py tui              # Start interactive TUI
    python main.py fetch --days 7   # Fetch 7 days of data
    python main.py analyze          # Run full analysis
"""

import sys
import os
import argparse
from pathlib import Path

# Add src directory to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

# Import configuration
sys.path.insert(0, str(PROJECT_ROOT / 'config'))
from config import get_config


def setup_environment():
    """Setup the Gold Digger environment."""
    config = get_config()

    # Create necessary directories
    config.ensure_directories()

    # Show welcome message
    print("🏆 Gold Digger Trading Analysis System")
    print("=" * 50)


def launch_terminal():
    """Launch the terminal interface."""
    print("🖥️  Launching Terminal Interface...")
    try:
        from src.ui.terminal import main as terminal_main
        terminal_main()
    except ImportError as e:
        print(f"❌ Error importing terminal module: {e}")
        sys.exit(1)


def launch_tui():
    """Launch the Text-based User Interface."""
    print("📱 Launching Text-based UI...")
    try:
        from src.ui.tui_launcher import main as tui_main
        tui_main()
    except ImportError as e:
        print(f"❌ Error importing TUI module: {e}")
        print("💡 Make sure Textual is installed: pip install textual")
        sys.exit(1)


def launch_web(port=None):
    """Launch the web interface."""
    print("🌐 Launching Web Interface...")
    try:
        # Setup paths for web app imports
        web_dir = PROJECT_ROOT / 'web'
        sys.path.insert(0, str(web_dir))
        sys.path.insert(0, str(PROJECT_ROOT / 'config'))

        # Change to web directory
        os.chdir(web_dir)

        if port:
            os.environ['PORT'] = str(port)

        from app import main as web_main
        web_main()
    except ImportError as e:
        print(f"❌ Error importing web module: {e}")
        print("💡 Make sure Flask is installed: pip install flask flask-cors")
        sys.exit(1)


def fetch_data(days=7, symbols=None):
    """Fetch latest gold prices and news."""
    print(f"📊 Fetching {days} days of data...")
    try:
        from src.core.gold_fetcher import GoldPriceFetcher
        from src.core.news_fetcher import GoldNewsFetcher

        # Initialize fetchers
        gold_fetcher = GoldPriceFetcher()
        news_fetcher = GoldNewsFetcher()

        # Fetch gold prices
        print("⚡ Fetching gold price data...")
        gold_fetcher.fetch_and_cache_data(days=days)

        # Fetch news
        print("📰 Fetching news data...")
        news_fetcher.fetch_and_cache_gold_news()

        print("✅ Data fetch completed successfully!")

    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        sys.exit(1)


def run_analysis():
    """Run complete trading analysis."""
    print("🧠 Running Complete Analysis...")
    try:
        # Import the complete analysis script
        sys.path.insert(0, str(PROJECT_ROOT / 'scripts'))
        from scripts.run_complete_analysis import main as analysis_main
        analysis_main()

    except Exception as e:
        print(f"❌ Error running analysis: {e}")
        sys.exit(1)


def configure_app():
    """Configure the Gold Digger application."""
    print("⚙️  Gold Digger Configuration")
    print("-" * 30)

    try:
        from config.configure import main as config_main
        config_main()
    except ImportError:
        # Fallback configuration
        config = get_config()
        config.print_config_summary()

        response = input("\nCreate .env file with current settings? (y/N): ")
        if response.lower() == 'y':
            config.create_env_file()


def main():
    """Main entry point with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description='Gold Digger - Professional Gold Trading Analysis System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py web --port 8080      Start web interface on port 8080
  python main.py tui                  Start interactive TUI
  python main.py fetch --days 14      Fetch 14 days of data
  python main.py analyze              Run complete analysis
  python main.py config               Configure application
        """
    )

    parser.add_argument(
        'command',
        choices=['terminal', 'tui', 'web', 'fetch', 'analyze', 'config'],
        help='Command to execute'
    )

    parser.add_argument(
        '--port',
        type=int,
        help='Port for web interface (default: 5000)'
    )

    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days for data fetching (default: 7)'
    )

    parser.add_argument(
        '--symbols',
        nargs='+',
        help='Symbols to fetch (for fetch command)'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='Gold Digger v1.0.0'
    )

    args = parser.parse_args()

    # Setup environment
    setup_environment()

    # Execute command
    try:
        if args.command == 'terminal':
            launch_terminal()
        elif args.command == 'tui':
            launch_tui()
        elif args.command == 'web':
            launch_web(args.port)
        elif args.command == 'fetch':
            fetch_data(args.days, args.symbols)
        elif args.command == 'analyze':
            run_analysis()
        elif args.command == 'config':
            configure_app()

    except KeyboardInterrupt:
        print("\n👋 Gold Digger shutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
