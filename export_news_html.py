#!/usr/bin/env python3
"""
Export Gold News to HTML
Creates a simple HTML file with cached news articles for easy viewing in browser.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from config import get_config

# Get configuration
config = get_config()

class NewsHTMLExporter:
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the HTML exporter with database path."""
        self.db_path = db_path or config.database_path

    def get_news_data(self, days: int = 7, limit: int = 100) -> List[Dict]:
        """Get news data from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)

                query = '''
                    SELECT id, title, summary, link, publisher, published_date,
                           sentiment_score, category, keywords
                    FROM gold_news
                    WHERE published_date >= ?
                    ORDER BY published_date DESC
                    LIMIT ?
                '''

                cursor = conn.cursor()
                cursor.execute(query, (start_date.isoformat(), limit))

                articles = []
                for row in cursor.fetchall():
                    try:
                        keywords = json.loads(row[8]) if row[8] else []
                    except json.JSONDecodeError:
                        keywords = []

                    articles.append({
                        'id': row[0],
                        'title': row[1],
                        'summary': row[2],
                        'link': row[3],
                        'publisher': row[4],
                        'published_date': row[5],
                        'sentiment_score': row[6] or 0,
                        'category': row[7] or 'general',
                        'keywords': keywords
                    })

                return articles

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

    def generate_html(self, articles: List[Dict], title: str = "Gold News Report") -> str:
        """Generate HTML content for news articles."""

        # Calculate stats
        total_articles = len(articles)
        avg_sentiment = sum(a['sentiment_score'] for a in articles) / total_articles if total_articles > 0 else 0

        # Count categories
        category_counts = {}
        for article in articles:
            cat = article['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}

        .header {{
            background: linear-gradient(135deg, #ffd700, #ffed4e);
            color: #333;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}

        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #ffd700;
        }}

        .stat-label {{
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }}

        .filters {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .filter-buttons {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }}

        .filter-btn {{
            padding: 8px 16px;
            border: 2px solid #ffd700;
            background: white;
            color: #333;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.3s;
        }}

        .filter-btn:hover, .filter-btn.active {{
            background: #ffd700;
            color: #333;
        }}

        .articles {{
            display: grid;
            gap: 20px;
        }}

        .article {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .article:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}

        .article-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }}

        .article-title {{
            font-size: 1.3em;
            font-weight: 600;
            margin: 0;
            flex: 1;
            margin-right: 15px;
        }}

        .article-title a {{
            color: #333;
            text-decoration: none;
        }}

        .article-title a:hover {{
            color: #ffd700;
        }}

        .sentiment-badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            white-space: nowrap;
        }}

        .sentiment-positive {{
            background: #d4edda;
            color: #155724;
        }}

        .sentiment-negative {{
            background: #f8d7da;
            color: #721c24;
        }}

        .sentiment-neutral {{
            background: #e2e3e5;
            color: #383d41;
        }}

        .article-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            font-size: 0.9em;
            color: #666;
            margin-bottom: 15px;
        }}

        .meta-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}

        .category-tag {{
            background: #f0f0f0;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            color: #666;
        }}

        .article-summary {{
            line-height: 1.6;
            margin-bottom: 15px;
        }}

        .keywords {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}

        .keyword {{
            background: #fff3cd;
            color: #856404;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.8em;
        }}

        .footer {{
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }}

        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}

            .header {{
                padding: 20px;
            }}

            .article-header {{
                flex-direction: column;
                align-items: flex-start;
            }}

            .sentiment-badge {{
                margin-top: 10px;
            }}

            .filter-buttons {{
                justify-content: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏆 {title}</h1>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="stats">
        <div class="stat-card">
            <div class="stat-value">{total_articles}</div>
            <div class="stat-label">Total Articles</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{avg_sentiment:.2f}</div>
            <div class="stat-label">Avg Sentiment</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len(category_counts)}</div>
            <div class="stat-label">Categories</div>
        </div>
    </div>

    <div class="filters">
        <h3>📂 Filter by Category</h3>
        <div class="filter-buttons">
            <button class="filter-btn active" onclick="filterArticles('all')">All</button>'''

        # Add category filter buttons
        for category in sorted(category_counts.keys()):
            display_name = category.replace('_', ' ').title()
            html += f'''
            <button class="filter-btn" onclick="filterArticles('{category}')">{display_name} ({category_counts[category]})</button>'''

        html += '''
        </div>
    </div>

    <div class="articles" id="articles">'''

        # Add articles
        for article in articles:
            sentiment_class = 'positive' if article['sentiment_score'] > 0.1 else 'negative' if article['sentiment_score'] < -0.1 else 'neutral'
            sentiment_emoji = '📈' if article['sentiment_score'] > 0.1 else '📉' if article['sentiment_score'] < -0.1 else '📊'

            # Format date
            try:
                pub_date = datetime.fromisoformat(article['published_date'].replace('Z', '+00:00'))
                date_str = pub_date.strftime('%Y-%m-%d %H:%M')
            except:
                date_str = article['published_date'][:16] if article['published_date'] else 'Unknown'

            html += f'''
        <div class="article" data-category="{article['category']}">
            <div class="article-header">
                <h2 class="article-title">
                    <a href="{article['link']}" target="_blank">{article['title']}</a>
                </h2>
                <div class="sentiment-badge sentiment-{sentiment_class}">
                    {sentiment_emoji} {article['sentiment_score']:.2f}
                </div>
            </div>

            <div class="article-meta">
                <div class="meta-item">
                    <span>📺</span> {article['publisher']}
                </div>
                <div class="meta-item">
                    <span>📅</span> {date_str}
                </div>
                <div class="meta-item">
                    <span class="category-tag">{article['category'].replace('_', ' ').title()}</span>
                </div>
            </div>

            <div class="article-summary">
                {article['summary'] or 'No summary available.'}
            </div>'''

            if article['keywords']:
                html += '''
            <div class="keywords">'''
                for keyword in article['keywords'][:8]:  # Show max 8 keywords
                    html += f'<span class="keyword">{keyword}</span>'
                html += '''
            </div>'''

            html += '''
        </div>'''

        html += '''
    </div>

    <div class="footer">
        <p>📰 Gold News Report | Generated by Gold Digger System</p>
        <p>⚠️ This data is for educational purposes only. Always do your own research.</p>
    </div>

    <script>
        function filterArticles(category) {
            const articles = document.querySelectorAll('.article');
            const buttons = document.querySelectorAll('.filter-btn');

            // Update active button
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');

            // Filter articles
            articles.forEach(article => {
                if (category === 'all' || article.dataset.category === category) {
                    article.style.display = 'block';
                } else {
                    article.style.display = 'none';
                }
            });
        }

        // Add smooth scrolling for better UX
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });
    </script>
</body>
</html>'''

        return html

    def export_to_file(self, filename: str = "gold_news_report.html", days: int = 7) -> bool:
        """Export news to HTML file."""
        try:
            articles = self.get_news_data(days)

            if not articles:
                print("❌ No articles found for export")
                return False

            title = f"Gold News Report - Last {days} Days"
            html_content = self.generate_html(articles, title)

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)

            print(f"✅ Exported {len(articles)} articles to {filename}")
            return True

        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False

def main():
    """Main function for HTML export."""
    import argparse

    parser = argparse.ArgumentParser(description='Export Gold News to HTML')
    parser.add_argument('--output', '-o', default='gold_news_report.html',
                       help='Output HTML filename')
    parser.add_argument('--days', '-d', type=int, default=7,
                       help='Days to include (default: 7)')

    args = parser.parse_args()

    exporter = NewsHTMLExporter()
    success = exporter.export_to_file(args.output, args.days)

    if success:
        print(f"🌐 Open {args.output} in your browser to view the news report")

if __name__ == "__main__":
    main()
