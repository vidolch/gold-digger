#!/usr/bin/env python3
"""
Gold News Fetcher with SQLite Caching
Fetches gold-related news articles and intelligently caches them in SQLite to avoid duplicate API calls.
"""

import sqlite3
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
import sys
import hashlib
import json
from typing import Optional, Dict, List, Any
import time
from config import get_config

# Get configuration
config = get_config()
logger = logging.getLogger(__name__)


class GoldNewsFetcher:
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the gold news fetcher with SQLite database."""
        self.db_path = db_path or config.database_path
        self.symbols = config.news_symbols  # Use configured news symbols
        self.init_database()

    def init_database(self):
        """Initialize the SQLite database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create table for news articles
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
                        created_at TEXT,
                        updated_at TEXT
                    )
                ''')

                # Create index for faster searches
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_published_date
                    ON gold_news(published_date)
                ''')

                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_symbol
                    ON gold_news(symbol)
                ''')

                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_keywords
                    ON gold_news(keywords)
                ''')

                # Create table for news fetch history
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS news_fetch_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT,
                        fetch_date TEXT,
                        articles_count INTEGER,
                        success BOOLEAN,
                        error_message TEXT,
                        created_at TEXT
                    )
                ''')

                conn.commit()
                logger.info(f"News database initialized at {self.db_path}")

        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            sys.exit(1)

    def _generate_content_hash(self, title: str, summary: str, link: str) -> str:
        """Generate a unique hash for news content to avoid duplicates."""
        content = f"{title}{summary}{link}".encode('utf-8')
        return hashlib.md5(content).hexdigest()

    def _extract_keywords(self, title: str, summary: str) -> List[str]:
        """Extract relevant keywords from news content."""
        if not config.auto_categorize_news:
            return []

        gold_keywords = [
            'gold', 'precious metals', 'bullion', 'mining', 'fed', 'inflation',
            'dollar', 'economy', 'market', 'price', 'trading', 'investment',
            'central bank', 'interest rates', 'commodity', 'futures'
        ]

        text = f"{title} {summary}".lower()
        found_keywords = [keyword for keyword in gold_keywords if keyword in text]
        return found_keywords

    def _categorize_news(self, title: str, summary: str) -> str:
        """Categorize news article based on content."""
        if not config.auto_categorize_news:
            return 'general'

        text = f"{title} {summary}".lower()

        if any(word in text for word in ['fed', 'federal reserve', 'interest rate', 'monetary policy']):
            return 'monetary_policy'
        elif any(word in text for word in ['mining', 'production', 'supply']):
            return 'supply_demand'
        elif any(word in text for word in ['trading', 'price', 'market', 'rally', 'drop']):
            return 'market_movement'
        elif any(word in text for word in ['geopolitical', 'war', 'crisis', 'tension']):
            return 'geopolitical'
        elif any(word in text for word in ['economic', 'gdp', 'employment', 'inflation']):
            return 'economic_data'
        else:
            return 'general'

    def _calculate_sentiment_score(self, title: str, summary: str) -> float:
        """Simple sentiment analysis based on keyword matching."""
        if not config.enable_sentiment_analysis:
            return 0.0

        text = f"{title} {summary}".lower()

        positive_words = [
            'surge', 'rally', 'rise', 'gain', 'up', 'bullish', 'strong', 'high',
            'increase', 'boost', 'positive', 'optimistic', 'buy', 'support'
        ]

        negative_words = [
            'fall', 'drop', 'decline', 'down', 'bearish', 'weak', 'low',
            'decrease', 'crash', 'negative', 'pessimistic', 'sell', 'pressure'
        ]

        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)

        total_words = len(text.split())
        if total_words == 0:
            return 0.0

        # Simple sentiment score between -1 and 1
        sentiment = (positive_count - negative_count) / max(total_words * 0.1, 1)
        return max(-1.0, min(1.0, sentiment))

    def fetch_news_for_symbol(self, symbol: str, max_articles: int = 50) -> List[Dict[str, Any]]:
        """Fetch news for a specific symbol using yfinance."""
        try:
            if config.use_mock_news:
                logger.info(f"Using mock news data for symbol: {symbol}")
                return self._get_mock_news(symbol, max_articles)

            logger.info(f"Fetching news for symbol: {symbol}")

            # Add delay for rate limiting
            if config.api_delay > 0:
                time.sleep(config.api_delay)

            ticker = yf.Ticker(symbol)
            news_data = ticker.news

            if not news_data:
                logger.warning(f"No news found for symbol: {symbol}")
                return []

            processed_news = []
            for article in news_data[:max_articles]:
                try:
                    # Extract article data from nested content structure
                    content = article.get('content', article)  # Handle both old and new formats
                    title = content.get('title', 'No Title')
                    summary = content.get('summary', content.get('description', ''))

                    # Get link from different possible locations
                    if 'clickThroughUrl' in content and content['clickThroughUrl']:
                        link = content['clickThroughUrl'].get('url', '')
                    elif 'canonicalUrl' in content and content['canonicalUrl']:
                        link = content['canonicalUrl'].get('url', '')
                    else:
                        link = content.get('link', '')

                    # Get publisher
                    if 'provider' in content and content['provider']:
                        publisher = content['provider'].get('displayName', 'Unknown')
                    else:
                        publisher = content.get('publisher', 'Unknown')

                    # Convert timestamp to datetime - handle different timestamp formats
                    published_timestamp = None
                    if 'pubDate' in content:
                        # Handle ISO format timestamp
                        try:
                            pub_date_str = content['pubDate']
                            if pub_date_str.endswith('Z'):
                                pub_date_str = pub_date_str[:-1] + '+00:00'
                            published_date = datetime.fromisoformat(pub_date_str).isoformat()
                        except:
                            published_date = datetime.now().isoformat()
                    elif 'providerPublishTime' in content:
                        # Handle Unix timestamp
                        published_timestamp = content.get('providerPublishTime', 0)
                        published_date = datetime.fromtimestamp(published_timestamp).isoformat() if published_timestamp else datetime.now().isoformat()
                    else:
                        published_date = datetime.now().isoformat()

                    # Generate content hash
                    content_hash = self._generate_content_hash(title, summary, link)

                    # Extract additional metadata
                    keywords = self._extract_keywords(title, summary)
                    category = self._categorize_news(title, summary)
                    sentiment_score = self._calculate_sentiment_score(title, summary)

                    processed_article = {
                        'title': title,
                        'summary': summary,
                        'link': link,
                        'publisher': publisher,
                        'published_date': published_date,
                        'symbol': symbol,
                        'content_hash': content_hash,
                        'sentiment_score': sentiment_score,
                        'keywords': json.dumps(keywords),
                        'category': category
                    }

                    processed_news.append(processed_article)

                except Exception as e:
                    logger.warning(f"Error processing article: {e}")
                    continue

            logger.info(f"Processed {len(processed_news)} articles for {symbol}")
            return processed_news

        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return []

    def _get_mock_news(self, symbol: str, max_articles: int) -> List[Dict[str, Any]]:
        """Generate mock news data for testing."""
        import random

        mock_titles = [
            f"Gold prices surge as {symbol} shows strong momentum",
            f"{symbol} drops amid market uncertainty",
            f"Federal Reserve decision impacts {symbol} trading",
            f"Mining sector update affects {symbol} outlook",
            f"{symbol} reaches key resistance level",
            f"Economic data supports {symbol} bull case",
            f"Geopolitical tensions drive {symbol} higher",
            f"{symbol} consolidates after recent rally"
        ]

        mock_summaries = [
            "Market analysts see continued strength in precious metals sector",
            "Technical indicators suggest potential reversal in gold market",
            "Central bank policies create volatility in commodity markets",
            "Supply chain disruptions affect precious metals production",
            "Institutional investors increase gold allocations",
            "Inflation concerns drive safe-haven demand"
        ]

        mock_publishers = ["MarketWatch", "Reuters", "Bloomberg", "Yahoo Finance", "CNBC"]

        mock_articles = []
        for i in range(min(max_articles, len(mock_titles))):
            title = random.choice(mock_titles)
            summary = random.choice(mock_summaries)
            link = f"https://example.com/news/{i}"
            publisher = random.choice(mock_publishers)

            # Random timestamp within last 24 hours
            hours_ago = random.randint(1, 24)
            published_date = (datetime.now() - timedelta(hours=hours_ago)).isoformat()

            content_hash = self._generate_content_hash(title, summary, link)
            keywords = self._extract_keywords(title, summary)
            category = self._categorize_news(title, summary)
            sentiment_score = self._calculate_sentiment_score(title, summary)

            mock_articles.append({
                'title': title,
                'summary': summary,
                'link': link,
                'publisher': publisher,
                'published_date': published_date,
                'symbol': symbol,
                'content_hash': content_hash,
                'sentiment_score': sentiment_score,
                'keywords': json.dumps(keywords),
                'category': category
            })

        return mock_articles

    def save_news_to_database(self, news_articles: List[Dict[str, Any]]) -> int:
        """Save news articles to SQLite database, avoiding duplicates."""
        if not news_articles:
            return 0

        saved_count = 0
        current_time = datetime.now().isoformat()

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                for article in news_articles:
                    try:
                        cursor.execute('''
                            INSERT OR IGNORE INTO gold_news
                            (title, summary, link, publisher, published_date, symbol,
                             content_hash, sentiment_score, keywords, category, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            article['title'],
                            article['summary'],
                            article['link'],
                            article['publisher'],
                            article['published_date'],
                            article['symbol'],
                            article['content_hash'],
                            article['sentiment_score'],
                            article['keywords'],
                            article['category'],
                            current_time,
                            current_time
                        ))

                        if cursor.rowcount > 0:
                            saved_count += 1

                    except sqlite3.Error as e:
                        logger.warning(f"Error saving article '{article.get('title', 'Unknown')}': {e}")

                conn.commit()
                logger.info(f"Saved {saved_count} new articles to database")

        except sqlite3.Error as e:
            logger.error(f"Database error while saving news: {e}")

        return saved_count

    def get_cached_news(self, days: int = 7, category: Optional[str] = None,
                       min_sentiment: Optional[float] = None) -> pd.DataFrame:
        """Retrieve cached news from database with optional filters."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)

                # Build query with optional filters
                query = '''
                    SELECT title, summary, link, publisher, published_date, symbol,
                           sentiment_score, keywords, category, created_at
                    FROM gold_news
                    WHERE published_date >= ?
                '''
                params = [start_date.isoformat()]

                if category:
                    query += ' AND category = ?'
                    params.append(category)

                if min_sentiment is not None:
                    query += ' AND sentiment_score >= ?'
                    params.append(min_sentiment)

                query += ' ORDER BY published_date DESC'

                df = pd.read_sql_query(query, conn, params=params)

                if not df.empty:
                    df['published_date'] = pd.to_datetime(df['published_date'])
                    df['keywords'] = df['keywords'].apply(lambda x: json.loads(x) if x else [])

                return df

        except sqlite3.Error as e:
            logger.error(f"Error retrieving cached news: {e}")
            return pd.DataFrame()

    def fetch_and_cache_gold_news(self, max_articles_per_symbol: Optional[int] = None) -> Dict[str, int]:
        """Main method to fetch and cache gold news from all symbols."""
        max_articles_per_symbol = max_articles_per_symbol or config.max_articles_per_symbol
        logger.info(f"Starting gold news fetch for symbols: {', '.join(self.symbols)}")

        results = {}
        total_saved = 0

        for symbol in self.symbols:
            try:
                # Fetch news for symbol
                news_articles = self.fetch_news_for_symbol(symbol, max_articles_per_symbol)

                # Save to database
                saved_count = self.save_news_to_database(news_articles)
                results[symbol] = saved_count
                total_saved += saved_count

                # Record fetch history
                self._record_fetch_history(symbol, len(news_articles), True, None)

                # Rate limiting between symbols
                if config.api_delay > 0 and symbol != self.symbols[-1]:
                    time.sleep(config.api_delay)

            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                results[symbol] = 0
                self._record_fetch_history(symbol, 0, False, str(e))

        logger.info(f"News fetch complete. Total new articles saved: {total_saved}")
        return results

    def _record_fetch_history(self, symbol: str, articles_count: int, success: bool, error_message: Optional[str]):
        """Record fetch history for monitoring."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO news_fetch_history
                    (symbol, fetch_date, articles_count, success, error_message, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    symbol,
                    datetime.now().date().isoformat(),
                    articles_count,
                    success,
                    error_message,
                    datetime.now().isoformat()
                ))
                conn.commit()
        except sqlite3.Error as e:
            logger.warning(f"Error recording fetch history: {e}")

    def get_news_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get a summary of cached news data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Total articles count
                cursor.execute('SELECT COUNT(*) FROM gold_news')
                total_articles = cursor.fetchone()[0]

                # Recent articles (last N days)
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)

                cursor.execute('''
                    SELECT COUNT(*) FROM gold_news
                    WHERE published_date >= ?
                ''', (start_date.isoformat(),))
                recent_articles = cursor.fetchone()[0]

                # Articles by category
                cursor.execute('''
                    SELECT category, COUNT(*) FROM gold_news
                    WHERE published_date >= ?
                    GROUP BY category
                    ORDER BY COUNT(*) DESC
                ''', (start_date.isoformat(),))
                categories = dict(cursor.fetchall())

                # Average sentiment
                cursor.execute('''
                    SELECT AVG(sentiment_score) FROM gold_news
                    WHERE published_date >= ?
                ''', (start_date.isoformat(),))
                avg_sentiment = cursor.fetchone()[0] or 0.0

                # Top publishers
                cursor.execute('''
                    SELECT publisher, COUNT(*) FROM gold_news
                    WHERE published_date >= ?
                    GROUP BY publisher
                    ORDER BY COUNT(*) DESC
                    LIMIT 5
                ''', (start_date.isoformat(),))
                top_publishers = dict(cursor.fetchall())

                return {
                    'total_articles': total_articles,
                    'recent_articles': recent_articles,
                    'days_analyzed': days,
                    'categories': categories,
                    'average_sentiment': round(avg_sentiment, 3),
                    'top_publishers': top_publishers,
                    'date_range': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
                }

        except sqlite3.Error as e:
            logger.error(f"Error generating news summary: {e}")
            return {}

    def display_news_summary(self):
        """Display a formatted summary of cached news data."""
        summary = self.get_news_summary()

        if not summary:
            print("❌ Unable to generate news summary")
            return

        print("\n" + "="*70)
        print("📰 GOLD NEWS CACHE SUMMARY")
        print("="*70)

        print(f"📊 Total Articles: {summary['total_articles']}")
        print(f"📅 Recent Articles ({summary['days_analyzed']} days): {summary['recent_articles']}")
        print(f"📈 Average Sentiment: {summary['average_sentiment']:.3f} (-1.0 to 1.0)")
        print(f"🗓️  Date Range: {summary['date_range']}")

        print(f"\n📂 Articles by Category:")
        for category, count in summary['categories'].items():
            print(f"   • {category.replace('_', ' ').title()}: {count}")

        print(f"\n📺 Top Publishers:")
        for publisher, count in summary['top_publishers'].items():
            print(f"   • {publisher}: {count}")

    def get_recent_headlines(self, limit: int = 10, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent headlines with optional category filter."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT title, summary, published_date, publisher, sentiment_score, category
                    FROM gold_news
                '''
                params = []

                if category:
                    query += ' WHERE category = ?'
                    params.append(category)

                query += ' ORDER BY published_date DESC LIMIT ?'
                params.append(limit)

                cursor = conn.cursor()
                cursor.execute(query, params)

                results = []
                for row in cursor.fetchall():
                    results.append({
                        'title': row[0],
                        'summary': row[1],
                        'published_date': row[2],
                        'publisher': row[3],
                        'sentiment_score': row[4],
                        'category': row[5]
                    })

                return results

        except sqlite3.Error as e:
            logger.error(f"Error getting recent headlines: {e}")
            return []

    def search_news(self, keyword: str, days: int = 30, limit: int = 20) -> List[Dict[str, Any]]:
        """Search news articles by keyword."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)

                query = '''
                    SELECT title, summary, link, published_date, publisher,
                           sentiment_score, category
                    FROM gold_news
                    WHERE (title LIKE ? OR summary LIKE ? OR keywords LIKE ?)
                    AND published_date >= ?
                    ORDER BY published_date DESC
                    LIMIT ?
                '''

                search_pattern = f'%{keyword}%'
                params = [search_pattern, search_pattern, search_pattern,
                         start_date.isoformat(), limit]

                cursor = conn.cursor()
                cursor.execute(query, params)

                results = []
                for row in cursor.fetchall():
                    results.append({
                        'title': row[0],
                        'summary': row[1],
                        'link': row[2],
                        'published_date': row[3],
                        'publisher': row[4],
                        'sentiment_score': row[5],
                        'category': row[6]
                    })

                return results

        except sqlite3.Error as e:
            logger.error(f"Error searching news: {e}")
            return []


def main():
    """Main function to run the gold news fetcher."""
    import argparse

    parser = argparse.ArgumentParser(description='Gold News Fetcher and Cache Manager')
    parser.add_argument('--fetch', '-f', action='store_true',
                       help='Fetch latest gold news')
    parser.add_argument('--summary', '-s', action='store_true',
                       help='Display news cache summary')
    parser.add_argument('--headlines', type=int, default=10,
                       help='Show recent headlines (default: 10)')
    parser.add_argument('--search', type=str,
                       help='Search news by keyword')
    parser.add_argument('--category', choices=['monetary_policy', 'supply_demand', 'market_movement',
                                              'geopolitical', 'economic_data', 'general'],
                       help='Filter by news category')
    parser.add_argument('--config-summary', action='store_true',
                       help='Show configuration summary and exit')

    args = parser.parse_args()

    if args.config_summary:
        config.print_config_summary()
        return

    try:
        fetcher = GoldNewsFetcher()

        if args.fetch:
            # Fetch and cache news
            results = fetcher.fetch_and_cache_gold_news()
            print(f"\n📰 News Fetch Results:")
            for symbol, count in results.items():
                print(f"   • {symbol}: {count} new articles")

        if args.summary:
            # Display summary
            fetcher.display_news_summary()

        if args.search:
            # Search functionality
            results = fetcher.search_news(args.search)
            print(f"\n🔍 Search Results for '{args.search}' ({len(results)} articles):")
            for article in results:
                sentiment_emoji = "📈" if article['sentiment_score'] > 0.1 else "📉" if article['sentiment_score'] < -0.1 else "📊"
                print(f"   {sentiment_emoji} {article['title']} [{article['publisher']}]")
                if article['summary']:
                    print(f"      {article['summary'][:150]}...")

        if args.headlines:
            # Show recent headlines
            headlines = fetcher.get_recent_headlines(args.headlines, args.category)
            category_text = f" ({args.category.replace('_', ' ').title()})" if args.category else ""
            print(f"\n📰 Recent Gold Headlines{category_text}:")
            for i, article in enumerate(headlines, 1):
                sentiment_emoji = "📈" if article['sentiment_score'] > 0.1 else "📉" if article['sentiment_score'] < -0.1 else "📊"
                date_str = article['published_date'][:19] if article['published_date'] else 'Unknown'
                print(f"   {i}. {sentiment_emoji} {article['title']}")
                print(f"      {article['publisher']} | {date_str} | Sentiment: {article['sentiment_score']:.2f}")

        # Default behavior: show summary if no specific action
        if not any([args.fetch, args.summary, args.search, args.headlines]):
            fetcher.display_news_summary()

    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
