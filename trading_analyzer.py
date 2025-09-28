#!/usr/bin/env python3
"""
Trading Analyzer with Ollama Integration
Analyzes gold price data and news sentiment to provide CFD trading recommendations using Ollama's gpt-oss:20b model.
"""

import sqlite3
import pandas as pd
import ollama
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
import os
from config import get_config

# Get configuration
config = get_config()
logger = logging.getLogger(__name__)


class TradingAnalyzer:
    def __init__(self, db_path: Optional[str] = None, prompt_file: Optional[str] = None,
                 ollama_host: Optional[str] = None, include_news: bool = True):
        """Initialize the trading analyzer with database and prompt file paths."""
        self.db_path = db_path or config.database_path
        self.prompt_file = prompt_file or config.prompt_file
        self.model = config.ollama_model
        self.ollama_host = ollama_host or config.ollama_host
        self.ollama_client = ollama.Client(host=self.ollama_host)
        self.include_news = include_news

        # Initialize news analyzer if requested
        if self.include_news:
            try:
                from news_analyzer import GoldNewsAnalyzer
                self.news_analyzer = GoldNewsAnalyzer(self.db_path)
            except ImportError as e:
                logger.warning(f"News analysis not available: {e}")
                self.include_news = False
                self.news_analyzer = None
        else:
            self.news_analyzer = None

        # Check if Ollama is available (unless skip is enabled)
        if not config.skip_model_check:
            self._check_ollama_connection()

    def _check_ollama_connection(self):
        """Check if Ollama is running and the model is available."""
        try:
            models = self.ollama_client.list()
            logger.info(f"Ollama models: {models}")
            model_names = [model['model'] for model in models['models']]

            if self.model not in model_names:
                logger.warning(f"Model {self.model} not found. Available models: {model_names}")
                logger.info(f"To install the model, run: ollama pull {self.model}")

        except Exception as e:
            logger.error(f"Cannot connect to Ollama at {self.ollama_host}: {e}")
            logger.info("Make sure Ollama is running. Install from: https://ollama.ai")
            if not config.debug_mode:
                raise

    def load_prompt_template(self) -> str:
        """Load the prompt template from file."""
        try:
            if not os.path.exists(self.prompt_file):
                logger.error(f"Prompt file {self.prompt_file} not found")
                return ""

            with open(self.prompt_file, 'r', encoding='utf-8') as f:
                return f.read()

        except Exception as e:
            logger.error(f"Error loading prompt template: {e}")
            return ""

    def get_recent_market_data(self, interval: str = "15m", hours: int = 24) -> pd.DataFrame:
        """Get recent market data from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                table_name = f"gold_prices_{interval}"

                # Get recent data from database
                query = f"""
                    SELECT datetime, open, high, low, close, volume
                    FROM {table_name}
                    ORDER BY datetime DESC
                    LIMIT 500
                """

                df = pd.read_sql_query(query, conn)

                if not df.empty:
                    df['datetime'] = pd.to_datetime(df['datetime'])

                    # Make start_time timezone-aware to match database datetime format
                    end_time = datetime.now()
                    start_time = end_time - timedelta(hours=hours)

                    # Convert start_time to match the timezone of the first record
                    first_record_tz = df.iloc[0]['datetime'].tz
                    if first_record_tz is not None:
                        # Make start_time timezone-aware using the same timezone as the data
                        if start_time.tzinfo is None:
                            start_time = start_time.replace(tzinfo=first_record_tz)
                        else:
                            start_time = start_time.astimezone(first_record_tz)

                    # Try to filter to the requested time range
                    try:
                        filtered_df = df[df['datetime'] >= start_time]
                    except Exception as e:
                        logger.warning(f"Timezone comparison failed: {e}. Using all recent data.")
                        filtered_df = pd.DataFrame()

                    if not filtered_df.empty:
                        logger.info(f"Retrieved {len(filtered_df)} records for {interval} interval from last {hours} hours")
                        return filtered_df
                    else:
                        # Fallback: use the most recent available data
                        recent_df = df.head(min(100, len(df)))  # Get up to 100 most recent records
                        if len(recent_df) > 1:
                            latest_time = recent_df.iloc[0]['datetime']
                            oldest_time = recent_df.iloc[-1]['datetime']
                            actual_hours = (latest_time - oldest_time).total_seconds() / 3600
                            logger.warning(f"No data found for last {hours} hours. Using {len(recent_df)} most recent records spanning {actual_hours:.1f} hours")
                        else:
                            logger.warning(f"Using {len(recent_df)} most recent records")
                        return recent_df
                else:
                    logger.error("No data found in database")
                    return pd.DataFrame()

        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return pd.DataFrame()

    def format_market_data(self, df: pd.DataFrame) -> str:
        """Format market data for the AI prompt."""
        if df.empty:
            return "No recent market data available."

        # Sort by datetime (most recent first)
        df_sorted = df.sort_values('datetime', ascending=False)

        # Get latest price info
        latest = df_sorted.iloc[0]
        oldest = df_sorted.iloc[-1]

        # Calculate statistics
        current_price = latest['close']
        price_change = current_price - oldest['close']
        price_change_pct = (price_change / oldest['close']) * 100

        high_24h = df['high'].max()
        low_24h = df['low'].min()
        avg_volume = df['volume'].mean()

        # Create formatted data string
        market_summary = f"""
