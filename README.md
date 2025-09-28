# Gold Digger 📈💰

A comprehensive Python system that fetches gold price data (GC=F) from Yahoo Finance, caches it intelligently in SQLite, and provides AI-powered trading analysis using Ollama's gpt-oss:20b model for CFD trading recommendations.

## Features

### Data Fetching & Caching
- Fetches gold prices in both 15-minute and 30-minute intervals
- Retrieves data for the last 14 days by default
- Smart caching system using SQLite database
- Automatically detects missing data ranges and only fetches what's needed
- Prevents duplicate API calls for already cached data
- Comprehensive logging and error handling
- Data summary display

### AI Trading Analysis 🤖
- **Ollama Integration**: Uses gpt-oss:20b model for intelligent analysis
- **CFD Trading Focus**: Specialized for Contract for Difference trading
- **Customizable Prompts**: Trading analysis prompt stored in separate file for easy modification
- **Multiple Timeframes**: Analyze 6h, 24h, 48h periods with different intervals
- **Risk Assessment**: Provides position recommendations with stop-loss and take-profit levels
- **Historical Tracking**: Saves all recommendations to database for performance tracking
- **Professional Output**: Structured trading recommendations with confidence levels

## Prerequisites

### 1. Quick Setup (Recommended)
Run the automated configurator:
```bash
python3 configure.py --quick
```

### 2. Manual Setup

#### Install Dependencies:
```bash
pip install -r requirements.txt
```

#### Setup Configuration:
1. Copy the example configuration:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file with your preferences:
   ```bash
   nano .env
   ```

