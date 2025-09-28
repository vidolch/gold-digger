# Gold Digger 📈💰📰

A comprehensive Python system that fetches gold price data and news, caches them intelligently in SQLite, and provides AI-powered trading analysis using Ollama's gpt-oss:20b model for CFD trading recommendations.

## 🚀 NEW: Unified Terminal Application

**The easiest way to use Gold Digger is now through the unified terminal interface:**

```bash
# Quick start - run the unified terminal
./gold_digger.sh

# Or directly with Python
python3 gold_digger_terminal.py

# Or use the simple launcher
python3 gold_digger.py
```

The unified terminal provides:
- 📊 All price data fetching and analysis
- 📰 Complete news management and sentiment analysis  
- 🤖 AI trading recommendations
- ⚙️ Configuration and setup tools
- 📋 Data exploration and export features

**No more running multiple scripts!** Everything is accessible through one interactive menu.

## Features

### 📊 Data Fetching & Caching
- **Smart Price Caching**: Fetches gold prices in 15m and 30m intervals with intelligent duplicate avoidance
- **News Aggregation**: Collects news from multiple gold-related symbols (GC=F, GOLD, GLD, IAU)
- **SQLite Storage**: Efficient local caching prevents redundant API calls
- **Automatic Deduplication**: Content hashing prevents duplicate articles
- **Rate Limiting**: Configurable delays to respect API limits

### 🤖 AI Trading Analysis
- **Ollama Integration**: Uses gpt-oss:20b model for intelligent market analysis
- **Multi-Modal Analysis**: Combines price data with news sentiment for comprehensive insights
- **CFD Trading Focus**: Specialized for Contract for Difference trading recommendations
- **Risk Assessment**: Provides position recommendations with stop-loss and take-profit levels
- **Historical Tracking**: Saves all recommendations to database for performance analysis

### 📰 News Intelligence System
- **Sentiment Analysis**: Advanced sentiment scoring (-1.0 to +1.0) for market impact assessment
- **Smart Categorization**: Auto-categorizes news (monetary_policy, market_movement, geopolitical, etc.)
- **Keyword Extraction**: Identifies trending keywords and their market implications
- **Publisher Analysis**: Tracks publisher sentiment bias and reliability
- **Market Signal Detection**: Identifies news-driven trading opportunities

### 🔧 Configuration & Customization
- **Environment Variables**: Complete .env configuration system
- **Customizable Prompts**: AI analysis prompts stored in editable files
- **Multiple Export Formats**: CSV, HTML, and database exports
- **Interactive Tools**: Command-line browsers and web interfaces
- **Mock Data Support**: Testing capabilities with synthetic data

## Prerequisites

### Quick Setup (Recommended)
```bash
# Clone the repository
cd gold-digger

# Run automated setup
python3 configure.py --quick
```

### Manual Setup

#### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Configure Environment
```bash
# Copy configuration template
cp .env.example .env

# Edit with your preferences
nano .env
```

#### 3. Install Ollama & Model
```bash
# Install Ollama from https://ollama.ai
ollama serve

# Install required model
ollama pull gpt-oss:20b
```

#### 4. Verify Setup
```bash
python3 configure.py --test
```

## Usage Guide

### 🚀 Quick Start Commands

**RECOMMENDED: Use the Unified Terminal**
```bash
# Start the unified terminal (easiest way)
./gold_digger.sh

# Quick analysis without interactive menu
./gold_digger.sh --quick

# Test your setup
./gold_digger.sh --test

# Show configuration
./gold_digger.sh --config
```

**Alternative: Individual Scripts (Legacy)**
```bash
# Activate virtual environment (if using one)
source venv/bin/activate

# Complete analysis workflow
python3 run_complete_analysis.py --quick

# Just price analysis
python3 gold_fetcher.py --analyze

# News-only analysis
python3 run_complete_analysis.py --news-only
```

### 📈 Price Data Commands

```bash
# Fetch gold prices (creates database)
python3 gold_fetcher.py

# Fetch with custom parameters
python3 gold_fetcher.py --days 30

# Get trading analysis
python3 gold_fetcher.py --analyze

# Skip fetching, just analyze
python3 gold_fetcher.py --skip-fetch --analyze

# View configuration
python3 gold_fetcher.py --config-summary
```