**CURRENT PRICE DATA:**
- Latest Price: ${current_price:.2f}
- 24h Change: ${price_change:+.2f} ({price_change_pct:+.2f}%)
- 24h High: ${high_24h:.2f}
- 24h Low: ${low_24h:.2f}
- Average Volume: {avg_volume:,.0f}

**RECENT PRICE HISTORY (Last 20 data points):**
"""

        # Add recent price points
        for i, row in df_sorted.head(20).iterrows():
            timestamp = row['datetime'].strftime('%Y-%m-%d %H:%M')
            market_summary += f"- {timestamp}: O=${row['open']:.2f} H=${row['high']:.2f} L=${row['low']:.2f} C=${row['close']:.2f} V={row['volume']:,.0f}\n"

        # Add price trend analysis
        if len(df_sorted) >= 10:
            recent_10 = df_sorted.head(10)['close'].mean()
            older_10 = df_sorted.tail(10)['close'].mean()
            trend_direction = "UPWARD" if recent_10 > older_10 else "DOWNWARD"
            trend_strength = abs(recent_10 - older_10) / older_10 * 100

            market_summary += f"""
**TREND ANALYSIS:**
- Short-term Trend: {trend_direction}
- Trend Strength: {trend_strength:.2f}%
- Volatility (24h): {((high_24h - low_24h) / current_price * 100):.2f}%
"""

        return market_summary

    def get_trading_recommendation(self, interval: Optional[str] = None, hours: Optional[int] = None) -> Dict[str, Any]:
        """Get trading recommendation from Ollama model."""
        # Use config defaults if not specified
        interval = interval or config.default_interval
        hours = hours or config.default_analysis_hours

        try:
            # Get market data
            market_data = self.get_recent_market_data(interval, hours)
            if market_data.empty:
                return {
                    "error": "No market data available",
                    "recommendation": None,
                    "timestamp": datetime.now().isoformat()
                }

            # Load and format prompt
            prompt_template = self.load_prompt_template()
            if not prompt_template:
                return {
                    "error": "Could not load prompt template",
                    "recommendation": None,
                    "timestamp": datetime.now().isoformat()
                }

            # Format market data for prompt
            formatted_data = self.format_market_data(market_data)

            # Include news analysis if available
            news_analysis = ""
            if self.include_news and self.news_analyzer:
                try:
                    news_analysis = self.news_analyzer.format_news_for_prompt(hours)
                    logger.info("News analysis included in trading recommendation")
                except Exception as e:
                    logger.warning(f"Failed to include news analysis: {e}")
                    news_analysis = ""

            # Combine market data and news analysis
            combined_data = formatted_data
            if news_analysis:
                combined_data += f"\n\n{news_analysis}"

            full_prompt = prompt_template.format(market_data=combined_data)

            logger.info("Sending request to Ollama...")

            # Send request to Ollama
            response = self.ollama_client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                options={
                    "temperature": 0.7,
                    "num_predict": 1000
                }
            )

            recommendation_text = response['message']['content']

            return {
                "success": True,
                "recommendation": recommendation_text,
                "market_data_points": len(market_data),
                "analysis_period": f"{hours} hours",
                "interval": interval,
                "timestamp": datetime.now().isoformat(),
                "current_price": market_data.iloc[0]['close'] if not market_data.empty else None,
                "news_analysis_included": self.include_news and bool(news_analysis)
            }

        except Exception as e:
            logger.error(f"Error getting trading recommendation: {e}")
            return {
                "error": str(e),
                "recommendation": None,
                "timestamp": datetime.now().isoformat()
            }

    def save_recommendation(self, recommendation_data: Dict[str, Any]):
        """Save recommendation to database for historical tracking."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create recommendations table if it doesn't exist
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS trading_recommendations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        interval_used TEXT,
                        hours_analyzed INTEGER,
                        current_price REAL,
                        recommendation TEXT,
                        market_data_points INTEGER,
                        success BOOLEAN,
                        error_message TEXT
                    )
                ''')

                # Insert recommendation
                cursor.execute('''
                    INSERT INTO trading_recommendations
                    (timestamp, interval_used, hours_analyzed, current_price,
                     recommendation, market_data_points, success, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    recommendation_data.get('timestamp'),
                    recommendation_data.get('interval'),
                    recommendation_data.get('analysis_period', '').split()[0] if 'analysis_period' in recommendation_data else None,
                    recommendation_data.get('current_price'),
                    recommendation_data.get('recommendation'),
                    recommendation_data.get('market_data_points'),
                    recommendation_data.get('success', False),
                    recommendation_data.get('error')
                ))

                conn.commit()
                logger.info("Recommendation saved to database")

        except sqlite3.Error as e:
            logger.error(f"Error saving recommendation: {e}")

    def display_recommendation(self, recommendation_data: Dict[str, Any]):
        """Display the trading recommendation in a formatted way."""
        print("\n" + "=" * 80)
        print("🏆 GOLD TRADING ANALYSIS & RECOMMENDATION")
        print("=" * 80)

        if recommendation_data.get('error'):
            print(f"❌ Error: {recommendation_data['error']}")
            return

        print(f"📊 Analysis Time: {recommendation_data['timestamp']}")
        print(f"📈 Current Gold Price: ${recommendation_data.get('current_price', 'N/A'):.2f}")
        print(f"⏱️  Data Period: {recommendation_data.get('analysis_period', 'N/A')}")
        print(f"📋 Data Points Analyzed: {recommendation_data.get('market_data_points', 0)}")
        print(f"🔄 Interval: {recommendation_data.get('interval', 'N/A')}")

        # Show news analysis status
        news_included = recommendation_data.get('news_analysis_included', False)
        news_icon = "📰" if news_included else "📊"
        news_status = "News + Price Analysis" if news_included else "Price Analysis Only"
        print(f"{news_icon} Analysis Type: {news_status}")

        print("\n" + "-" * 80)
        print("🤖 AI TRADING RECOMMENDATION:")
        print("-" * 80)

        if recommendation_data.get('recommendation'):
            print(recommendation_data['recommendation'])
        else:
            print("No recommendation available.")

        print("\n" + "=" * 80)
        print("⚠️  DISCLAIMER: This is for educational purposes only. Always do your own research and consider your risk tolerance before trading.")
        print("=" * 80)

    def get_recommendation_history(self, limit: int = 10) -> pd.DataFrame:
        """Get historical recommendations from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT timestamp, interval_used, current_price, success,
                           SUBSTR(recommendation, 1, 100) as recommendation_preview
                    FROM trading_recommendations
                    WHERE success = 1
                    ORDER BY timestamp DESC
                    LIMIT ?
                '''

                df = pd.read_sql_query(query, conn, params=(limit,))
                return df

        except sqlite3.Error as e:
            logger.error(f"Error getting recommendation history: {e}")
            return pd.DataFrame()


def main():
    """Main function to run trading analysis."""
    import argparse

    parser = argparse.ArgumentParser(description='AI-powered Gold Trading Analysis')
    parser.add_argument('--config-summary', action='store_true',
                       help='Show configuration summary and exit')
    parser.add_argument('--interval', choices=['15m', '30m'],
                       help=f'Price data interval (default: {config.default_interval})')
    parser.add_argument('--hours', type=int,
                       help=f'Hours of data to analyze (default: {config.default_analysis_hours})')
    parser.add_argument('--no-news', action='store_true',
                       help='Exclude news analysis from recommendation')
    parser.add_argument('--fetch-news', action='store_true',
                       help='Fetch latest news before analysis')

    args = parser.parse_args()

    if args.config_summary:
        config.print_config_summary()
        return

    # Fetch news if requested
    if args.fetch_news:
        try:
            from news_fetcher import GoldNewsFetcher
            logger.info("Fetching latest gold news...")
            news_fetcher = GoldNewsFetcher()
            results = news_fetcher.fetch_and_cache_gold_news()
            total_new = sum(results.values())
            logger.info(f"Fetched {total_new} new articles")
        except ImportError as e:
            logger.warning(f"News fetching not available: {e}")
        except Exception as e:
            logger.error(f"Error fetching news: {e}")

    analyzer = TradingAnalyzer(include_news=not args.no_news)

    try:
        # Get trading recommendation
        logger.info(f"Getting trading recommendation using {config.ollama_host}...")
        recommendation = analyzer.get_trading_recommendation(interval=args.interval, hours=args.hours)

        # Display recommendation
        analyzer.display_recommendation(recommendation)

        # Save to database
        analyzer.save_recommendation(recommendation)

        # Optionally show recent history
        print(f"\n📜 Recent Recommendation History:")
        history = analyzer.get_recommendation_history(5)
        if not history.empty:
            for _, row in history.iterrows():
                print(f"• {row['timestamp'][:19]} - Price: ${row['current_price']:.2f} - {row['recommendation_preview']}...")

    except Exception as e:
        logger.error(f"Error in main execution: {e}")


if __name__ == "__main__":
    main()