#### Install and Setup Ollama:
1. Install Ollama from [https://ollama.ai](https://ollama.ai)
2. Start Ollama service
3. Pull the required model:
   ```bash
   ollama pull gpt-oss:20b
   ```

### 3. Verify Setup
```bash
python3 run_complete_analysis.py --quick
```

## Usage

### 1. Basic Price Fetching

Fetch gold prices for the last 14 days:
```bash
python3 gold_fetcher.py
```

Fetch prices and get AI trading analysis:
```bash
python3 gold_fetcher.py --analyze
```

### 2. AI Trading Analysis Only

Run only the trading analysis (skip fetching):
```bash
python3 trading_analyzer.py
```

### 3. Complete Analysis Suite

Run comprehensive analysis with all features:
```bash
python3 run_complete_analysis.py
```

Quick analysis (fetch + AI only):
```bash
python3 run_complete_analysis.py --quick
```

### 4. Available Command Options

```bash
# Gold fetcher options
python3 gold_fetcher.py --days 7 --analyze
python3 gold_fetcher.py --skip-fetch --analyze

# Complete analysis options
python3 run_complete_analysis.py --days 7
python3 run_complete_analysis.py --skip-trading
python3 run_complete_analysis.py --skip-export

# Configuration management
python3 configure.py                    # Interactive setup
python3 configure.py --quick           # Quick setup with defaults
python3 gold_fetcher.py --config-summary  # Show current config
```

## Configuration (.env file)

The system uses a `.env` file for all configuration options. Here are the key settings:

### **Core Configuration**
```bash
# Ollama Settings
OLLAMA_HOST=http://localhost:11434    # Ollama server address
OLLAMA_MODEL=gpt-oss:20b             # AI model to use
OLLAMA_TIMEOUT=120                   # Request timeout in seconds

# Database Settings
DATABASE_PATH=gold_prices.db         # SQLite database location

# Analysis Settings
DEFAULT_INTERVAL=15m                 # Price data interval (15m, 30m, etc.)
DEFAULT_ANALYSIS_HOURS=24           # Hours of data to analyze
DEFAULT_FETCH_DAYS=14               # Days of historical data to fetch
```

### **Advanced Configuration**
```bash
# Logging
LOG_LEVEL=INFO                      # DEBUG, INFO, WARNING, ERROR
ENABLE_FILE_LOGGING=false          # Save logs to file
LOG_FILE=gold_digger.log           # Log file location

# Trading Settings
DEFAULT_RISK_LEVEL=MEDIUM          # LOW, MEDIUM, HIGH
DEFAULT_POSITION_SIZE=0.05         # Position size as % of portfolio
PROMPT_FILE=trading_prompt.txt     # AI analysis prompt template

# API Settings
API_DELAY=1.0                      # Delay between API calls (seconds)
MAX_RETRIES=3                      # Retry failed API calls
YFINANCE_TIMEOUT=30               # Yahoo Finance timeout

# Development
DEBUG_MODE=false                   # Enable debug output
USE_MOCK_DATA=false               # Use fake data for testing
```

### **Remote Ollama Setup**
To use a remote Ollama instance, update your `.env` file:
```bash
OLLAMA_HOST=http://your-server.com:11434
```

Or set environment variable:
```bash
export OLLAMA_HOST="http://192.168.1.100:11434"
```

### Database Structure

The system creates a SQLite database (`gold_prices.db`) with multiple tables:

#### Price Data Tables:
- `gold_prices_15m`: 15-minute interval data
- `gold_prices_30m`: 30-minute interval data

Each price table contains:
- `datetime`: Timestamp of the data point
- `open`: Opening price
- `high`: Highest price
- `low`: Lowest price
- `close`: Closing price
- `volume`: Trading volume
- `created_at`: When the record was cached

#### Trading Analysis Table:
- `trading_recommendations`: AI-generated trading recommendations

Contains:
- `timestamp`: When analysis was performed
- `interval_used`: Data interval for analysis (15m/30m)
- `hours_analyzed`: Time period analyzed
- `current_price`: Gold price at analysis time
- `recommendation`: Full AI recommendation text
- `market_data_points`: Number of data points analyzed
- `success`: Whether analysis completed successfully

### Example Output

#### Basic Price Fetching:
```
2024-01-15 10:30:00 - INFO - Starting gold price fetch for last 14 days
2024-01-15 10:30:00 - INFO - Date range: 2024-01-01 to 2024-01-15

--- Processing 15m interval ---
2024-01-15 10:30:01 - INFO - Fetching 15m data from 2024-01-01 to 2024-01-15
2024-01-15 10:30:05 - INFO - Fetched 1344 records for 15m interval
2024-01-15 10:30:05 - INFO - Saved 1344 records to gold_prices_15m

--- Processing 30m interval ---
2024-01-15 10:30:06 - INFO - All 30m data is already cached

============================================================
GOLD PRICE CACHE SUMMARY
============================================================

15M INTERVAL DATA:
  Records: 1344
  Date range: 2024-01-01 08:00:00 to 2024-01-15 16:30:00
  Latest price: $2045.50

30M INTERVAL DATA:
  Records: 672
  Date range: 2024-01-01 08:00:00 to 2024-01-15 16:30:00
  Latest price: $2045.50
```

#### AI Trading Analysis Output:
```
================================================================================
🏆 GOLD TRADING ANALYSIS & RECOMMENDATION
================================================================================
📊 Analysis Time: 2024-01-15T10:30:15.123456
📈 Current Gold Price: $2045.50
⏱️  Data Period: 24 hours
📋 Data Points Analyzed: 96
🔄 Interval: 15m

--------------------------------------------------------------------------------
🤖 AI TRADING RECOMMENDATION:
--------------------------------------------------------------------------------

**TRADING RECOMMENDATION:**
- Position: LONG
- Confidence Level: MEDIUM
- Entry Price Target: $2043.00
- Stop Loss: $2035.00
- Take Profit: $2055.00

**REASONING:**
Gold shows bullish momentum with higher lows formation over the past 24 hours. 
Breaking above $2045 resistance with increasing volume suggests continuation. 
Technical indicators support upward movement in the short term.

**KEY FACTORS:**
- Strong support at $2040 level holding consistently
- Volume increase on recent price advances
- Dollar weakness providing tailwind for gold

**RISK ASSESSMENT:**
- Risk Level: MEDIUM
- Risk/Reward Ratio: 1:1.5
- Moderate volatility expected due to upcoming economic data releases
```

## Customization

### Price Fetching:
- Change the number of days by modifying the `days` parameter
- Use a different database path by changing the `db_path` parameter
- Add different time intervals (yfinance supports: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)

### AI Trading Analysis:
- **Custom Prompts**: Edit `trading_prompt.txt` to modify the AI analysis approach
- **Different Models**: Change the model in `trading_analyzer.py` (line 27):
  ```python
  self.model = "gpt-oss:20b"  # Change to any Ollama model
  ```
- **Analysis Parameters**: Modify time periods and intervals:
  ```python
  recommendation = analyzer.get_trading_recommendation(interval="30m", hours=48)
  ```

### Sample Prompt Customization:
Edit `trading_prompt.txt` to focus on specific trading strategies:
```
You are a [SCALPING/SWING/POSITION] trading specialist...
Focus on [TECHNICAL/FUNDAMENTAL] analysis...
Consider [RISK_LEVEL] risk tolerance...
```

## Error Handling

The script includes comprehensive error handling for:
- Network connectivity issues
- Invalid API responses
- Database errors
- Missing data scenarios

## Dependencies

### Core Dependencies:
- `yfinance>=0.2.25`: Fetching financial data from Yahoo Finance
- `pandas>=2.0.0`: Data manipulation and analysis
- `sqlite3`: Database operations (built into Python)
- `ollama>=0.1.7`: AI model integration
- `matplotlib>=3.5.0`: Optional plotting functionality

### System Requirements:
- **Ollama**: Must be installed and running locally
- **gpt-oss:20b model**: Downloaded via `ollama pull gpt-oss:20b`
- **Python 3.8+**: Required for all dependencies

## File Structure

```
gold-digger/
├── gold_fetcher.py              # Main price fetching script
├── trading_analyzer.py          # AI trading analysis engine
├── trading_prompt.txt           # Customizable AI prompt template
├── query_example.py             # Data analysis examples
├── run_complete_analysis.py     # Comprehensive analysis runner
├── configure.py                 # Configuration management utility
├── config.py                    # Configuration loading module
├── .env                         # Configuration file (create from .env.example)
├── .env.example                 # Example configuration file
├── requirements.txt             # Python dependencies
├── gold_prices.db              # SQLite database (created automatically)
└── README.md                   # This file
```

## Important Notes

### Data & API:
- Uses gold futures symbol `GC=F` from Yahoo Finance
- Data is cached with timestamps to avoid duplicate fetching
- Designed to run multiple times without wasting API calls
- Market hours and holidays may affect data availability

### AI Analysis:
- **Educational Purpose Only**: AI recommendations are for learning and research
- **Not Financial Advice**: Always do your own research and consult professionals
- **Model Limitations**: AI analysis based on historical price data only
- **Internet Required**: Ollama needs to download models initially

### Performance:
- First run downloads ~13GB for gpt-oss:20b model
- Subsequent runs are fast with cached data
- AI analysis takes 10-30 seconds depending on system specs

## Troubleshooting

### **Configuration Issues:**

1. **Setup Problems**:
   ```bash
   # Run configuration wizard
   python3 configure.py
   
   # Test current setup
   python3 configure.py --test
   
   # Reset configuration
   python3 configure.py --reset
   ```

2. **Environment Variables Not Loading**:
   ```bash
   # Check if .env file exists
   ls -la .env
   
   # Verify configuration
   python3 gold_fetcher.py --config-summary
   ```

### **Common Issues:**

1. **Ollama Connection Failed**:
   ```bash
   # Check Ollama host in .env
   echo $OLLAMA_HOST
   
   # Start Ollama service
   ollama serve
   ```

2. **Model Not Found**:
   ```bash
   # Install the model
   ollama pull gpt-oss:20b
   
   # Or install via configurator
   python3 configure.py --install-model
   ```

3. **No Market Data**:
   - Check internet connection
   - Verify market hours (gold markets closed on weekends)
   - Try different date ranges
   - Check `USE_MOCK_DATA=true` in `.env` for testing

4. **Database Locked**:
   - Close any other scripts accessing the database
   - Check file permissions in the directory
   - Verify `DATABASE_PATH` in `.env`

5. **Missing Dependencies**:
   ```bash
   # Install all dependencies
   python3 configure.py --install-deps
   
   # Or manually
   pip install -r requirements.txt
   ```