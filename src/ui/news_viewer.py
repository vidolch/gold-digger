#!/usr/bin/env python3
"""
Interactive Gold News Viewer
A comprehensive tool for browsing, filtering, and analyzing cached gold news articles.
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json
import sys
from typing import List, Dict, Optional, Any
import argparse
from config import get_config

# Get configuration
config = get_config()

class NewsViewer:
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the news viewer with database path."""
        self.db_path = db_path or config.database_path

    def get_news_stats(self) -> Dict[str, Any]:
        """Get basic statistics about the news database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Total articles
                cursor.execute('SELECT COUNT(*) FROM gold_news')
                total_articles = cursor.fetchone()[0]

                # Date range
                cursor.execute('SELECT MIN(published_date), MAX(published_date) FROM gold_news')
                date_range = cursor.fetchone()

                # Categories
                cursor.execute('''
                    SELECT category, COUNT(*)
                    FROM gold_news
                    WHERE category IS NOT NULL
                    GROUP BY category
                    ORDER BY COUNT(*) DESC
                ''')
                categories = dict(cursor.fetchall())

                # Publishers
                cursor.execute('''
                    SELECT publisher, COUNT(*)
                    FROM gold_news
                    WHERE publisher IS NOT NULL
                    GROUP BY publisher
                    ORDER BY COUNT(*) DESC
                    LIMIT 5
                ''')
                top_publishers = dict(cursor.fetchall())

                return {
                    'total_articles': total_articles,
                    'date_range': date_range,
                    'categories': categories,
                    'top_publishers': top_publishers
                }

        except sqlite3.Error as e:
            return {'error': str(e)}

    def browse_headlines(self, limit: int = 20, category: Optional[str] = None,
                        days: Optional[int] = None, min_sentiment: Optional[float] = None) -> List[Dict]:
        """Browse news headlines with optional filters."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT id, title, summary, publisher, published_date,
                           sentiment_score, category, keywords, link
                    FROM gold_news
                    WHERE 1=1
                '''
                params = []

                # Add filters
                if category:
                    query += ' AND category = ?'
                    params.append(category)

                if days:
                    cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
                    query += ' AND published_date >= ?'
                    params.append(cutoff_date)

                if min_sentiment is not None:
                    query += ' AND sentiment_score >= ?'
                    params.append(min_sentiment)

                query += ' ORDER BY published_date DESC LIMIT ?'
                params.append(limit)

                cursor = conn.cursor()
                cursor.execute(query, params)

                articles = []
                for row in cursor.fetchall():
                    try:
                        keywords = json.loads(row[7]) if row[7] else []
                    except json.JSONDecodeError:
                        keywords = []

                    articles.append({
                        'id': row[0],
                        'title': row[1],
                        'summary': row[2],
                        'publisher': row[3],
                        'published_date': row[4],
                        'sentiment_score': row[5],
                        'category': row[6],
                        'keywords': keywords,
                        'link': row[8]
                    })

                return articles

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

    def search_articles(self, query: str, limit: int = 10) -> List[Dict]:
        """Search articles by title, summary, or keywords."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                search_query = '''
                    SELECT id, title, summary, publisher, published_date,
                           sentiment_score, category, keywords, link
                    FROM gold_news
                    WHERE title LIKE ? OR summary LIKE ? OR keywords LIKE ?
                    ORDER BY published_date DESC
                    LIMIT ?
                '''

                search_pattern = f'%{query}%'
                params = [search_pattern, search_pattern, search_pattern, limit]

                cursor = conn.cursor()
                cursor.execute(search_query, params)

                articles = []
                for row in cursor.fetchall():
                    try:
                        keywords = json.loads(row[7]) if row[7] else []
                    except json.JSONDecodeError:
                        keywords = []

                    articles.append({
                        'id': row[0],
                        'title': row[1],
                        'summary': row[2],
                        'publisher': row[3],
                        'published_date': row[4],
                        'sentiment_score': row[5],
                        'category': row[6],
                        'keywords': keywords,
                        'link': row[8]
                    })

                return articles

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

    def get_article_details(self, article_id: int) -> Optional[Dict]:
        """Get full details for a specific article."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM gold_news WHERE id = ?
                ''', (article_id,))

                row = cursor.fetchone()
                if not row:
                    return None

                try:
                    keywords = json.loads(row[9]) if row[9] else []
                except json.JSONDecodeError:
                    keywords = []

                return {
                    'id': row[0],
                    'title': row[1],
                    'summary': row[2],
                    'link': row[3],
                    'publisher': row[4],
                    'published_date': row[5],
                    'symbol': row[6],
                    'content_hash': row[7],
                    'sentiment_score': row[8],
                    'keywords': keywords,
                    'category': row[10],
                    'created_at': row[11],
                    'updated_at': row[12]
                }

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

    def print_news_stats(self):
        """Print formatted news statistics."""
        stats = self.get_news_stats()

        if 'error' in stats:
            print(f"❌ Error: {stats['error']}")
            return

        print("\n" + "="*70)
        print("📊 GOLD NEWS DATABASE STATISTICS")
        print("="*70)

        print(f"📰 Total Articles: {stats['total_articles']}")

        if stats['date_range'] and stats['date_range'][0]:
            print(f"📅 Date Range: {stats['date_range'][0][:10]} to {stats['date_range'][1][:10]}")

        print(f"\n📂 Categories:")
        for category, count in stats['categories'].items():
            percentage = (count / stats['total_articles']) * 100
            print(f"   • {category.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")

        print(f"\n📺 Top Publishers:")
        for publisher, count in stats['top_publishers'].items():
            print(f"   • {publisher}: {count} articles")

    def print_headlines(self, articles: List[Dict], show_details: bool = False):
        """Print formatted headlines."""
        if not articles:
            print("❌ No articles found matching criteria")
            return

        print(f"\n📰 Found {len(articles)} articles:")
        print("-" * 80)

        for i, article in enumerate(articles, 1):
            # Sentiment emoji
            sentiment = article['sentiment_score'] or 0
            if sentiment > 0.1:
                emoji = "📈"
            elif sentiment < -0.1:
                emoji = "📉"
            else:
                emoji = "📊"

            # Format date
            date_str = article['published_date'][:19] if article['published_date'] else 'Unknown'

            print(f"{i:2d}. {emoji} {article['title']}")
            print(f"    📺 {article['publisher']} | 📅 {date_str} | 📊 {sentiment:.2f}")
            print(f"    🏷️  {article['category']} | 🆔 ID: {article['id']}")

            if show_details and article['summary']:
                summary = article['summary'][:200] + "..." if len(article['summary']) > 200 else article['summary']
                print(f"    💬 {summary}")

            if article['keywords']:
                keywords_str = ", ".join(article['keywords'][:5])
                print(f"    🔍 Keywords: {keywords_str}")

            print()

    def print_article_details(self, article: Dict):
        """Print full article details."""
        print("\n" + "="*80)
        print("📰 ARTICLE DETAILS")
        print("="*80)

        print(f"🆔 ID: {article['id']}")
        print(f"📰 Title: {article['title']}")
        print(f"📺 Publisher: {article['publisher']}")
        print(f"📅 Published: {article['published_date']}")
        print(f"🏷️  Category: {article['category']}")
        print(f"📊 Sentiment: {article['sentiment_score']:.3f}")
        print(f"🔗 Link: {article['link']}")

        if article['keywords']:
            print(f"🔍 Keywords: {', '.join(article['keywords'])}")

        print(f"\n💬 Summary:")
        print(f"   {article['summary']}")

        print(f"\n🔧 Metadata:")
        print(f"   Symbol: {article['symbol']}")
        print(f"   Cached: {article['created_at'][:19]}")
        print("="*80)

