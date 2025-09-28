#!/usr/bin/env python3
"""
Web Data Initialization Script
Initialize basic data for the Gold Digger web application.
"""

import sys
import os
import sqlite3
from datetime import datetime, timedelta
import logging

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get configuration
config = get_config()

def init_database():
    """Initialize the database with basic tables."""
    try:
        with sqlite3.connect(config.database_path) as conn:
            cursor = conn.cursor()

            # Create price tables
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

            # Create news table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS gold_news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    summary TEXT,
                    link TEXT UNIQUE,
                    publisher TEXT,
                    published_date TEXT,
                    symbol TEXT,
                    content_hash TEXT UNIQUE,
                    sentiment_score REAL,
                    keywords TEXT,
                    category TEXT,
                    created_at TEXT
                )
            ''')

            conn.commit()
            logger.info("Database tables initialized successfully")

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False

    return True

def create_sample_price_data():
    """Create sample price data for testing."""
    try:
        with sqlite3.connect(config.database_path) as conn:
            cursor = conn.cursor()

            # Check if we already have data
            cursor.execute("SELECT COUNT(*) FROM gold_prices_15m")
            count = cursor.fetchone()[0]

            if count > 0:
                logger.info(f"Price data already exists ({count} records), skipping sample creation")
                return True

            # Create sample data for the last 24 hours
            now = datetime.now()
            base_price = 2650.00

            sample_data = []
            for i in range(96):  # 96 15-minute intervals in 24 hours
                timestamp = now - timedelta(minutes=15 * (96 - i))

                # Generate realistic price movements
                price_change = (i % 20 - 10) * 0.5  # Small random-like movements
                open_price = base_price + price_change
                high_price = open_price + abs(price_change) * 0.3
                low_price = open_price - abs(price_change) * 0.3
                close_price = open_price + (price_change * 0.8)
                volume = 1000 + (i * 10)

                sample_data.append((
                    timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    round(open_price, 2),
                    round(high_price, 2),
                    round(low_price, 2),
                    round(close_price, 2),
                    volume,
                    now.strftime('%Y-%m-%d %H:%M:%S')
                ))

            # Insert sample data
            cursor.executemany('''
                INSERT INTO gold_prices_15m
                (datetime, open, high, low, close, volume, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', sample_data)

            conn.commit()
            logger.info(f"Created {len(sample_data)} sample price records")

    except Exception as e:
        logger.error(f"Error creating sample price data: {e}")
        return False

    return True

def create_sample_news_data():
    """Create sample news data for testing."""
    try:
        with sqlite3.connect(config.database_path) as conn:
            cursor = conn.cursor()

            # Check if we already have data
            cursor.execute("SELECT COUNT(*) FROM gold_news")
            count = cursor.fetchone()[0]

            if count > 0:
                logger.info(f"News data already exists ({count} records), skipping sample creation")
                return True

            # Sample news articles
            sample_news = [
                {
                    'title': 'Gold Prices Rise on Federal Reserve Policy Uncertainty',
                    'summary': 'Gold futures gained as investors sought safe-haven assets amid speculation about Federal Reserve interest rate decisions.',
                    'publisher': 'Reuters',
                    'sentiment_score': 0.3,
                    'category': 'market',
                    'keywords': 'federal reserve,interest rates,safe haven'
                },
                {
                    'title': 'Inflation Data Boosts Gold Demand',
                    'summary': 'Latest inflation figures support gold as hedge against rising prices, driving increased investor interest.',
                    'publisher': 'Bloomberg',
                    'sentiment_score': 0.5,
                    'category': 'economic',
                    'keywords': 'inflation,hedge,demand'
                },
                {
                    'title': 'Central Bank Gold Purchases Continue Strong',
                    'summary': 'Central banks worldwide maintain robust gold purchasing programs, supporting long-term price stability.',
                    'publisher': 'MarketWatch',
                    'sentiment_score': 0.4,
                    'category': 'market',
                    'keywords': 'central banks,purchases,stability'
                },
                {
                    'title': 'Dollar Weakness Supports Gold Rally',
                    'summary': 'Weakening US dollar provides tailwind for gold prices as international buyers find metal more affordable.',
                    'publisher': 'Financial Times',
                    'sentiment_score': 0.6,
                    'category': 'market',
                    'keywords': 'dollar,weakness,rally'
                },
                {
                    'title': 'Geopolitical Tensions Drive Safe Haven Demand',
                    'summary': 'Ongoing geopolitical uncertainties boost demand for gold as investors seek portfolio protection.',
                    'publisher': 'CNBC',
                    'sentiment_score': 0.2,
                    'category': 'political',
                    'keywords': 'geopolitical,tensions,safe haven'
                }
            ]

            now = datetime.now()

            for i, article in enumerate(sample_news):
                published_time = now - timedelta(hours=i * 2)

                cursor.execute('''
                    INSERT INTO gold_news
                    (title, summary, link, publisher, published_date, symbol,
                     content_hash, sentiment_score, keywords, category, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    article['title'],
                    article['summary'],
                    f'https://example.com/article-{i+1}',
                    article['publisher'],
                    published_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'GC=F',
                    f'sample_hash_{i+1}',
                    article['sentiment_score'],
                    article['keywords'],
                    article['category'],
                    now.strftime('%Y-%m-%d %H:%M:%S')
                ))

            conn.commit()
            logger.info(f"Created {len(sample_news)} sample news records")

    except Exception as e:
        logger.error(f"Error creating sample news data: {e}")
        return False

    return True

def main():
    """Main initialization function."""
    logger.info("🚀 Initializing Gold Digger Web Application Data...")

    success = True

    # Initialize database
    if init_database():
        logger.info("✅ Database initialized")
    else:
        logger.error("❌ Database initialization failed")
        success = False

    # Create sample price data
    if create_sample_price_data():
        logger.info("✅ Sample price data ready")
    else:
        logger.error("❌ Sample price data creation failed")
        success = False

    # Create sample news data
    if create_sample_news_data():
        logger.info("✅ Sample news data ready")
    else:
        logger.error("❌ Sample news data creation failed")
        success = False

    if success:
        logger.info("🎉 Web application data initialization complete!")
        logger.info("You can now start the web application with: python gold_digger_web.py")
    else:
        logger.error("❌ Initialization completed with errors")
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())
