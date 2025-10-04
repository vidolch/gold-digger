# 🏆 Gold Digger - Professional Gold Trading Analysis System

A comprehensive, professional-grade gold trading analysis system with real-time data fetching, sentiment analysis, AI-powered recommendations, and multiple user interfaces.

![Gold Digger Logo](https://img.shields.io/badge/Gold%20Digger-v1.0.0-gold?style=for-the-badge&logo=chart-line)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

## 🌟 Features

### 📊 **Real-Time Data Analysis**
- Live gold price fetching from Yahoo Finance
- Historical data caching with SQLite
- Multiple timeframe analysis (15m, 30m, 1h, 1d)
- Technical indicator calculations

### 📰 **News Sentiment Analysis**
- Automated news collection from multiple sources
- AI-powered sentiment analysis
- Market impact correlation
- Trending keyword extraction

### 🤖 **AI Trading Recommendations**
- Integration with Ollama for local AI processing
- Context-aware trading signals
- Risk assessment and position sizing
- Entry/exit point recommendations

### 🎯 **Multiple User Interfaces**
- **Web Interface**: Modern, responsive dashboard
- **Terminal UI (TUI)**: Rich interactive console interface
- **Command Line**: Direct terminal commands
- **API Endpoints**: RESTful API for integrations

## 🏗️ Repository Structure

```
gold-digger/
├── 📁 src/                     # Source code
│   ├── 📁 core/               # Core business logic
│   │   ├── gold_fetcher.py    # Gold price data fetching
│   │   ├── news_fetcher.py    # News data collection
│   │   ├── news_analyzer.py   # Sentiment analysis
│   │   └── trading_analyzer.py # Trading signal generation
│   ├── 📁 ui/                 # User interfaces
│   │   ├── terminal.py        # Command-line interface
│   │   ├── tui.py            # Text-based UI (Textual)
│   │   ├── tui.tcss          # TUI styling
│   │   ├── tui_launcher.py   # TUI launcher
│   │   └── news_viewer.py    # News viewing components
│   └── 📁 utils/              # Utility modules
│       ├── export_news_html.py # HTML export utilities
│       ├── query_example.py   # Database query examples
│       └── init_web_data.py   # Web data initialization
├── 📁 web/                     # Web interface
│   ├── 📁 templates/          # HTML templates
│   ├── 📁 static/             # CSS, JS, images
│   └── app.py                # Flask web application
├── 📁 config/                  # Configuration files
│   ├── config.py             # Main configuration
│   ├── configure.py          # Configuration utility
│   └── trading_prompt.txt    # AI trading prompt
├── 📁 scripts/                 # Executable scripts
│   ├── gold_digger.py        # Main CLI script
│   ├── gold_digger.sh        # Shell launcher
│   ├── gold_digger_web.py    # Web launcher
│   ├── gold_digger_web.sh    # Web shell launcher
│   └── run_complete_analysis.py # Analysis runner
├── 📁 data/                    # Data storage
│   ├── 📁 exports/           # Export outputs
│   ├── gold_prices.db        # SQLite database
│   ├── *.csv                 # Historical data files
│   └── *.html               # Generated reports
├── 📁 tests/                   # Test suite
├── 📁 docs/                    # Documentation
├── 📁 logs/                    # Application logs
├── main.py                    # Main entry point
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd gold-digger

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Configure the application
python main.py config

# Or manually create .env file
cp .env.example .env
# Edit .env with your preferences
```

### 3. Launch Application

#### 🌐 Web Interface (Recommended)
```bash
python main.py web
# Visit http://localhost:5000
```

#### 📱 Interactive TUI
```bash
python main.py tui
```

#### 🖥️ Terminal Interface
```bash
python main.py terminal
```

#### 📊 Fetch Data & Analyze
```bash
# Fetch latest data
python main.py fetch --days 14

# Run complete analysis
python main.py analyze
```

## 📋 Requirements

### System Requirements
- Python 3.8 or higher
- 2GB+ RAM
- Internet connection for data fetching

### Dependencies
- **Core**: `pandas`, `sqlite3`, `requests`, `yfinance`
- **AI**: `ollama` (for local AI processing)
- **Web**: `flask`, `flask-cors`, `plotly`
- **TUI**: `textual`, `rich`
- **Analysis**: `scikit-learn`, `numpy`

### Optional: Ollama Setup
For AI-powered recommendations:
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull recommended model
ollama pull gpt-oss:20b
# or smaller model: ollama pull phi3.5
```

## 🎯 Usage Examples

### Web Interface Features
- **Dashboard**: Real-time price charts and market overview
- **Sentiment Analysis**: News sentiment tracking with visual indicators
- **AI Recommendations**: Context-aware trading signals
- **Historical Data**: Interactive charts and data analysis

### API Endpoints
```bash
# Get current gold price
curl http://localhost:5000/api/current-price

# Get sentiment analysis
curl http://localhost:5000/api/news/analyze

# Get trading recommendation
curl http://localhost:5000/api/complete-analysis
```

### Command Line Usage
```bash
# Fetch and analyze gold data
python scripts/gold_digger.py --fetch --analyze

# Export data to CSV
python src/utils/export_news_html.py --format csv

# Run custom queries
python src/utils/query_example.py --interval 15m
```

## 🔧 Configuration

### Environment Variables
Key configuration options (see `config/config.py` for full list):

```env
# Database
DATABASE_PATH=data/gold_prices.db

# Ollama AI
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gpt-oss:20b

# Data Fetching
DEFAULT_FETCH_DAYS=14
GOLD_SYMBOL=GC=F

# Web Interface
PORT=5000
FLASK_ENV=development
```

### Trading Parameters
Customize trading analysis in `config/trading_prompt.txt`:
- Risk tolerance levels
- Position sizing rules
- Technical indicator preferences
- Market condition filters

## 📊 Data Sources

- **Gold Prices**: Yahoo Finance (GC=F futures)
- **News Data**: Multiple financial news sources
- **Market Data**: Real-time and historical OHLCV data
- **Economic Indicators**: Integration-ready structure

## 🧠 AI Integration

Gold Digger uses local AI processing via Ollama:
- **Privacy-First**: All AI processing runs locally
- **Customizable**: Use any Ollama-compatible model
- **Context-Aware**: AI considers market conditions, news, and technical data
- **Real-Time**: Generate fresh recommendations on demand

## 🔐 Security & Privacy

- **Local Processing**: No data sent to external AI services
- **Secure Database**: SQLite with proper permissions
- **API Security**: Built-in rate limiting and validation
- **Configuration**: Secure environment variable handling

## 📈 Performance

- **Efficient Caching**: Smart database caching reduces API calls
- **Async Processing**: Non-blocking data fetching
- **Memory Optimized**: Handles large datasets efficiently
- **Scalable**: Modular design supports easy extensions

## 🧪 Testing

```bash
# Run test suite
python -m pytest tests/

# Run specific tests
python tests/test_tui.py
python tests/test_layout.py

# Test web interface
python -m unittest web.test_app
```

## 📚 Documentation

Detailed documentation available in `/docs/`:
- `TERMINAL_GUIDE.md` - Command-line usage
- `TUI_GUIDE.md` - Text UI instructions
- `WEB_GUIDE.md` - Web interface guide
- `API_REFERENCE.md` - API documentation

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit install

# Run linting
flake8 src/
black src/

# Run type checking
mypy src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support & Troubleshooting

### Common Issues

**Port 5000 in use (macOS)**
```bash
# Disable AirPlay Receiver in System Preferences
# Or use different port:
python main.py web --port 8080
```

**Ollama connection issues**
```bash
# Check Ollama status
ollama list
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

**Database errors**
```bash
# Reset database
rm data/gold_prices.db
python main.py fetch --days 7
```

### Getting Help

- 📧 Email: support@golddigger.dev
- 💬 Discord: [Gold Digger Community](https://discord.gg/golddigger)
- 🐛 Issues: [GitHub Issues](https://github.com/golddigger/issues)
- 📖 Wiki: [Documentation Wiki](https://github.com/golddigger/wiki)

## 🏆 Acknowledgments

- Yahoo Finance for reliable market data
- Ollama team for local AI infrastructure
- Textual framework for beautiful TUI components
- Flask ecosystem for robust web framework
- Open source community for inspiration and libraries

---

<div align="center">

**Built with ❤️ for traders who demand better tools**

[🌟 Star this repo](https://github.com/golddigger/stargazers) • [🐛 Report Bug](https://github.com/golddigger/issues) • [💡 Request Feature](https://github.com/golddigger/issues)

</div>