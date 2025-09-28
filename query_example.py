#!/usr/bin/env python3
"""
Example script showing how to query cached gold price data.
Demonstrates various ways to analyze the cached data.
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import sys

class GoldDataAnalyzer:
    def __init__(self, db_path: str = "gold_prices.db"):
        """Initialize the analyzer with the database path."""
        self.db_path = db_path

    def get_latest_prices(self):
        """Get the latest gold prices for both intervals."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get latest 15m price
                query_15m = '''
                    SELECT datetime, close FROM gold_prices_15m
                    ORDER BY datetime DESC LIMIT 1
                '''

                # Get latest 30m price
                query_30m = '''
                    SELECT datetime, close FROM gold_prices_30m
                    ORDER BY datetime DESC LIMIT 1
                '''

                latest_15m = pd.read_sql_query(query_15m, conn)
                latest_30m = pd.read_sql_query(query_30m, conn)

                print("LATEST GOLD PRICES")
                print("=" * 30)

                if not latest_15m.empty:
                    print(f"15m interval: ${latest_15m.iloc[0]['close']:.2f} at {latest_15m.iloc[0]['datetime']}")

                if not latest_30m.empty:
                    print(f"30m interval: ${latest_30m.iloc[0]['close']:.2f} at {latest_30m.iloc[0]['datetime']}")

        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def get_daily_summary(self, days: int = 7):
        """Get daily high, low, and close for the last N days."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)

                query = '''
                    SELECT
                        DATE(datetime) as date,
                        MAX(high) as daily_high,
                        MIN(low) as daily_low,
                        AVG(close) as avg_close,
                        COUNT(*) as records
                    FROM gold_prices_15m
                    WHERE datetime >= ? AND datetime <= ?
                    GROUP BY DATE(datetime)
                    ORDER BY date DESC
                '''

                df = pd.read_sql_query(query, conn, params=(start_date.isoformat(), end_date.isoformat()))

                print(f"\nDAILY SUMMARY (Last {days} days)")
                print("=" * 50)

                for _, row in df.iterrows():
                    print(f"{row['date']}: High=${row['daily_high']:.2f}, Low=${row['daily_low']:.2f}, Avg=${row['avg_close']:.2f}")

                return df

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return pd.DataFrame()

    def get_price_changes(self, interval: str = "15m"):
        """Calculate price changes over different periods."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                table_name = f"gold_prices_{interval}"

                query = f'''
                    SELECT datetime, close
                    FROM {table_name}
                    ORDER BY datetime DESC
                    LIMIT 100
                '''

                df = pd.read_sql_query(query, conn)
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df.sort_values('datetime')

                if len(df) < 2:
                    print("Not enough data for price change analysis")
                    return

                current_price = df.iloc[-1]['close']

                # Calculate changes
                changes = {
                    '1 hour ago': self._get_price_at_time_ago(df, hours=1),
                    '4 hours ago': self._get_price_at_time_ago(df, hours=4),
                    '24 hours ago': self._get_price_at_time_ago(df, hours=24),
                }

                print(f"\nPRICE CHANGES ({interval.upper()} data)")
                print("=" * 30)
                print(f"Current price: ${current_price:.2f}")

                for period, past_price in changes.items():
                    if past_price:
                        change = current_price - past_price
                        change_pct = (change / past_price) * 100
                        direction = "↑" if change > 0 else "↓" if change < 0 else "→"
                        print(f"{period}: {direction} ${change:+.2f} ({change_pct:+.2f}%)")

        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def _get_price_at_time_ago(self, df, hours: int):
        """Helper function to get price from N hours ago."""
        target_time = df.iloc[-1]['datetime'] - timedelta(hours=hours)

        # Find the closest record to the target time
        df['time_diff'] = abs(df['datetime'] - target_time)
        closest_idx = df['time_diff'].idxmin()

        return df.loc[closest_idx, 'close']

    def export_to_csv(self, interval: str = "15m", days: int = 14, filename: str = None):
        """Export cached data to CSV file."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                table_name = f"gold_prices_{interval}"
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)

                query = f'''
                    SELECT datetime, open, high, low, close, volume
                    FROM {table_name}
                    WHERE datetime >= ? AND datetime <= ?
                    ORDER BY datetime
                '''

                df = pd.read_sql_query(query, conn, params=(start_date.isoformat(), end_date.isoformat()))

                if filename is None:
                    filename = f"gold_prices_{interval}_{days}days.csv"

                df.to_csv(filename, index=False)
                print(f"\nExported {len(df)} records to {filename}")

        except Exception as e:
            print(f"Export error: {e}")

    def plot_price_trend(self, interval: str = "30m", days: int = 7):
        """Create a simple price trend plot."""
        try:
            import matplotlib.pyplot as plt

            with sqlite3.connect(self.db_path) as conn:
                table_name = f"gold_prices_{interval}"
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)

                query = f'''
                    SELECT datetime, close
                    FROM {table_name}
                    WHERE datetime >= ? AND datetime <= ?
                    ORDER BY datetime
                '''

                df = pd.read_sql_query(query, conn, params=(start_date.isoformat(), end_date.isoformat()))

                if df.empty:
                    print("No data available for plotting")
                    return

                df['datetime'] = pd.to_datetime(df['datetime'])

                plt.figure(figsize=(12, 6))
                plt.plot(df['datetime'], df['close'], linewidth=1)
                plt.title(f'Gold Price Trend - Last {days} days ({interval} intervals)')
                plt.xlabel('Date/Time')
                plt.ylabel('Price (USD)')
                plt.xticks(rotation=45)
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

                filename = f"gold_price_trend_{interval}_{days}days.png"
                plt.savefig(filename, dpi=300, bbox_inches='tight')
                print(f"\nPrice trend chart saved as {filename}")
                plt.show()

        except ImportError:
            print("Matplotlib not installed. Install with: pip install matplotlib")
        except Exception as e:
            print(f"Plotting error: {e}")


def main():
    """Main function demonstrating various data queries."""
    analyzer = GoldDataAnalyzer()

    print("GOLD PRICE DATA ANALYSIS")
    print("=" * 40)

    # Get latest prices
    analyzer.get_latest_prices()

    # Get daily summary
    analyzer.get_daily_summary(days=7)

    # Show price changes
    analyzer.get_price_changes("15m")

    # Export data to CSV
    analyzer.export_to_csv("15m", days=7, filename="recent_gold_prices.csv")

    # Uncomment the line below to create a price trend chart
    # analyzer.plot_price_trend("30m", days=3)

    print("\n" + "=" * 40)
    print("Analysis complete!")


if __name__ == "__main__":
    main()
