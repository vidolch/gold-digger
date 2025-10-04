# Gold Digger Web Interface Guide 🌐

A comprehensive guide to using the Gold Digger web-based trading terminal.

## Table of Contents
- [Getting Started](#getting-started)
- [Interface Overview](#interface-overview)
- [Dashboard Features](#dashboard-features)
- [Price Analysis](#price-analysis)
- [News Monitoring](#news-monitoring)
- [Analysis Tools](#analysis-tools)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## Getting Started

### Quick Launch

```bash
# Start with default settings (localhost:5000)
./gold_digger_web.sh

# Or using Python directly
python3 gold_digger_web.py
```

The web interface will automatically:
1. Check and install dependencies
2. Set up the virtual environment
3. Initialize the database
4. Launch the web server
5. Open your default browser

### Launch Options

```bash
# Custom port
./gold_digger_web.sh --port 8080

# Network access (accessible from other devices)
./gold_digger_web.sh --host 0.0.0.0 --port 5000

# Debug mode (shows detailed errors)
./gold_digger_web.sh --debug

# Production mode (optimized for performance)
./gold_digger_web.sh --production

# Setup environment without starting server
./gold_digger_web.sh --setup-only
```

### Accessing the Interface

Once started, open your browser and navigate to:
- **Local access**: `http://localhost:5000`
- **Network access**: `http://YOUR_IP_ADDRESS:5000`

## Interface Overview

### Header Section
- **Logo**: Gold Digger branding
- **Current Price**: Live gold price with change indicator
- **24h Change**: Price change percentage (green/red)
- **System Status**: Health indicator (healthy/degraded/error)
- **Refresh All**: Manual refresh button

### Navigation Tabs
- **Dashboard**: Main overview with key metrics
- **Prices**: Detailed price data and charts
- **News**: News articles and sentiment analysis
- **Analysis**: AI-powered trading insights

## Dashboard Features

### 1. Price Chart
- **Interactive candlestick chart** powered by Plotly
- **Multiple timeframes**: 15m, 30m, 1h, 1d
- **Real-time updates** every 5 minutes
- **Zoom and pan** functionality
- **Responsive design** for all screen sizes

```javascript
// Chart automatically updates based on selected interval
Chart intervals: 15 minutes → 30 minutes → 1 hour → 1 day
```

### 2. AI Market Summary
- **Real-time AI analysis** using Ollama
- **Market sentiment** interpretation
- **Key insights** and recommendations
- **Auto-refresh** with manual refresh option

### 3. Sentiment Analysis
- **Visual sentiment gauge** with needle indicator
- **Color-coded sentiment**: Red (negative) → Yellow (neutral) → Green (positive)
- **Article breakdown**: Positive, neutral, negative counts
- **Real-time updates** based on latest news

### 4. Recent Headlines
- **Top 5 latest news** articles
- **Publisher information** and timestamps
- **Sentiment indicators** for each article
- **One-click refresh** to fetch new articles

## Price Analysis

### Price Data Controls
- **Interval Selection**: Choose from 15m, 30m, 1h, 1d
- **Fetch Prices**: Manual data refresh
- **Auto-refresh**: Automatic updates every 5 minutes

### Price Table Features
- **Real-time OHLCV data** (Open, High, Low, Close, Volume)
- **Sortable columns** for easy analysis
- **Recent 50 entries** displayed by default
- **Responsive table** with horizontal scrolling on mobile
- **Professional formatting** with currency symbols

### Chart Interactions
```javascript
// Interactive features:
- Zoom: Mouse wheel or touch gestures
- Pan: Click and drag
- Reset: Double-click to reset zoom
- Hover: View exact values at any point
```

## News Monitoring

### News Filters
- **Article Limit**: 10, 20, or 50 articles
- **Category Filter**: All, Market, Economic, Political
- **Real-time Filtering**: Instant results without page reload

### Article Display
Each news article shows:
- **Title**: Full article headline
- **Publisher**: News source (Reuters, Bloomberg, etc.)
- **Published Date**: When the article was published
- **Sentiment Score**: Color-coded sentiment indicator
- **Summary**: Article summary when available
- **Read More**: Direct link to full article

### Sentiment Indicators
- 🟢 **Positive**: Green background, optimistic tone
- 🟡 **Neutral**: Gray background, balanced reporting
- 🔴 **Negative**: Red background, concerning news

### Fetching New Articles
```bash
# Manual refresh options:
1. Click "Fetch New" button in Recent Headlines
2. Click "Load News" in News tab
3. Use "Refresh All" in header
```

## Analysis Tools

### Complete Analysis
Provides comprehensive market overview:
- **Current price** and change indicators
- **Trading analysis** with technical indicators
- **Sentiment analysis** from recent news
- **AI-generated summary** with market insights
- **Recent news impact** assessment

### Sentiment Analysis
Deep dive into market sentiment:
- **Overall sentiment score** (-1 to +1 scale)
- **Article distribution** by sentiment
- **Top keywords** from recent news
- **Trend analysis** over time

### Trading Analysis
Technical analysis features:
- **Current price** with change metrics
- **Trend indicators** and signals
- **Volume analysis** patterns
- **Support/resistance** levels (when available)

## Configuration

### Environment Variables
```bash
# .env file settings for web interface
PORT=5000                    # Web server port
HOST=localhost              # Web server host (0.0.0.0 for network access)
FLASK_ENV=development       # development or production
```

### Auto-refresh Settings
```javascript
// Default refresh intervals:
System Status: 5 minutes
Current Price: 5 minutes
Recent Headlines: 5 minutes (dashboard only)
Charts: Manual refresh only (to preserve zoom/pan state)
```

### Browser Compatibility
- **Chrome/Chromium**: Full support
- **Firefox**: Full support
- **Safari**: Full support
- **Edge**: Full support
- **Mobile browsers**: Responsive design

## Advanced Features

### Keyboard Shortcuts
- **Ctrl + R**: Refresh current tab data
- **Tab**: Navigate between tabs
- **Esc**: Close any open modals

### URL Parameters
```bash
# Direct tab access:
http://localhost:5000/#dashboard
http://localhost:5000/#prices
http://localhost:5000/#news
http://localhost:5000/#analysis
```

### API Endpoints
The web interface provides REST API endpoints:

```bash
# System status
GET /api/status

# Price data
GET /api/prices/{interval}
GET /api/prices/chart/{interval}

# News data
GET /api/news
GET /api/news/fetch
GET /api/news/analyze

# Trading analysis
GET /api/trading/analyze

# Complete analysis
GET /api/complete-analysis
```

## Troubleshooting

### Common Issues

#### 1. Server Won't Start
```bash
# Check if port is already in use
lsof -i :5000

# Use different port
./gold_digger_web.sh --port 8080
```

#### 2. Dependencies Missing
```bash
# Install dependencies
pip install -r requirements.txt

# Or let the launcher handle it
./gold_digger_web.sh  # Will auto-install dependencies
```

#### 3. Database Errors
```bash
# Delete and recreate database
rm gold_prices.db
python3 gold_fetcher.py --quick
```

#### 4. Charts Not Loading
- Check browser console for JavaScript errors
- Ensure Plotly CDN is accessible
- Try refreshing the page (Ctrl + F5)

#### 5. API Errors
```bash
# Check server logs in terminal
# Common causes:
- Ollama not running (for AI features)
- Internet connection issues (for data fetching)
- Rate limiting from data providers
```

### Performance Optimization

#### For Large Datasets
```bash
# Limit data fetching in production
export PRICE_DATA_LIMIT=100  # Limit price records
export NEWS_DATA_LIMIT=50    # Limit news articles
```

#### For Slow Networks
```bash
# Reduce auto-refresh frequency
# Edit web/static/js/app.js:
// Change refresh interval from 5 minutes to 10 minutes
this.refreshInterval = setInterval(..., 10 * 60 * 1000);
```

### Network Access

#### Local Network Access
```bash
# Start server on all interfaces
./gold_digger_web.sh --host 0.0.0.0 --port 5000

# Access from other devices on same network
http://YOUR_COMPUTER_IP:5000
```

#### Firewall Configuration
```bash
# Allow port through firewall (Linux)
sudo ufw allow 5000

# Windows Firewall
# Add inbound rule for port 5000 in Windows Firewall settings
```

## Production Deployment

### Using Gunicorn (Recommended)
```bash
# Production mode with Gunicorn
./gold_digger_web.sh --production --host 0.0.0.0 --port 5000

# Or manually
gunicorn --bind 0.0.0.0:5000 --workers 4 web.app:app
```

### Environment Variables for Production
```bash
export FLASK_ENV=production
export HOST=0.0.0.0
export PORT=5000
export WORKERS=4
```

### Security Considerations
- Change default port in production
- Use HTTPS with reverse proxy (nginx/Apache)
- Implement authentication if needed
- Monitor for unusual access patterns

## Support

### Getting Help
- Check this guide for common solutions
- Review terminal output for error messages
- Check browser console for JavaScript errors
- Ensure all dependencies are installed

### Reporting Issues
When reporting issues, include:
- Operating system and version
- Python version
- Browser and version
- Complete error messages
- Steps to reproduce

---

**Happy Trading! 🚀📈💰**

The Gold Digger web interface provides a powerful, user-friendly way to monitor gold markets and make informed trading decisions. For additional features and updates, check the main README.md file.