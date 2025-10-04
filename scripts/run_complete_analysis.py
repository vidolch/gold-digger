#!/usr/bin/env python3
"""
Complete Gold Trading Analysis Runner
This script demonstrates all features of the gold price fetcher and trading analyzer.
"""

import sys
import os
import logging
from datetime import datetime
import argparse

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from src.core.gold_fetcher import GoldPriceFetcher
from src.core.news_fetcher import GoldNewsFetcher
from src.core.news_analyzer import GoldNewsAnalyzer
from src.core.trading_analyzer import TradingAnalyzer
from config.config import get_config

# Get configuration
config = get_config()
logger = logging.getLogger(__name__)


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "-" * 60)
    print(f"  {title}")
    print("-" * 60)


def check_dependencies():
    """Check if all required dependencies are available."""
    try:
        import yfinance
        import pandas
        import ollama
        logger.info("✅ All dependencies are available")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.info("Install missing packages with: pip install -r requirements.txt")
        return False


def check_ollama_setup():
    """Check if Ollama is properly set up."""
    try:
        import ollama
        client = ollama.Client(host=config.ollama_host)
        models = client.list()
        model_names = [model['name'] for model in models['models']]

        if config.ollama_model in model_names:
            logger.info(f"✅ Ollama and {config.ollama_model} model are ready")
            return True
        else:
            logger.warning(f"⚠️  {config.ollama_model} model not found")
            logger.info("Available models: " + ", ".join(model_names))
            logger.info(f"To install the model, run: ollama pull {config.ollama_model}")
            return False
    except Exception as e:
        logger.error(f"❌ Ollama connection failed at {config.ollama_host}: {e}")
        logger.info("Make sure Ollama is running. Install from: https://ollama.ai")
        return False


def run_price_fetching(days=None):
    """Run the price fetching process."""
    print_section("GOLD PRICE DATA FETCHING")

    try:
        fetcher = GoldPriceFetcher()
        fetcher.fetch_and_cache_gold_prices(days=days or config.default_fetch_days)
        fetcher.display_summary()
        return True
    except Exception as e:
        logger.error(f"Error in price fetching: {e}")
        return False


def run_data_analysis():
    """Run basic data analysis."""
    print_section("DATA ANALYSIS")

    try:
        from query_example import GoldDataAnalyzer
        analyzer = GoldDataAnalyzer()

        # Show latest prices
        analyzer.get_latest_prices()

        # Show daily summary
        analyzer.get_daily_summary(days=7)

        # Show price changes
        analyzer.get_price_changes("15m")

        return True
    except Exception as e:
        logger.error(f"Error in data analysis: {e}")
        return False


def run_news_fetching():
    """Run news fetching and caching."""
    print_section("GOLD NEWS FETCHING")

    try:
        news_fetcher = GoldNewsFetcher()
        results = news_fetcher.fetch_and_cache_gold_news()

        total_new = sum(results.values())
        print(f"📰 News fetch results:")
        for symbol, count in results.items():
            print(f"   • {symbol}: {count} new articles")
        print(f"📊 Total new articles: {total_new}")

        # Display news summary
        news_fetcher.display_news_summary()

        return True
    except Exception as e:
        logger.error(f"Error in news fetching: {e}")
        return False


def run_news_analysis():
    """Run comprehensive news analysis."""
    print_section("NEWS SENTIMENT ANALYSIS")

    try:
        news_analyzer = GoldNewsAnalyzer()

        # Generate and display trading-focused news summary
        summary = news_analyzer.generate_news_summary_for_trading(days=3)

        if 'error' not in summary:
            print(f"📊 Overall Assessment: {summary['overall_assessment'].upper()}")
            print(f"📈 Current Sentiment: {summary['overall_sentiment']:.3f}")
            print(f"📰 News Volume: {summary['news_volume']} articles")

            if summary['key_factors']:
                print(f"\n🔑 Key Market Factors:")
                for factor in summary['key_factors']:
                    print(f"   • {factor['category']}: {factor['sentiment']:.2f} sentiment ({factor['impact']} impact)")

            if summary['market_signals']:
                print(f"\n🚨 Market Signals:")
                for signal in summary['market_signals']:
                    print(f"   • {signal}")

            if summary['risk_factors']:
                print(f"\n⚠️ Risk Factors:")
                for risk in summary['risk_factors']:
                    print(f"   • {risk}")
        else:
            print("❌ Insufficient news data for analysis")

        return True
    except Exception as e:
        logger.error(f"Error in news analysis: {e}")
        return False


def run_trading_analysis():
    """Run AI-powered trading analysis with news integration."""
    print_section("AI TRADING ANALYSIS (Price + News)")

    try:
        analyzer = TradingAnalyzer(include_news=True)

        # Get recommendation for different time periods
        intervals = [config.default_interval, "30m"]
        hours = [6, config.default_analysis_hours, 48]  # 6 hours, default hours, 48 hours

        for interval in intervals:
            for hour_period in hours:
                print(f"\n🔍 Analysis: {interval} interval, last {hour_period} hours (with news)")

                recommendation = analyzer.get_trading_recommendation(
                    interval=interval,
                    hours=hour_period
                )

                if recommendation.get('success'):
                    news_included = recommendation.get('news_analysis_included', False)
                    analysis_type = "📰 Price + News" if news_included else "📊 Price Only"
                    print(f"✅ Analysis completed successfully ({analysis_type})")
                    # Save the recommendation
                    analyzer.save_recommendation(recommendation)
                else:
                    print(f"❌ Analysis failed: {recommendation.get('error', 'Unknown error')}")

        # Display the most recent comprehensive analysis
        print_header("COMPREHENSIVE TRADING RECOMMENDATION")
        final_recommendation = analyzer.get_trading_recommendation()
        analyzer.display_recommendation(final_recommendation)

        # Show recommendation history
        print_section("RECENT RECOMMENDATION HISTORY")
        history = analyzer.get_recommendation_history(10)
        if not history.empty:
            print(f"📜 Last {len(history)} recommendations:")
            for _, row in history.iterrows():
                timestamp = row['timestamp'][:19] if row['timestamp'] else 'Unknown'
                price = f"${row['current_price']:.2f}" if row['current_price'] else 'N/A'
                preview = row['recommendation_preview'] if row['recommendation_preview'] else 'No preview'
                print(f"  • {timestamp} - Price: {price}")
                print(f"    {preview}...")
        else:
            print("📝 No previous recommendations found")

        return True
    except Exception as e:
        logger.error(f"Error in trading analysis: {e}")
        return False


