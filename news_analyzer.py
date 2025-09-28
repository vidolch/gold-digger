#!/usr/bin/env python3
"""
Gold News Analyzer
Analyzes cached news data to provide sentiment analysis and trading insights.
Integrates with the trading analyzer to provide comprehensive market analysis.
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from collections import Counter
from config import get_config

# Get configuration
config = get_config()
logger = logging.getLogger(__name__)


class GoldNewsAnalyzer:
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the news analyzer with database path."""
        self.db_path = db_path or config.database_path

    def get_sentiment_trend(self, days: int = 7) -> Dict[str, Any]:
        """Analyze sentiment trend over specified time period."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)

                # Get daily sentiment averages
                query = '''
                    SELECT DATE(published_date) as date,
                           AVG(sentiment_score) as avg_sentiment,
                           COUNT(*) as article_count
                    FROM gold_news
                    WHERE published_date >= ? AND sentiment_score IS NOT NULL
                    GROUP BY DATE(published_date)
                    ORDER BY date
                '''

                df = pd.read_sql_query(query, conn, params=(start_date.isoformat(),))

                if df.empty:
                    return {'error': 'No sentiment data available'}

                # Calculate trend metrics
                sentiment_values = df['avg_sentiment'].values
                current_sentiment = sentiment_values[-1] if len(sentiment_values) > 0 else 0

                trend_direction = 'neutral'
                if len(sentiment_values) >= 2:
                    recent_avg = np.mean(sentiment_values[-3:]) if len(sentiment_values) >= 3 else sentiment_values[-1]
                    older_avg = np.mean(sentiment_values[:-3]) if len(sentiment_values) > 3 else sentiment_values[0]

                    if recent_avg > older_avg + 0.05:
                        trend_direction = 'improving'
                    elif recent_avg < older_avg - 0.05:
                        trend_direction = 'declining'

                return {
                    'current_sentiment': round(current_sentiment, 3),
                    'trend_direction': trend_direction,
                    'daily_data': df.to_dict('records'),
                    'summary': {
                        'avg_sentiment': round(np.mean(sentiment_values), 3),
                        'max_sentiment': round(np.max(sentiment_values), 3),
                        'min_sentiment': round(np.min(sentiment_values), 3),
                        'volatility': round(np.std(sentiment_values), 3),
                        'total_articles': int(df['article_count'].sum())
                    }
                }

        except sqlite3.Error as e:
            logger.error(f"Error analyzing sentiment trend: {e}")
            return {'error': str(e)}

    def get_category_analysis(self, days: int = 7) -> Dict[str, Any]:
        """Analyze news by category and their sentiment impact."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)

                query = '''
                    SELECT category,
                           COUNT(*) as article_count,
                           AVG(sentiment_score) as avg_sentiment,
                           MAX(sentiment_score) as max_sentiment,
                           MIN(sentiment_score) as min_sentiment
                    FROM gold_news
                    WHERE published_date >= ?
                    AND category IS NOT NULL
                    AND sentiment_score IS NOT NULL
                    GROUP BY category
                    ORDER BY article_count DESC
                '''

                df = pd.read_sql_query(query, conn, params=(start_date.isoformat(),))

                if df.empty:
                    return {'error': 'No category data available'}

                # Convert to dictionary with analysis
                categories = {}
                for _, row in df.iterrows():
                    category = row['category']
                    categories[category] = {
                        'article_count': int(row['article_count']),
                        'avg_sentiment': round(row['avg_sentiment'], 3),
                        'max_sentiment': round(row['max_sentiment'], 3),
                        'min_sentiment': round(row['min_sentiment'], 3),
                        'sentiment_range': round(row['max_sentiment'] - row['min_sentiment'], 3),
                        'market_impact': self._assess_category_impact(category, row['avg_sentiment'])
                    }

                return {
                    'categories': categories,
                    'most_covered': df.iloc[0]['category'] if not df.empty else None,
                    'most_positive': df.loc[df['avg_sentiment'].idxmax()]['category'] if not df.empty else None,
                    'most_negative': df.loc[df['avg_sentiment'].idxmin()]['category'] if not df.empty else None
                }

        except sqlite3.Error as e:
            logger.error(f"Error analyzing categories: {e}")
            return {'error': str(e)}

    def _assess_category_impact(self, category: str, sentiment: float) -> str:
        """Assess the potential market impact of a news category."""
        impact_weights = {
            'monetary_policy': 0.9,  # High impact
            'economic_data': 0.8,
            'geopolitical': 0.7,
            'market_movement': 0.6,
            'supply_demand': 0.5,
            'general': 0.3  # Low impact
        }

        weight = impact_weights.get(category, 0.5)
        impact_score = abs(sentiment) * weight

        if impact_score > 0.4:
            return 'high'
        elif impact_score > 0.2:
            return 'medium'
        else:
            return 'low'

    def get_keyword_analysis(self, days: int = 7, top_n: int = 10) -> Dict[str, Any]:
        """Analyze trending keywords and their sentiment impact."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)

                query = '''
                    SELECT keywords, sentiment_score
                    FROM gold_news
                    WHERE published_date >= ?
                    AND keywords IS NOT NULL
                    AND keywords != '[]'
                    AND sentiment_score IS NOT NULL
                '''

                cursor = conn.cursor()
                cursor.execute(query, (start_date.isoformat(),))
                results = cursor.fetchall()

                if not results:
                    return {'error': 'No keyword data available'}

                # Process keywords and sentiments
                keyword_sentiments = {}
                all_keywords = []

                for keywords_json, sentiment in results:
                    try:
                        keywords = json.loads(keywords_json)
                        for keyword in keywords:
                            all_keywords.append(keyword)
                            if keyword not in keyword_sentiments:
                                keyword_sentiments[keyword] = []
                            keyword_sentiments[keyword].append(sentiment)
                    except json.JSONDecodeError:
                        continue

                # Calculate keyword statistics
                keyword_counts = Counter(all_keywords)
                top_keywords = {}

                for keyword, count in keyword_counts.most_common(top_n):
                    sentiments = keyword_sentiments[keyword]
                    top_keywords[keyword] = {
                        'count': count,
                        'avg_sentiment': round(np.mean(sentiments), 3),
                        'sentiment_std': round(np.std(sentiments), 3),
                        'market_signal': self._interpret_keyword_sentiment(keyword, np.mean(sentiments))
                    }

                return {
                    'top_keywords': top_keywords,
                    'total_unique_keywords': len(keyword_counts),
                    'trending': list(keyword_counts.keys())[:5]
                }

        except sqlite3.Error as e:
            logger.error(f"Error analyzing keywords: {e}")
            return {'error': str(e)}

    def _interpret_keyword_sentiment(self, keyword: str, sentiment: float) -> str:
        """Interpret what keyword sentiment means for gold trading."""
        bullish_keywords = ['fed', 'inflation', 'crisis', 'uncertainty', 'safe haven']
        bearish_keywords = ['strong dollar', 'rate hikes', 'economic growth']

        if keyword.lower() in bullish_keywords:
            if sentiment > 0.1:
                return 'strong_bullish'
            elif sentiment < -0.1:
                return 'mixed_signal'
            else:
                return 'bullish'
        elif keyword.lower() in bearish_keywords:
            if sentiment > 0.1:
                return 'mixed_signal'
            elif sentiment < -0.1:
                return 'strong_bearish'
            else:
                return 'bearish'
        else:
            if sentiment > 0.2:
                return 'positive'
            elif sentiment < -0.2:
                return 'negative'
            else:
                return 'neutral'

    def get_publisher_analysis(self, days: int = 7) -> Dict[str, Any]:
        """Analyze news publishers and their sentiment bias."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)

                query = '''
                    SELECT publisher,
                           COUNT(*) as article_count,
                           AVG(sentiment_score) as avg_sentiment,
                           STDEV(sentiment_score) as sentiment_std
                    FROM gold_news
                    WHERE published_date >= ?
                    AND publisher IS NOT NULL
                    AND sentiment_score IS NOT NULL
                    GROUP BY publisher
                    HAVING COUNT(*) >= 2
                    ORDER BY article_count DESC
                '''

                df = pd.read_sql_query(query, conn, params=(start_date.isoformat(),))

                if df.empty:
                    return {'error': 'No publisher data available'}

                publishers = {}
                for _, row in df.iterrows():
                    publisher = row['publisher']
                    avg_sentiment = row['avg_sentiment'] or 0

                    publishers[publisher] = {
                        'article_count': int(row['article_count']),
                        'avg_sentiment': round(avg_sentiment, 3),
                        'sentiment_std': round(row['sentiment_std'] or 0, 3),
                        'bias': self._assess_publisher_bias(avg_sentiment),
                        'reliability': self._assess_publisher_reliability(int(row['article_count']))
                    }

                return {
                    'publishers': publishers,
                    'most_active': df.iloc[0]['publisher'] if not df.empty else None,
                    'most_bullish': df.loc[df['avg_sentiment'].idxmax()]['publisher'] if not df.empty else None,
                    'most_bearish': df.loc[df['avg_sentiment'].idxmin()]['publisher'] if not df.empty else None
                }

        except sqlite3.Error as e:
            logger.error(f"Error analyzing publishers: {e}")
            return {'error': str(e)}

    def _assess_publisher_bias(self, avg_sentiment: float) -> str:
        """Assess publisher sentiment bias."""
        if avg_sentiment > 0.15:
            return 'bullish'
        elif avg_sentiment < -0.15:
            return 'bearish'
        else:
            return 'balanced'

    def _assess_publisher_reliability(self, article_count: int) -> str:
        """Assess publisher reliability based on article volume."""
        if article_count >= 10:
            return 'high'
        elif article_count >= 5:
            return 'medium'
        else:
            return 'low'

    def generate_news_summary_for_trading(self, days: int = 3) -> Dict[str, Any]:
        """Generate a comprehensive news summary for trading decisions."""
        try:
            sentiment_analysis = self.get_sentiment_trend(days)
            category_analysis = self.get_category_analysis(days)
            keyword_analysis = self.get_keyword_analysis(days, top_n=5)

            if any('error' in analysis for analysis in [sentiment_analysis, category_analysis, keyword_analysis]):
                return {'error': 'Insufficient news data for comprehensive analysis'}

            # Generate trading-focused summary
            summary = {
                'overall_sentiment': sentiment_analysis.get('current_sentiment', 0),
                'sentiment_trend': sentiment_analysis.get('trend_direction', 'neutral'),
                'key_factors': [],
                'market_signals': [],
                'risk_factors': [],
                'news_volume': sentiment_analysis.get('summary', {}).get('total_articles', 0)
            }

            # Analyze key factors from categories
            categories = category_analysis.get('categories', {})
            for category, data in categories.items():
                if data['market_impact'] in ['high', 'medium'] and data['article_count'] >= 2:
                    factor = {
                        'category': category.replace('_', ' ').title(),
                        'sentiment': data['avg_sentiment'],
                        'impact': data['market_impact'],
                        'article_count': data['article_count']
                    }
                    summary['key_factors'].append(factor)

            # Generate market signals
            overall_sentiment = summary['overall_sentiment']
            if overall_sentiment > 0.1 and sentiment_analysis.get('trend_direction') == 'improving':
                summary['market_signals'].append('Positive sentiment trend supports bullish outlook')
            elif overall_sentiment < -0.1 and sentiment_analysis.get('trend_direction') == 'declining':
                summary['market_signals'].append('Negative sentiment trend suggests bearish pressure')

            # Analyze keywords for signals
            keywords = keyword_analysis.get('top_keywords', {})
            for keyword, data in keywords.items():
                if data['count'] >= 3 and data['market_signal'] in ['strong_bullish', 'strong_bearish']:
                    signal = f"'{keyword}' keyword trending with {data['market_signal'].replace('_', ' ')} signal"
                    summary['market_signals'].append(signal)

            # Identify risk factors
            if sentiment_analysis.get('summary', {}).get('volatility', 0) > 0.3:
                summary['risk_factors'].append('High sentiment volatility indicates market uncertainty')

            if summary['news_volume'] < 10:
                summary['risk_factors'].append('Low news volume may indicate reduced market attention')

            # Generate overall assessment
            summary['overall_assessment'] = self._generate_overall_assessment(summary)

            return summary

        except Exception as e:
            logger.error(f"Error generating news summary: {e}")
            return {'error': str(e)}

    def _generate_overall_assessment(self, summary: Dict[str, Any]) -> str:
        """Generate overall market assessment based on news analysis."""
        sentiment = summary['overall_sentiment']
        trend = summary['sentiment_trend']
        high_impact_factors = len([f for f in summary['key_factors'] if f['impact'] == 'high'])

        if sentiment > 0.2 and trend == 'improving' and high_impact_factors >= 1:
            return 'bullish'
        elif sentiment < -0.2 and trend == 'declining' and high_impact_factors >= 1:
            return 'bearish'
        elif abs(sentiment) < 0.1 or trend == 'neutral':
            return 'neutral'
        else:
            return 'mixed'

    def get_recent_news_for_analysis(self, hours: int = 24, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent news formatted for AI analysis integration."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                end_time = datetime.now()
                start_time = end_time - timedelta(hours=hours)

                query = '''
                    SELECT title, summary, published_date, publisher,
                           sentiment_score, category, keywords
                    FROM gold_news
                    WHERE published_date >= ?
                    ORDER BY published_date DESC
                    LIMIT ?
                '''

                cursor = conn.cursor()
                cursor.execute(query, (start_time.isoformat(), limit))

                news_items = []
                for row in cursor.fetchall():
                    try:
                        keywords = json.loads(row[6]) if row[6] else []
                    except json.JSONDecodeError:
                        keywords = []

                    news_items.append({
                        'title': row[0],
                        'summary': row[1],
                        'published_date': row[2],
                        'publisher': row[3],
                        'sentiment_score': row[4],
                        'category': row[5],
                        'keywords': keywords
                    })

                return news_items

        except sqlite3.Error as e:
            logger.error(f"Error getting recent news: {e}")
            return []

    def format_news_for_prompt(self, hours: int = 24) -> str:
        """Format recent news data for AI trading analysis prompt."""
        news_items = self.get_recent_news_for_analysis(hours)
        news_summary = self.generate_news_summary_for_trading(days=2)

        if not news_items and not news_summary:
            return "No recent news data available for analysis."

        formatted_news = "## RECENT GOLD NEWS ANALYSIS\n\n"

        # Add overall news sentiment summary
        if 'error' not in news_summary:
            formatted_news += f"**Overall News Sentiment:** {news_summary.get('overall_sentiment', 0):.3f} (Trend: {news_summary.get('sentiment_trend', 'neutral')})\n"
            formatted_news += f"**Market Assessment:** {news_summary.get('overall_assessment', 'neutral').upper()}\n"
            formatted_news += f"**News Volume:** {news_summary.get('news_volume', 0)} articles\n\n"

            if news_summary.get('key_factors'):
                formatted_news += "**Key Market Factors:**\n"
                for factor in news_summary['key_factors']:
                    formatted_news += f"- {factor['category']}: {factor['sentiment']:.2f} sentiment ({factor['impact']} impact)\n"
                formatted_news += "\n"

            if news_summary.get('market_signals'):
                formatted_news += "**Market Signals:**\n"
                for signal in news_summary['market_signals']:
                    formatted_news += f"- {signal}\n"
                formatted_news += "\n"

        # Add recent headlines
        if news_items:
            formatted_news += f"**Recent Headlines (Last {hours} hours):**\n"
            for i, item in enumerate(news_items[:10], 1):
                sentiment_indicator = "📈" if item['sentiment_score'] > 0.1 else "📉" if item['sentiment_score'] < -0.1 else "📊"
                formatted_news += f"{i}. {sentiment_indicator} {item['title']} [{item['publisher']}]\n"
                if item['summary']:
                    formatted_news += f"   Summary: {item['summary'][:150]}...\n"
                formatted_news += f"   Sentiment: {item['sentiment_score']:.2f} | Category: {item['category']}\n\n"

        return formatted_news


def main():
    """Main function for news analysis."""
    import argparse

    parser = argparse.ArgumentParser(description='Gold News Analysis Tool')
    parser.add_argument('--sentiment', '-s', action='store_true',
                       help='Show sentiment trend analysis')
    parser.add_argument('--categories', '-c', action='store_true',
                       help='Show category analysis')
    parser.add_argument('--keywords', '-k', action='store_true',
                       help='Show keyword analysis')
    parser.add_argument('--publishers', '-p', action='store_true',
                       help='Show publisher analysis')
    parser.add_argument('--trading-summary', '-t', action='store_true',
                       help='Show trading-focused news summary')
    parser.add_argument('--days', '-d', type=int, default=7,
                       help='Number of days to analyze (default: 7)')

    args = parser.parse_args()

    try:
        analyzer = GoldNewsAnalyzer()

        if args.sentiment:
            print("📊 SENTIMENT TREND ANALYSIS")
            print("=" * 50)
            sentiment = analyzer.get_sentiment_trend(args.days)
            if 'error' not in sentiment:
                print(f"Current Sentiment: {sentiment['current_sentiment']}")
                print(f"Trend Direction: {sentiment['trend_direction']}")
                print(f"Average Sentiment: {sentiment['summary']['avg_sentiment']}")
                print(f"Volatility: {sentiment['summary']['volatility']}")
                print(f"Total Articles: {sentiment['summary']['total_articles']}")

        if args.categories:
            print("\n📂 CATEGORY ANALYSIS")
            print("=" * 50)
            categories = analyzer.get_category_analysis(args.days)
            if 'error' not in categories:
                for cat, data in categories['categories'].items():
                    print(f"{cat.replace('_', ' ').title()}:")
                    print(f"  Articles: {data['article_count']}")
                    print(f"  Avg Sentiment: {data['avg_sentiment']}")
                    print(f"  Market Impact: {data['market_impact']}")

        if args.keywords:
            print("\n🔍 KEYWORD ANALYSIS")
            print("=" * 50)
            keywords = analyzer.get_keyword_analysis(args.days)
            if 'error' not in keywords:
                for keyword, data in keywords['top_keywords'].items():
                    print(f"'{keyword}': {data['count']} mentions, sentiment: {data['avg_sentiment']}, signal: {data['market_signal']}")

        if args.publishers:
            print("\n📰 PUBLISHER ANALYSIS")
            print("=" * 50)
            publishers = analyzer.get_publisher_analysis(args.days)
            if 'error' not in publishers:
                for pub, data in publishers['publishers'].items():
                    print(f"{pub}: {data['article_count']} articles, sentiment: {data['avg_sentiment']} ({data['bias']})")

        if args.trading_summary:
            print("\n💰 TRADING SUMMARY")
            print("=" * 50)
            summary = analyzer.generate_news_summary_for_trading(3)
            if 'error' not in summary:
                print(f"Overall Assessment: {summary['overall_assessment'].upper()}")
                print(f"Sentiment: {summary['overall_sentiment']:.3f} ({summary['sentiment_trend']})")
                print(f"News Volume: {summary['news_volume']} articles")

                if summary['key_factors']:
                    print("\nKey Factors:")
                    for factor in summary['key_factors']:
                        print(f"  - {factor['category']}: {factor['sentiment']:.2f} ({factor['impact']} impact)")

                if summary['market_signals']:
                    print("\nMarket Signals:")
                    for signal in summary['market_signals']:
                        print(f"  - {signal}")

        # Default: show trading summary if no specific analysis requested
        if not any([args.sentiment, args.categories, args.keywords, args.publishers, args.trading_summary]):
            print("💰 GOLD NEWS TRADING SUMMARY")
            print("=" * 60)
            summary = analyzer.generate_news_summary_for_trading(3)
            if 'error' not in summary:
                print(f"📊 Overall Assessment: {summary['overall_assessment'].upper()}")
                print(f"📈 Current Sentiment: {summary['overall_sentiment']:.3f}")
                print(f"📰 News Volume: {summary['news_volume']} articles (last 3 days)")

                if summary['market_signals']:
                    print(f"\n🚨 Market Signals:")
                    for signal in summary['market_signals']:
                        print(f"   • {signal}")
            else:
                print("❌ Error: Insufficient news data available")

    except Exception as e:
        logger.error(f"Error in news analysis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