### 📰 News Commands

```bash
# Fetch latest news
python3 news_fetcher.py --fetch

# View news summary
python3 news_fetcher.py --summary

# Search news by keyword
python3 news_fetcher.py --search "fed"
python3 news_fetcher.py --search "inflation"

# Recent headlines
python3 news_fetcher.py --headlines 15

# Filter by category
python3 news_fetcher.py --headlines 20 --category monetary_policy
```

### 🔍 Advanced News Viewing

```bash
# Interactive news browser
python3 news_viewer.py --interactive

# Browse with details
python3 news_viewer.py --browse --limit 10 --details

# Database statistics
python3 news_viewer.py --stats

# Search with filters
python3 news_viewer.py --search "central bank" --details

# View specific article
python3 news_viewer.py --article 42

# Filter by sentiment
python3 news_viewer.py --browse --min-sentiment 0.2
```

### 📊 News Analysis Commands

```bash
# Complete trading analysis
python3 news_analyzer.py --trading-summary

# Sentiment trend analysis
python3 news_analyzer.py --sentiment --days 7

# Category breakdown
python3 news_analyzer.py --categories

# Keyword analysis
python3 news_analyzer.py --keywords --days 5

# Publisher analysis
python3 news_analyzer.py --publishers
```

### 🤖 AI Trading Analysis

```bash
# AI recommendation with news
python3 trading_analyzer.py

# Fetch news first, then analyze
python3 trading_analyzer.py --fetch-news

# Price analysis only (no news)
python3 trading_analyzer.py --no-news

# Custom parameters
python3 trading_analyzer.py --interval 30m --hours 48

# View configuration
python3 trading_analyzer.py --config-summary
```

### 🏆 Complete Analysis Suite

```bash
# Full comprehensive analysis
python3 run_complete_analysis.py

# Quick mode (price + news + AI)
python3 run_complete_analysis.py --quick

# Custom time periods
python3 run_complete_analysis.py --days 21

# Skip specific components
python3 run_complete_analysis.py --skip-news-fetch
python3 run_complete_analysis.py --skip-trading

# News-only mode
python3 run_complete_analysis.py --news-only
```

### 📤 Export & Visualization

```bash
# Export news to HTML
python3 export_news_html.py --days 7 --output report.html

# Export data using query examples
python3 query_example.py

# Create price trend charts
python3 query_example.py  # Uncomment plotting lines
```

### ⚙️ Configuration Management

```bash
# Interactive setup wizard
python3 configure.py

# Install dependencies only
python3 configure.py --install-deps

# Install Ollama model only
python3 configure.py --install-model

# Test current setup
python3 configure.py --test

# Reset configuration
python3 configure.py --reset
```

## Configuration (.env)

### Core Settings
```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434    # Ollama server address
OLLAMA_MODEL=gpt-oss:20b             # AI model to use
OLLAMA_TIMEOUT=120                   # Request timeout

# Database
DATABASE_PATH=gold_prices.db         # SQLite database location

# Analysis Defaults
DEFAULT_INTERVAL=15m                 # Price data interval
DEFAULT_ANALYSIS_HOURS=24           # Hours of data to analyze
DEFAULT_FETCH_DAYS=14               # Days of historical data
DEFAULT_NEWS_DAYS=7                 # Days of news to analyze

# News Configuration
NEWS_SYMBOLS=GC=F,GOLD,GLD,IAU      # Symbols to fetch news from
MAX_ARTICLES_PER_SYMBOL=30          # Articles per symbol
ENABLE_SENTIMENT_ANALYSIS=true      # Enable sentiment analysis
AUTO_CATEGORIZE_NEWS=true           # Auto-categorize articles
```

### Advanced Settings
```bash
# API Configuration
API_DELAY=1.0                       # Delay between API calls
MAX_RETRIES=3                       # Retry failed calls
YFINANCE_TIMEOUT=30                # Yahoo Finance timeout

# Risk Management
DEFAULT_RISK_LEVEL=MEDIUM          # LOW, MEDIUM, HIGH
DEFAULT_POSITION_SIZE=0.05         # Position size as % of portfolio

# Development
DEBUG_MODE=false                   # Enable debug output
USE_MOCK_DATA=false               # Use synthetic data
USE_MOCK_NEWS=false               # Use synthetic news
```