def export_data():
    """Export data to CSV files."""
    print_section("DATA EXPORT")

    try:
        from query_example import GoldDataAnalyzer
        analyzer = GoldDataAnalyzer()

        # Export different intervals and time periods
        exports = [
            ("15m", 7, "gold_15m_1week.csv"),
            ("15m", 14, "gold_15m_2weeks.csv"),
            ("30m", 7, "gold_30m_1week.csv"),
            ("30m", 14, "gold_30m_2weeks.csv")
        ]

        for interval, days, filename in exports:
            analyzer.export_to_csv(interval=interval, days=days, filename=filename)

        return True
    except Exception as e:
        logger.error(f"Error in data export: {e}")
        return False


def main():
    """Main function with comprehensive analysis."""
    parser = argparse.ArgumentParser(description='Complete Gold Trading Analysis')
    parser.add_argument('--days', '-d', type=int,
                       help=f'Number of days to fetch (default: {config.default_fetch_days})')
    parser.add_argument('--skip-fetch', action='store_true',
                       help='Skip price fetching')
    parser.add_argument('--skip-news-fetch', action='store_true',
                       help='Skip news fetching')
    parser.add_argument('--skip-analysis', action='store_true',
                       help='Skip data analysis')
    parser.add_argument('--skip-news-analysis', action='store_true',
                       help='Skip news analysis')
    parser.add_argument('--skip-trading', action='store_true',
                       help='Skip AI trading analysis')
    parser.add_argument('--skip-export', action='store_true',
                       help='Skip data export')
    parser.add_argument('--quick', '-q', action='store_true',
                       help='Run quick analysis (fetch + AI trading only)')
    parser.add_argument('--news-only', action='store_true',
                       help='Run only news-related analysis')
    parser.add_argument('--config-summary', action='store_true',
                       help='Show configuration summary and exit')

    args = parser.parse_args()

    if args.config_summary:
        config.print_config_summary()
        return 0

    print_header("🏆 COMPLETE GOLD TRADING ANALYSIS SYSTEM")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check dependencies
    print_section("SYSTEM CHECKS")
    if not check_dependencies():
        return 1

    ollama_ready = check_ollama_setup()

    success_count = 0
    total_steps = 0

    # Handle news-only mode
    if args.news_only:
        print_header("📰 NEWS-ONLY ANALYSIS MODE")

        # News fetching
        if not args.skip_news_fetch:
            total_steps += 1
            if run_news_fetching():
                success_count += 1

        # News analysis
        if not args.skip_news_analysis:
            total_steps += 1
            if run_news_analysis():
                success_count += 1

    else:
        # Step 1: Price Fetching
        if not args.skip_fetch and not args.quick:
            total_steps += 1
            if run_price_fetching(args.days):
                success_count += 1
        elif args.quick:
            total_steps += 1
            if run_price_fetching(args.days):
                success_count += 1

        # Step 2: News Fetching
        if not args.skip_news_fetch and not args.quick:
            total_steps += 1
            if run_news_fetching():
                success_count += 1
        elif args.quick:
            total_steps += 1
            if run_news_fetching():
                success_count += 1

        # Step 3: Basic Data Analysis
        if not args.skip_analysis and not args.quick:
            total_steps += 1
            if run_data_analysis():
                success_count += 1

        # Step 4: News Analysis
        if not args.skip_news_analysis and not args.quick:
            total_steps += 1
            if run_news_analysis():
                success_count += 1

        # Step 5: AI Trading Analysis
        if not args.skip_trading and ollama_ready:
            total_steps += 1
            if run_trading_analysis():
                success_count += 1
        elif not args.skip_trading:
            logger.warning("⚠️  Skipping AI trading analysis - Ollama not ready")

        # Step 6: Data Export
        if not args.skip_export and not args.quick:
            total_steps += 1
            if export_data():
                success_count += 1

    # Final Summary
    print_header("📊 EXECUTION SUMMARY")
    print(f"✅ Successful steps: {success_count}/{total_steps}")
    print(f"🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if success_count == total_steps:
        print("🎉 All analysis completed successfully!")
        print("💡 Next steps:")
        print("  • Review the AI trading recommendations above")
        print("  • Check exported CSV files for detailed data")
        print("  • Monitor news sentiment for market-moving events")
        print("  • Consider your risk tolerance before making any trades")
        print("  • Run this script regularly to get updated analysis")
        print("  • Use --news-only for quick news sentiment updates")
    else:
        print(f"⚠️  {total_steps - success_count} step(s) failed. Check the logs above.")

    print("\n⚠️  IMPORTANT DISCLAIMER:")
    print("This analysis is for educational purposes only. Always do your own research")
    print("and consult with financial professionals before making trading decisions.")

    return 0 if success_count == total_steps else 1


if __name__ == "__main__":
    sys.exit(main())
