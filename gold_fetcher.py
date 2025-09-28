#!/usr/bin/env python3
"""
Gold Price Fetcher with SQLite Caching
Fetches gold prices (GC=F) in 15m and 30m intervals for the last 14 days.
Caches results in SQLite to avoid duplicate API calls.
"""

import sqlite3
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
import sys
from typing import Optional, Tuple
import argparse
from config import get_config

# Get configuration
config = get_config()
logger = logging.getLogger(__name__)

class GoldPriceFetcher:
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the gold price fetcher with SQLite database."""
        self.db_path = db_path or config.database_path
        self.symbol = config.gold_symbol
        self.init_database()

    def init_database(self):
        """Initialize the SQLite database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create table for 15m intervals
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS gold_prices_15m (
                        datetime TEXT PRIMARY KEY,
                        open REAL,
                        high REAL,
                        low REAL,
                        close REAL,
                        volume INTEGER,
                        created_at TEXT
                    )
                ''')

                # Create table for 30m intervals
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS gold_prices_30m (
                        datetime TEXT PRIMARY KEY,
                        open REAL,
                        high REAL,
                        low REAL,
                        close REAL,
                        volume INTEGER,
                        created_at TEXT
                    )
                ''')

                conn.commit()
                logger.info(f"Database initialized at {self.db_path}")

        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            sys.exit(1)

    def get_cached_date_range(self, interval: str) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Get the date range of cached data for a specific interval."""
        table_name = f"gold_prices_{interval}"

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    SELECT MIN(datetime), MAX(datetime)
                    FROM {table_name}
                ''')

                result = cursor.fetchone()
                if result and result[0] and result[1]:
                    min_date = datetime.fromisoformat(result[0])
                    max_date = datetime.fromisoformat(result[1])
                    return min_date, max_date

                return None, None

        except sqlite3.Error as e:
            logger.error(f"Error getting cached date range: {e}")
            return None, None

    def get_missing_date_ranges(self, interval: str, start_date: datetime, end_date: datetime) -> list:
        """Identify date ranges that need to be fetched."""
        cached_min, cached_max = self.get_cached_date_range(interval)

        if cached_min is None or cached_max is None:
            # No cached data, fetch everything
            return [(start_date, end_date)]

        missing_ranges = []

        # Check if we need data before the cached range
        if start_date < cached_min:
            missing_ranges.append((start_date, cached_min - timedelta(minutes=1)))

        # Check if we need data after the cached range
        if end_date > cached_max:
            missing_ranges.append((cached_max + timedelta(minutes=1), end_date))

        return missing_ranges

    def fetch_gold_data(self, start_date: datetime, end_date: datetime, interval: str) -> Optional[pd.DataFrame]:
        """Fetch gold price data from yfinance."""
        try:
            if config.use_mock_data:
                logger.info(f"Using mock data for {interval} interval")
                return self._get_mock_data(start_date, end_date, interval)

            logger.info(f"Fetching {interval} data from {start_date} to {end_date}")

            # Add delay for rate limiting
            if config.api_delay > 0:
                import time
                time.sleep(config.api_delay)

            ticker = yf.Ticker(self.symbol)
            data = ticker.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=(end_date + timedelta(days=1)).strftime('%Y-%m-%d'),
                interval=interval,
                prepost=True,
                actions=False,
                timeout=config.yfinance_timeout
            )

            if data.empty:
                logger.warning(f"No data received for {interval} interval")
                return None

            # Reset index to make datetime a column
            data.reset_index(inplace=True)

            # Convert datetime to string for SQLite storage
            data['Datetime'] = data['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S%z')

            logger.info(f"Fetched {len(data)} records for {interval} interval")
            return data

        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            # Retry logic
            retries = 0
            while retries < config.max_retries:
                retries += 1
                logger.info(f"Retrying... ({retries}/{config.max_retries})")
                try:
                    import time
                    time.sleep(config.api_delay * retries)  # Exponential backoff

                    ticker = yf.Ticker(self.symbol)
                    data = ticker.history(
                        start=start_date.strftime('%Y-%m-%d'),
                        end=(end_date + timedelta(days=1)).strftime('%Y-%m-%d'),
                        interval=interval,
                        prepost=True,
                        actions=False,
                        timeout=config.yfinance_timeout
                    )

                    if not data.empty:
                        data.reset_index(inplace=True)
                        data['Datetime'] = data['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S%z')
                        logger.info(f"Retry successful: Fetched {len(data)} records for {interval} interval")
                        return data
                except Exception as retry_e:
                    logger.warning(f"Retry {retries} failed: {retry_e}")

            logger.error(f"All retries failed for {interval} interval")
            return None

    def _get_mock_data(self, start_date: datetime, end_date: datetime, interval: str) -> Optional[pd.DataFrame]:
        """Generate mock data for testing purposes."""
        import pandas as pd
        import numpy as np

        # Generate time range based on interval
        if interval == "15m":
            freq = "15T"
        elif interval == "30m":
            freq = "30T"
        else:
            freq = "1H"

        dates = pd.date_range(start=start_date, end=end_date, freq=freq)

        # Generate mock price data around $2000
        base_price = 2000.0
        price_data = []

        for i, date in enumerate(dates):
            # Add some random walk behavior
            change = np.random.normal(0, 5)  # Random price movement
            current_price = base_price + change

            # Create OHLC data
            open_price = current_price
            high_price = current_price + abs(np.random.normal(0, 2))
            low_price = current_price - abs(np.random.normal(0, 2))
            close_price = current_price + np.random.normal(0, 1)
            volume = int(np.random.normal(10000, 2000))

            price_data.append({
                'Datetime': date.strftime('%Y-%m-%d %H:%M:%S%z'),
                'Open': round(open_price, 2),
                'High': round(high_price, 2),
                'Low': round(low_price, 2),
                'Close': round(close_price, 2),
                'Volume': max(volume, 1000)  # Ensure positive volume
            })

            base_price = close_price  # Update base for next iteration

        return pd.DataFrame(price_data)

    def save_to_database(self, data: pd.DataFrame, interval: str):
        """Save fetched data to SQLite database."""
        if data is None or data.empty:
            return

        table_name = f"gold_prices_{interval}"
        current_time = datetime.now().isoformat()

        try:
            with sqlite3.connect(self.db_path) as conn:
                # Prepare data for insertion
                records = []
                for _, row in data.iterrows():
                    records.append((
                        row['Datetime'],
                        row['Open'],
                        row['High'],
                        row['Low'],
                        row['Close'],
                        row['Volume'],
                        current_time
                    ))

                cursor = conn.cursor()
                cursor.executemany(f'''
                    INSERT OR REPLACE INTO {table_name}
                    (datetime, open, high, low, close, volume, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', records)

                conn.commit()
                logger.info(f"Saved {len(records)} records to {table_name}")

        except sqlite3.Error as e:
            logger.error(f"Error saving to database: {e}")

    def get_cached_data(self, interval: str, days: int = 14) -> pd.DataFrame:
        """Retrieve cached data from database."""
        table_name = f"gold_prices_{interval}"
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        try:
            with sqlite3.connect(self.db_path) as conn:
                query = f'''
                    SELECT datetime, open, high, low, close, volume
                    FROM {table_name}
                    WHERE datetime >= ? AND datetime <= ?
                    ORDER BY datetime
                '''

                df = pd.read_sql_query(
                    query,
                    conn,
                    params=(start_date.isoformat(), end_date.isoformat())
                )

                if not df.empty:
                    df['datetime'] = pd.to_datetime(df['datetime'])

                return df

        except sqlite3.Error as e:
            logger.error(f"Error retrieving cached data: {e}")
            return pd.DataFrame()

    def fetch_and_cache_gold_prices(self, days: Optional[int] = None):
        """Main method to fetch and cache gold prices for both intervals."""
        days = days or config.default_fetch_days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        logger.info(f"Starting gold price fetch for last {days} days")
        logger.info(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

        intervals = ["15m", "30m"]

        for interval in intervals:
            logger.info(f"\n--- Processing {interval} interval ---")

            # Check what data we already have
            missing_ranges = self.get_missing_date_ranges(interval, start_date, end_date)

            if not missing_ranges:
                logger.info(f"All {interval} data is already cached")
                continue

            # Fetch missing data
            for missing_start, missing_end in missing_ranges:
                data = self.fetch_gold_data(missing_start, missing_end, interval)
                if data is not None:
                    self.save_to_database(data, interval)

    def display_summary(self):
        """Display a summary of cached data."""
        print("\n" + "="*60)
        print("GOLD PRICE CACHE SUMMARY")
        print("="*60)

        for interval in ["15m", "30m"]:
            cached_data = self.get_cached_data(interval)

            if not cached_data.empty:
                latest_price = cached_data.iloc[-1]['close']
                earliest_date = cached_data.iloc[0]['datetime']
                latest_date = cached_data.iloc[-1]['datetime']
                record_count = len(cached_data)

                print(f"\n{interval.upper()} INTERVAL DATA:")
                print(f"  Records: {record_count}")
                print(f"  Date range: {earliest_date} to {latest_date}")
                print(f"  Latest price: ${latest_price:.2f}")
            else:
                print(f"\n{interval.upper()} INTERVAL DATA: No data available")


def main():
    """Main function to run the gold price fetcher."""
    parser = argparse.ArgumentParser(description='Gold Price Fetcher and Trading Analyzer')
    parser.add_argument('--analyze', '-a', action='store_true',
                       help='Run trading analysis after fetching prices')
    parser.add_argument('--days', '-d', type=int,
                       help=f'Number of days to fetch (default: {config.default_fetch_days})')
    parser.add_argument('--skip-fetch', action='store_true',
                       help='Skip price fetching and only run analysis')
    parser.add_argument('--config-summary', action='store_true',
                       help='Show configuration summary and exit')

    args = parser.parse_args()

    if args.config_summary:
        config.print_config_summary()
        return

    try:
        fetcher = GoldPriceFetcher()

        if not args.skip_fetch:
            fetcher.fetch_and_cache_gold_prices(days=args.days)
            fetcher.display_summary()

        if args.analyze:
            try:
                from trading_analyzer import TradingAnalyzer
                logger.info("Running trading analysis...")
                analyzer = TradingAnalyzer()
                recommendation = analyzer.get_trading_recommendation()
                analyzer.display_recommendation(recommendation)
                analyzer.save_recommendation(recommendation)
            except ImportError as e:
                logger.error(f"Could not import trading analyzer: {e}")
                logger.info("Make sure trading_analyzer.py is in the same directory")
            except Exception as e:
                logger.error(f"Error running trading analysis: {e}")

    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
