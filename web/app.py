#!/usr/bin/env python3
"""
Gold Digger Web Application
A modern web-based interface for gold trading analysis and news monitoring.
"""

import sys
import os
from datetime import datetime
import json
import logging
import pandas as pd
import socket

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import plotly.graph_objs as go
import plotly.utils

# Import our existing modules
from gold_fetcher import GoldPriceFetcher
from news_fetcher import GoldNewsFetcher
from news_analyzer import GoldNewsAnalyzer
from trading_analyzer import TradingAnalyzer
from config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Get configuration
config = get_config()

# Set database path to parent directory to use the main database
db_path = os.path.join(parent_dir, 'gold_prices.db')

# Initialize components with correct database path
gold_fetcher = GoldPriceFetcher(db_path=db_path)
news_fetcher = GoldNewsFetcher(db_path=db_path)
news_analyzer = GoldNewsAnalyzer(db_path=db_path)
trading_analyzer = TradingAnalyzer(db_path=db_path)


@app.route('/')
def index():
    """Main dashboard page."""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        return f"<h1>Gold Digger Dashboard</h1><p>Template Error: {e}</p><p>Please check server logs.</p>", 500

@app.route('/debug')
def debug():
    """Debug route to test basic functionality."""
    return "<h1>Gold Digger Web App Debug</h1><p>Server is running!</p><p>Flask app loaded successfully.</p>"

@app.route('/test')
def test():
    """Simple test route."""
    import os
    template_path = os.path.join(app.template_folder, 'index.html')
    template_exists = os.path.exists(template_path)
    return {
        'status': 'ok',
        'template_folder': app.template_folder,
        'template_exists': template_exists,
        'template_path': template_path
    }