## Interactive Commands Reference

### News Viewer Interactive Mode
```bash
python3 news_viewer.py --interactive

# Commands within interactive mode:
stats                    # Show database statistics
browse [number]         # Browse recent headlines
search <keyword>        # Search articles
article <id>           # View specific article details
quit                   # Exit interactive mode
```

### Available Categories
- `monetary_policy` - Federal Reserve, interest rates, central bank decisions
- `market_movement` - Trading activity, price movements, market trends
- `geopolitical` - International tensions, wars, political events
- `economic_data` - GDP, employment, inflation data
- `supply_demand` - Mining, production, commodity supply chains
- `general` - Other gold-related news

## Database Schema

### Price Data Tables
```sql
-- 15-minute interval gold prices
gold_prices_15m (datetime, open, high, low, close, volume, created_at)

-- 30-minute interval gold prices
gold_prices_30m (datetime, open, high, low, close, volume, created_at)

-- AI trading recommendations
trading_recommendations (timestamp, interval_used, current_price, recommendation, success)
```

### News Data Tables
```sql
-- News articles with sentiment analysis
gold_news (id, title, summary, link, publisher, published_date, symbol, 
          sentiment_score, keywords, category, created_at)

-- News fetch history for monitoring
news_fetch_history (symbol, fetch_date, articles_count, success, error_message)
```

## Sample Outputs

### AI Trading Recommendation
```
🏆 GOLD TRADING ANALYSIS & RECOMMENDATION
📊 Analysis Time: 2025-09-28T10:30:15
📈 Current Gold Price: $2,045.50
📰 Analysis Type: News + Price Analysis

🤖 AI TRADING RECOMMENDATION:
**TRADING RECOMMENDATION:**
- Position: LONG
- Confidence Level: HIGH
- Entry Price Target: $2,043.00
- Stop Loss: $2,035.00
- Take Profit: $2,055.00

**REASONING:**
Gold shows strong bullish momentum supported by technical breakout 
and positive news sentiment around Federal Reserve dovish signals.

**KEY FACTORS:**
- Strong support at $2,040 level
- Volume increase on advances
- Fed uncertainty driving positive sentiment (0.35 score)
- Geopolitical tensions supporting safe-haven demand

**RISK ASSESSMENT:**
- Risk Level: MEDIUM
- Risk/Reward Ratio: 1:1.5
- News Risk Factor: Positive sentiment reduces downside risk
```

### News Analysis Summary
```
📰 GOLD NEWS CACHE SUMMARY
📊 Total Articles: 40
📈 Average Sentiment: 0.191 (slightly positive)
🗓️ Date Range: 2025-09-21 to 2025-09-28

📂 Articles by Category:
• Market Movement: 9
• General: 5
• Supply Demand: 3
• Geopolitical: 2

📺 Top Publishers:
• Simply Wall St.: 7
• MarketWatch: 6
• Reuters: 3
```

## File Structure

```
gold-digger/
├── 🚀 UNIFIED TERMINAL (NEW!)
│   ├── gold_digger_terminal.py      # Main unified terminal application
│   ├── gold_digger.py               # Simple launcher script
│   └── gold_digger.sh               # Shell wrapper for easy execution
│
├── 📊 CORE SYSTEM
│   ├── gold_fetcher.py              # Price data fetching & caching
│   ├── trading_analyzer.py          # AI-powered trading analysis
│   ├── config.py                    # Configuration management
│   └── run_complete_analysis.py     # Comprehensive analysis runner
│
├── 📰 NEWS SYSTEM
│   ├── news_fetcher.py              # News fetching & caching
│   ├── news_analyzer.py             # Sentiment & market analysis
│   ├── news_viewer.py               # Interactive news browser
│   └── export_news_html.py          # HTML report generation
│
├── ⚙️ CONFIGURATION
│   ├── configure.py                 # Setup & management utility
│   ├── .env                         # Your configuration file
│   ├── .env.example                 # Configuration template
│   └── trading_prompt.txt           # AI analysis prompt template
│
├── 📋 UTILITIES
│   ├── query_example.py             # Data analysis examples
│   ├── requirements.txt             # Python dependencies
│   └── README.md                    # This documentation
│
└── 💾 DATA (auto-generated)
    ├── gold_prices.db               # SQLite database
    ├── exports/                     # CSV exports directory
    ├── *.csv                        # Individual data exports
    ├── *.html                       # HTML reports
    └── *.log                        # Log files
```

