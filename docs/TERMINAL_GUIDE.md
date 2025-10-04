# Gold Digger Terminal - Quick Usage Guide

## 🚀 Getting Started

The Gold Digger Terminal is a unified interface that consolidates all functionality into one easy-to-use application.

### Launch Options

```bash
# Option 1: Shell wrapper (recommended)
./gold_digger.sh

# Option 2: Direct Python execution
python3 gold_digger_terminal.py

# Option 3: Simple launcher
python3 gold_digger.py
```

### Command Line Options

```bash
# Quick analysis without menu
./gold_digger.sh --quick

# Test system setup
./gold_digger.sh --test

# Show configuration
./gold_digger.sh --config

# Run setup wizard
./gold_digger.sh --setup

# Show help
./gold_digger.sh --help
```

## 📋 Menu Overview

When you launch the terminal, you'll see a menu with the following categories:

### 📊 Price Data & Analysis (Options 1-4)
- **1**: Fetch current gold prices (15m/30m intervals)
- **2**: Run AI trading analysis with recommendations
- **3**: View summary of cached price data
- **4**: Export price data to CSV files

### 📰 News & Sentiment (Options 5-10)
- **5**: Fetch latest gold-related news articles
- **6**: View news cache summary with sentiment scores
- **7**: Interactive news browser with search
- **8**: Detailed sentiment analysis over time
- **9**: Search news by specific keywords
- **10**: Export news reports to HTML

### 🤖 Comprehensive Analysis (Options 11-14)
- **11**: Complete analysis (prices + news + AI)
- **12**: Quick analysis (streamlined version)
- **13**: News-only analysis (sentiment + categories)
- **14**: Price-only analysis (technical indicators)

### 📋 Data Exploration (Options 15-18)
- **15**: Database query examples and statistics
- **16**: View database table statistics
- **17**: Browse recent news headlines
- **18**: News category breakdown analysis

### ⚙️ Configuration & Setup (Options 19-22)
- **19**: View current system configuration
- **20**: Run interactive setup wizard
- **21**: Test system components and dependencies
- **22**: Install missing dependencies

### 🔧 Utilities
- **0**: Exit application
- **h**: Show menu again
- **c**: Clear screen

## 🎯 Common Workflows

### First-Time Setup
1. Run `./gold_digger.sh --setup` or choose option **20**
2. Test setup with option **21**
3. View configuration with option **19**

### Daily Trading Analysis
1. Choose option **12** for quick analysis, or
2. Choose option **11** for complete analysis
3. Review AI recommendations and news sentiment

### News Monitoring
1. Choose option **5** to fetch latest news
2. Choose option **8** for sentiment analysis
3. Choose option **7** for interactive browsing

### Data Export
1. Choose option **4** for price data CSV export
2. Choose option **10** for news HTML reports

## 💡 Tips

- **First run**: Always start with option **20** (Setup Wizard)
- **Daily use**: Option **12** (Quick Analysis) is fastest
- **Deep dive**: Option **11** (Complete Analysis) for full insights
- **News focus**: Option **13** for news-only analysis
- **Technical focus**: Option **14** for price-only analysis

## 🔧 Troubleshooting

If you encounter issues:

1. **Dependencies missing**: Choose option **22**
2. **Setup problems**: Choose option **20**
3. **System test**: Choose option **21**
4. **Configuration check**: Choose option **19**

## 📊 What Each Analysis Provides

### Quick Analysis (Option 12)
- 3 days of price data
- Latest news headlines
- AI trading recommendation
- Fast execution (~2-3 minutes)

### Complete Analysis (Option 11)
- 14 days of price data
- Comprehensive news analysis
- Detailed sentiment trends
- AI recommendation with reasoning
- Full execution (~5-10 minutes)

### News-Only Analysis (Option 13)
- Latest news fetch
- Sentiment analysis
- Category breakdown
- Publisher analysis
- Keyword trends

### Price-Only Analysis (Option 14)
- Price data fetch
- Technical indicators
- Volume analysis
- AI recommendation (price-based only)

## 🚨 Prerequisites

Before using the terminal, ensure:

1. **Python 3.8+** is installed
2. **Virtual environment** is activated (automatic with shell script)
3. **Dependencies** are installed (use option 22)
4. **Ollama** is running with gpt-oss:20b model
5. **Internet connection** for data fetching

## 📈 Understanding AI Recommendations

The AI provides:
- **Position**: LONG/SHORT/HOLD
- **Confidence Level**: LOW/MEDIUM/HIGH
- **Entry/Exit Points**: Specific price levels
- **Risk Assessment**: Stop-loss and take-profit levels
- **Reasoning**: Why the recommendation was made

## 🔄 Data Refresh

- **Price data**: Fetched in real-time when requested
- **News data**: Cached to avoid rate limits
- **AI analysis**: Uses latest available data
- **Database**: Automatically maintained and deduplicated

## 💾 File Outputs

The terminal creates:
- **gold_prices.db**: SQLite database with all data
- ***.csv**: Price data exports
- ***.html**: News reports
- **exports/**: Directory for all export files

---

**Need help?** Use option **h** to show the menu anytime, or refer to the main README.md for detailed documentation.