@app.route('/api/current-price')
def get_current_price():
    """Get current gold price without running full analysis."""
    try:
        # Get recent price data without AI analysis
        df = gold_fetcher.get_cached_data('15m')
        if df.empty:
            return jsonify({'error': 'No price data available'}), 404

        # Calculate current price and change
        current_price = df['close'].iloc[-1] if not df.empty else None
        price_change = df['close'].iloc[-1] - df['close'].iloc[-2] if len(df) >= 2 else 0
        price_change_pct = (price_change / df['close'].iloc[-2] * 100) if len(df) >= 2 and df['close'].iloc[-2] != 0 else 0

        return jsonify({
            'current_price': current_price,
            'price_change': price_change,
            'price_change_percent': price_change_pct,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error fetching current price: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/prices/<interval>')
def get_prices(interval):
    """Get gold prices for specified interval."""
    try:
        valid_intervals = ['15m', '30m', '1h', '1d']
        if interval not in valid_intervals:
            return jsonify({'error': f'Invalid interval. Must be one of: {valid_intervals}'}), 400

        # Get price data - use get_cached_data method
        df = gold_fetcher.get_cached_data(interval)

        # For intervals not directly cached, use 15m data and resample
        if df.empty and interval in ['1h', '1d']:
            df = gold_fetcher.get_cached_data('15m')
            if not df.empty:
                df.set_index('datetime', inplace=True)
                if interval == '1h':
                    df = df.resample('1H').agg({
                        'open': 'first',
                        'high': 'max',
                        'low': 'min',
                        'close': 'last',
                        'volume': 'sum'
                    })
                elif interval == '1d':
                    df = df.resample('1D').agg({
                        'open': 'first',
                        'high': 'max',
                        'low': 'min',
                        'close': 'last',
                        'volume': 'sum'
                    })

        if df.empty:
            return jsonify({'error': 'No price data available'}), 404

        # Convert to JSON format
        df_reset = df.reset_index()
        data = {
            'timestamps': list(range(len(df_reset))),
            'dates': [str(date) for date in df_reset['datetime']],
            'open': df_reset['open'].tolist(),
            'high': df_reset['high'].tolist(),
            'low': df_reset['low'].tolist(),
            'close': df_reset['close'].tolist(),
            'volume': df_reset['volume'].tolist()
        }

        return jsonify(data)

    except Exception as e:
        logger.error(f"Error fetching prices: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/prices/chart/<interval>')
def get_price_chart(interval):
    """Generate price chart data for Plotly."""
    try:
        # Get price data directly
        df = gold_fetcher.get_cached_data(interval)
        if df.empty:
            return jsonify({'error': 'No price data available'}), 404

        # Convert to data format for chart
        df_reset = df.reset_index()
        data = {
            'dates': [str(date) for date in df_reset['datetime']],
            'open': df_reset['open'].tolist(),
            'high': df_reset['high'].tolist(),
            'low': df_reset['low'].tolist(),
            'close': df_reset['close'].tolist()
        }

        # Create candlestick chart
        fig = go.Figure(data=go.Candlestick(
            x=data['dates'],
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            name='Gold Price'
        ))

        fig.update_layout(
            title=f'Gold Prices ({interval.upper()})',
            xaxis_title='Date',
            yaxis_title='Price (USD)',
            template='plotly_white',
            height=500
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    except Exception as e:
        logger.error(f"Error generating chart: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/news')
def get_news():
    """Get recent gold news articles."""
    try:
        limit = request.args.get('limit', 20, type=int)
        category = request.args.get('category', None)

        # Fetch news - convert to list format
        try:
            news_df = news_fetcher.get_cached_news(days=7, category=category)
        except Exception as e:
            logger.warning(f"Error fetching cached news: {e}")
            news_df = pd.DataFrame()

        if news_df.empty:
            news_data = []
        else:
            # Convert DataFrame to list of dicts
            news_data = []
            for _, row in news_df.head(limit).iterrows():
                # Handle datetime parsing safely
                published_date = row.get('published_date', '')
                if isinstance(published_date, str) and published_date:
                    try:
                        # Try different datetime formats
                        if '+' in published_date or 'Z' in published_date:
                            published_date = pd.to_datetime(published_date, format='ISO8601').strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            published_date = str(published_date)
                    except:
                        published_date = str(published_date)

                news_data.append({
                    'title': row['title'],
                    'summary': row.get('summary', ''),
                    'link': row.get('link', ''),
                    'publisher': row.get('publisher', 'Unknown'),
                    'published_date': published_date,
                    'sentiment_score': row.get('sentiment_score', 0)
                })



        return jsonify({
            'articles': news_data,
            'count': len(news_data)
        })

    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/news/fetch')
def fetch_fresh_news():
    """Fetch fresh news from external sources."""
    try:
        # Fetch new articles
        results = news_fetcher.fetch_and_cache_gold_news()

        return jsonify({
            'message': 'News fetched successfully',
            'articles_fetched': sum(results.values()) if results else 0
        })

    except Exception as e:
        logger.error(f"Error fetching fresh news: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/news/analyze')
def analyze_news():
    """Analyze news sentiment and generate summary."""
    try:
        # Get recent news for analysis
        try:
            news_df = news_fetcher.get_cached_news(days=7)
        except Exception as e:
            logger.warning(f"Error fetching news for analysis: {e}")
            return jsonify({'error': f'Error fetching news: {str(e)}'}), 500

        if news_df.empty:
            return jsonify({'error': 'No news data available for analysis'}), 404

        # Use built-in sentiment analysis from the analyzer
        try:
            sentiment_trend = news_analyzer.get_sentiment_trend(days=7)
            keyword_analysis = news_analyzer.get_keyword_analysis(days=7)
        except Exception as e:
            logger.warning(f"Error in sentiment analysis: {e}")
            # Provide fallback analysis
            sentiment_trend = {'average_sentiment': 0, 'positive_articles': 0, 'negative_articles': 0, 'total_articles': len(news_df)}
            keyword_analysis = {'keywords': []}

        # Extract sentiment data from analyzer response
        summary = sentiment_trend.get('summary', {})
        avg_sentiment = summary.get('avg_sentiment', 0)
        total_articles = summary.get('total_articles', 0)

        # Categorize sentiment
        if avg_sentiment > 0.1:
            sentiment_label = 'Positive'
        elif avg_sentiment < -0.1:
            sentiment_label = 'Negative'
        else:
            sentiment_label = 'Neutral'

        # Get top keywords from keyword analysis
        top_keywords = []
        if 'top_keywords' in keyword_analysis:
            for keyword, data in list(keyword_analysis['top_keywords'].items())[:10]:
                top_keywords.append({
                    'keyword': keyword,
                    'count': data.get('count', 0)
                })

        # Calculate sentiment distribution from daily data
        positive_count = 0
        negative_count = 0
        neutral_count = 0

        for day_data in sentiment_trend.get('daily_data', []):
            day_sentiment = day_data.get('avg_sentiment', 0)
            day_count = day_data.get('article_count', 0)

            if day_sentiment > 0.1:
                positive_count += day_count
            elif day_sentiment < -0.1:
                negative_count += day_count
            else:
                neutral_count += day_count

        return jsonify({
            'overall_sentiment': avg_sentiment,
            'sentiment_label': sentiment_label,
            'articles_analyzed': total_articles,
            'top_keywords': top_keywords,
            'sentiment_distribution': {
                'positive': positive_count,
                'negative': negative_count,
                'neutral': neutral_count
            }
        })

    except Exception as e:
        logger.error(f"Error analyzing news: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/trading/analyze')
def trading_analysis():
    """Perform trading analysis on current data."""
    try:
        # Get recent price data
        df = gold_fetcher.get_cached_data('15m')
        if df.empty:
            return jsonify({'error': 'No price data available for analysis'}), 404

        # Get trading recommendation which includes analysis
        recommendation = trading_analyzer.get_trading_recommendation()

        # Save the recommendation to database
        if recommendation and not recommendation.get('error'):
            trading_analyzer.save_recommendation(recommendation)

        # Add current price info
        current_price = df['close'].iloc[-1] if not df.empty else None
        price_change = df['close'].iloc[-1] - df['close'].iloc[-2] if len(df) >= 2 else 0
        price_change_pct = (price_change / df['close'].iloc[-2] * 100) if len(df) >= 2 and df['close'].iloc[-2] != 0 else 0

        return jsonify({
            'current_price': current_price,
            'price_change': price_change,
            'price_change_percent': price_change_pct,
            'analysis': recommendation.get('analysis', {}),
            'recommendation': recommendation.get('recommendation', ''),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error performing trading analysis: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/complete-analysis')
def complete_analysis():
    """Perform complete analysis including prices, news, and trading signals."""
    try:
        # Get price data
        price_df = gold_fetcher.get_cached_data('15m')
        current_price = price_df['close'].iloc[-1] if not price_df.empty else None

        # Get recent headlines
        headlines_list = news_fetcher.get_recent_headlines(limit=20)

        # Get sentiment analysis
        try:
            sentiment_analysis = news_analyzer.get_sentiment_trend(days=3)
            avg_sentiment = sentiment_analysis.get('average_sentiment', 0)
        except Exception as e:
            logger.warning(f"Error in sentiment analysis: {e}")
            sentiment_analysis = {'average_sentiment': 0, 'total_articles': 0}
            avg_sentiment = 0

        # Get trading recommendation
        try:
            trading_recommendation = trading_analyzer.get_trading_recommendation() if not price_df.empty else {}
            # Save the recommendation to database
            if trading_recommendation and not trading_recommendation.get('error'):
                trading_analyzer.save_recommendation(trading_recommendation)
        except Exception as e:
            logger.warning(f"Error in trading analysis: {e}")
            trading_recommendation = {'summary': 'Trading analysis unavailable', 'analysis': {}}

        # Generate AI summary - use trading recommendation summary
        ai_summary = trading_recommendation.get('recommendation', 'AI summary unavailable')

        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'current_price': current_price,
            'sentiment': {
                'score': avg_sentiment,
                'articles_analyzed': sentiment_analysis.get('total_articles', 0)
            },
            'trading_analysis': trading_recommendation,
            'recent_news': headlines_list[:5],  # Top 5 articles
            'ai_summary': ai_summary
        })

    except Exception as e:
        logger.error(f"Error performing complete analysis: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/latest-ai-analysis')
def get_latest_ai_analysis():
    """Get the latest cached AI analysis."""
    try:
        latest = trading_analyzer.get_latest_recommendation()
        return jsonify(latest)

    except Exception as e:
        logger.error(f"Error getting latest AI analysis: {e}")
        return jsonify({
            'has_cached_analysis': False,
            'error': str(e)
        }), 500


@app.route('/api/status')
def system_status():
    """Get system status and health check."""
    try:
        # Check database connectivity
        db_status = True
        try:
            df_test = gold_fetcher.get_cached_data('15m', days=1)
            db_status = not df_test.empty
        except:
            db_status = False

        # Check if we have recent data
        has_price_data = False
        has_news_data = False

        try:
            df = gold_fetcher.get_cached_data('15m')
            has_price_data = not df.empty
        except:
            pass

        try:
            news_df = news_fetcher.get_cached_news(days=1)
            has_news_data = not news_df.empty
        except Exception as e:
            logger.warning(f"Error checking news data: {e}")
            has_news_data = False

        return jsonify({
            'status': 'healthy' if db_status and has_price_data else 'degraded',
            'database': 'connected' if db_status else 'error',
            'price_data': 'available' if has_price_data else 'unavailable',
            'news_data': 'available' if has_news_data else 'unavailable',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error checking status: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


def is_port_in_use(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def main():
    """Run the Flask application."""
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'

    # Check if port is in use and find alternative
    if is_port_in_use(port):
        print(f"⚠️  Port {port} is in use, trying alternative ports...")
        for alternative_port in range(5001, 5010):
            if not is_port_in_use(alternative_port):
                port = alternative_port
                break
        else:
            print("❌ Could not find an available port between 5001-5009")
            return

    print("🚀 Starting Gold Digger Web Application...")
    print(f"📊 Dashboard will be available at: http://localhost:{port}")
    print(f"🔧 Debug routes: http://localhost:{port}/debug and http://localhost:{port}/test")
    print("💡 Press Ctrl+C to stop the server")

    # Add more verbose logging
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} became unavailable. Please try again.")
        else:
            raise


if __name__ == '__main__':
    main()