## API Data Sources

### Price Data
- **Yahoo Finance** (`yfinance` library)
- **Symbol**: GC=F (Gold Futures)
- **Intervals**: 15m, 30m (configurable)
- **Rate Limiting**: Built-in delays and retry logic

### News Data
- **Yahoo Finance News API**
- **Symbols**: GC=F, GOLD, GLD, IAU (configurable)
- **Processing**: Sentiment analysis, categorization, keyword extraction
- **Deduplication**: Content-based hashing prevents duplicates

## Troubleshooting

### Setup Issues
```bash
# Run configuration wizard
python3 configure.py

# Test current setup
python3 configure.py --test

# Check configuration
python3 gold_fetcher.py --config-summary
```

### Ollama Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Install model
ollama pull gpt-oss:20b

# Test with different model
# Edit OLLAMA_MODEL in .env file
```

### Database Issues
```bash
# Check if tables exist
python3 -c "
import sqlite3
conn = sqlite3.connect('gold_prices.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')
print('Tables:', cursor.fetchall())
"

# Reinitialize database
rm gold_prices.db
python3 gold_fetcher.py
python3 news_fetcher.py --fetch
```

### Data Issues
```bash
# Test with mock data
# Set USE_MOCK_DATA=true in .env
# Set USE_MOCK_NEWS=true in .env

# Check API connectivity
python3 -c "import yfinance as yf; print(yf.Ticker('GC=F').info['regularMarketPrice'])"

# Verify news data
python3 -c "import yfinance as yf; print(len(yf.Ticker('GC=F').news))"
```

### Performance Issues
```bash
# Increase API delays in .env
API_DELAY=2.0

# Reduce data fetch amounts
DEFAULT_FETCH_DAYS=7
MAX_ARTICLES_PER_SYMBOL=20

# Enable debug mode
DEBUG_MODE=true
```

## Remote/Cloud Deployment

### Docker Configuration
```bash
# Use remote Ollama instance
OLLAMA_HOST=http://ollama-server:11434

# Cloud database path
DATABASE_PATH=/data/gold_prices.db

# Log to files for monitoring
ENABLE_FILE_LOGGING=true
LOG_FILE=/logs/gold_digger.log
```

### Environment Examples
```bash
# Development
OLLAMA_HOST=http://localhost:11434
DEBUG_MODE=true
USE_MOCK_DATA=false

# Production
OLLAMA_HOST=http://production-ollama:11434
DEBUG_MODE=false
LOG_LEVEL=WARNING
ENABLE_FILE_LOGGING=true
```

## Security & Best Practices

### Data Protection
- Database contains market data only (no personal information)
- API keys not required for Yahoo Finance
- Local Ollama instance recommended for privacy
- Regular backups of `.env` and database recommended

### Performance Optimization
- Configure appropriate `API_DELAY` to avoid rate limits
- Use `MAX_RETRIES` for reliable data fetching
- Enable `ENABLE_FILE_LOGGING` for production monitoring
- Consider `USE_MOCK_DATA` for development/testing

## Contributing

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd gold-digger

# Setup development environment
python3 configure.py
python3 configure.py --test

# Enable debug mode
echo "DEBUG_MODE=true" >> .env
```

### Adding Features
- Follow existing code patterns
- Add configuration options to `.env.example`
- Update this README with new commands
- Test with both real and mock data

## Disclaimer

⚠️ **Important**: This system is for educational and research purposes only. 

- **Not Financial Advice**: AI recommendations are algorithmic analysis, not professional financial advice
- **Market Risk**: All trading involves risk of loss
- **Data Accuracy**: Market data accuracy depends on external APIs
- **Personal Responsibility**: Always do your own research and consult financial professionals
- **Testing Recommended**: Use paper trading to validate strategies

## License

This project is for educational use. Users are responsible for compliance with financial data provider terms of service and applicable trading regulations.

---

🏆 **Gold Digger System** - Comprehensive AI-Powered Gold Market Analysis  
📊 Price Data • 📰 News Intelligence • 🤖 AI Trading Analysis • ⚙️ Complete Automation