def main():
    """Main function for interactive news viewing."""
    parser = argparse.ArgumentParser(description='Interactive Gold News Viewer')

    # Main commands
    parser.add_argument('--stats', '-s', action='store_true',
                       help='Show news database statistics')
    parser.add_argument('--browse', '-b', action='store_true',
                       help='Browse recent headlines')
    parser.add_argument('--search', type=str,
                       help='Search articles by keyword')
    parser.add_argument('--article', '-a', type=int,
                       help='View specific article by ID')

    # Filters
    parser.add_argument('--category', choices=['monetary_policy', 'supply_demand', 'market_movement',
                                              'geopolitical', 'economic_data', 'general'],
                       help='Filter by category')
    parser.add_argument('--days', '-d', type=int, default=7,
                       help='Days to look back (default: 7)')
    parser.add_argument('--limit', '-l', type=int, default=20,
                       help='Maximum articles to show (default: 20)')
    parser.add_argument('--min-sentiment', type=float,
                       help='Minimum sentiment score (-1.0 to 1.0)')
    parser.add_argument('--details', action='store_true',
                       help='Show article summaries in browse mode')

    # Interactive mode
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Start interactive mode')

    args = parser.parse_args()

    viewer = NewsViewer()

    # Interactive mode
    if args.interactive:
        print("🏆 Welcome to Gold News Interactive Viewer!")
        print("Commands: stats, browse, search <term>, article <id>, quit")

        while True:
            try:
                command = input("\n📰 > ").strip().split()
                if not command:
                    continue

                if command[0] == 'quit':
                    break
                elif command[0] == 'stats':
                    viewer.print_news_stats()
                elif command[0] == 'browse':
                    limit = int(command[1]) if len(command) > 1 else 10
                    articles = viewer.browse_headlines(limit=limit, days=7)
                    viewer.print_headlines(articles)
                elif command[0] == 'search' and len(command) > 1:
                    query = ' '.join(command[1:])
                    articles = viewer.search_articles(query)
                    viewer.print_headlines(articles)
                elif command[0] == 'article' and len(command) > 1:
                    article_id = int(command[1])
                    article = viewer.get_article_details(article_id)
                    if article:
                        viewer.print_article_details(article)
                    else:
                        print(f"❌ Article {article_id} not found")
                else:
                    print("❌ Unknown command. Try: stats, browse, search <term>, article <id>, quit")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

        return

    # Command-line mode
    if args.stats:
        viewer.print_news_stats()

    elif args.browse:
        articles = viewer.browse_headlines(
            limit=args.limit,
            category=args.category,
            days=args.days,
            min_sentiment=args.min_sentiment
        )
        viewer.print_headlines(articles, show_details=args.details)

    elif args.search:
        articles = viewer.search_articles(args.search, args.limit)
        print(f"🔍 Search results for '{args.search}':")
        viewer.print_headlines(articles, show_details=args.details)

    elif args.article:
        article = viewer.get_article_details(args.article)
        if article:
            viewer.print_article_details(article)
        else:
            print(f"❌ Article {args.article} not found")

    else:
        # Default: show stats and recent headlines
        viewer.print_news_stats()
        print(f"\n📰 Recent Headlines (last {args.days} days):")
        articles = viewer.browse_headlines(limit=10, days=args.days)
        viewer.print_headlines(articles[:5])

        print(f"\n💡 Use --help for more options or --interactive for interactive mode")

if __name__ == "__main__":
    main()
