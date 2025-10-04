# Gold Digger TUI - Complete User Guide

## 🎨 Modern Text User Interface

The Gold Digger TUI provides a beautiful, interactive terminal interface for all Gold Digger functionality. Built with Textual and Rich, it offers a modern, responsive experience with real-time updates, interactive panels, and intuitive navigation.

## 🚀 Quick Start

### Launch Options

```bash
# Recommended: Shell wrapper with auto-setup
./gold_digger.sh --tui

# Direct Python execution
python3 gold_digger_tui.py

# Demo mode with sample data (great for testing)
python3 gold_digger_tui.py --demo

# Launcher with dependency checking
python3 gold_digger_tui_launcher.py
```

### First Time Setup

1. **Install Dependencies**: The TUI requires `textual` and `rich`
   ```bash
   pip install textual rich
   ```

2. **Launch in Demo Mode**: Test the interface first
   ```bash
   python3 gold_digger_tui.py --demo
   ```

3. **Full Setup**: Run the setup wizard
   ```bash
   ./gold_digger.sh --setup
   ```

## 📱 Interface Overview

### Main Dashboard

The main screen provides:
- 📊 **System Status Panel**: Real-time database and API status
- ⚡ **Quick Actions**: One-click access to common operations
- 🎛️ **Module Access**: Navigate to specialized screens
- 💾 **Live Data**: Current gold price and system health

### Screen Navigation

#### 🏠 Main Dashboard
- System overview and quick actions
- Status monitoring
- Direct access to all modules

#### 🤖 Trading Analysis Screen
- AI-powered trading recommendations
- Real-time analysis execution
- Historical recommendation tracking
- Progress indicators for long-running analyses

#### 📰 News & Sentiment Screen
- Live news headline browsing
- Sentiment analysis visualization
- Interactive article search
- Category-based filtering
- Publisher analysis

#### 💾 Database Screen
- Tabbed interface for different data types
- Price data statistics (15m/30m intervals)
- News article metrics
- Analysis history
- Data export options

#### ⚙️ Configuration Screen
- System settings overview
- Real-time configuration editing
- Validation and error checking
- Reset to defaults option

## ⌨️ Keyboard Shortcuts

### Global Shortcuts (Work Everywhere)
```
Q           - Quit application
ESC         - Go back to previous screen
D           - Toggle dark/light mode
H           - Show help information
Ctrl+R      - Refresh current screen
Tab         - Navigate forward between elements
Shift+Tab   - Navigate backward between elements
Enter       - Activate focused element
```

### Context-Specific Shortcuts
```
F           - Fetch data (context dependent)
A           - Run analysis (on analysis screens)
S           - Search/Save (context dependent)
R           - Refresh data (context dependent)
C           - Clear/Reset (context dependent)
```

### Navigation Shortcuts
```
↑↓          - Scroll up/down in lists
←→          - Navigate between tabs/panels
Page Up/Dn  - Quick scroll in long content
Home/End    - Jump to beginning/end
```

## 🎛️ Screen Details

### Main Dashboard Features

**Status Panel:**
- Database connection status
- AI model availability
- Latest gold price
- System health indicators

**Quick Actions:**
- ⚡ **Quick Analysis**: 24-hour analysis with news
- 📊 **Full Analysis**: Comprehensive multi-day analysis
- 📰 **Latest News**: Fetch and browse recent articles
- ⚙️ **Configuration**: Access system settings

**Module Buttons:**
- 💰 **Price Data**: Price fetching and analysis tools
- 📈 **Trading Analysis**: AI recommendations and insights
- 📰 **News & Sentiment**: News management and analysis
- 💾 **Database**: Data exploration and statistics

### Trading Analysis Screen

**Analysis Types:**
- ⚡ **Quick Analysis**: Fast 24-hour analysis
- 📊 **Full Analysis**: Comprehensive multi-day analysis
- 📈 **Price Only**: Technical analysis without news
- 📰 **News Only**: Sentiment-driven analysis

**Real-time Features:**
- Progress bars for running analyses
- Live recommendation updates
- Analysis history tracking
- Success rate monitoring

**Recommendation Display:**
```
🎯 LONG POSITION RECOMMENDED
💰 Current Price: $2,045.50
📈 Entry Target: $2,043.00
🛑 Stop Loss: $2,035.00
🎯 Take Profit: $2,055.00
🔒 Confidence: HIGH (85%)
```

### News & Sentiment Screen

**Headline Browser:**
- Recent articles with sentiment indicators
- Publisher and date information
- Expandable article details
- Sentiment score visualization

**Interactive Features:**
- 🔄 **Fetch News**: Load latest articles
- 🔍 **Search**: Find articles by keyword
- 📈 **Sentiment**: Analyze sentiment trends
- 📂 **Categories**: Browse by article category

**Sentiment Indicators:**
- 😊 Positive sentiment (> 0.1)
- 😐 Neutral sentiment (-0.1 to 0.1)
- 😟 Negative sentiment (< -0.1)

### Database Screen

**Tabbed Interface:**
- **Price Data Tab**: 15m and 30m interval statistics
- **News Data Tab**: Article counts and sentiment metrics
- **Analysis Tab**: Trading recommendation history

**Statistics Display:**
- Record counts and date ranges
- Average sentiment scores
- Category breakdowns
- Publisher analysis

### Configuration Screen

**Settings Categories:**
- 🤖 **Ollama Configuration**: AI model settings
- 💾 **Database Settings**: File paths and connections
- 📊 **Analysis Parameters**: Default intervals and timeframes
- 📰 **News Configuration**: Sources and limits
- 🔧 **System Settings**: Debug mode, logging, etc.

**Interactive Elements:**
- Real-time validation
- Save/Reset buttons
- Configuration export/import

## 🎨 Themes and Styling

### Dark Mode (Default)
- High contrast for eye comfort
- Professional terminal appearance
- Optimized for extended use

### Light Mode
- Clean, modern appearance
- Better for bright environments
- Toggle with `D` key

### Visual Elements
- 🎯 **Status Indicators**: Color-coded system health
- 📊 **Progress Bars**: Real-time operation tracking
- 🎨 **Syntax Highlighting**: Code and data display
- 📋 **Tables**: Structured data presentation
- 🎪 **Panels**: Organized content sections

## 🔧 Advanced Features

### Demo Mode
Perfect for testing and demonstrations:
```bash
python3 gold_digger_tui.py --demo
```
- Sample data for all screens
- No external API calls
- Simulated analysis results
- Safe for presentations

### Mouse Support
- Click buttons and interactive elements
- Scroll through content
- Select text and data
- Hover tooltips (where available)

### Responsive Design
- Adapts to different terminal sizes
- Compact mode for smaller screens
- Optimal layout for various resolutions
- Mobile terminal support

### Real-time Updates
- Live status monitoring
- Dynamic data refresh
- Progress tracking
- Instant notifications

## 🚨 Troubleshooting

### Common Issues

**TUI Won't Start:**
```bash
# Check dependencies
pip install textual rich

# Try demo mode
python3 gold_digger_tui.py --demo

# Use launcher with auto-install
python3 gold_digger_tui_launcher.py
```

**CSS/Styling Errors:**
- Ensure Textual version is 0.45.0+
- Check terminal compatibility
- Try different terminal emulators

**Performance Issues:**
- Reduce data fetch amounts in settings
- Use demo mode for testing
- Check terminal buffer size

**Database Errors:**
- Verify database file permissions
- Run database initialization
- Check SQLite installation

### Terminal Compatibility

**Recommended Terminals:**
- ✅ iTerm2 (macOS)
- ✅ Windows Terminal
- ✅ GNOME Terminal (Linux)
- ✅ Konsole (KDE)
- ✅ Alacritty
- ✅ Kitty

**Features by Terminal:**
- **Mouse Support**: Most modern terminals
- **True Color**: iTerm2, Windows Terminal, Alacritty
- **Unicode**: All recommended terminals
- **Resize Handling**: All modern terminals

## 💡 Tips and Best Practices

### Efficient Workflow

1. **Start with Dashboard**: Get system overview
2. **Use Quick Analysis**: For daily trading insights
3. **Browse News First**: Understand market sentiment
4. **Check Database Stats**: Monitor data health
5. **Configure Once**: Set up preferences early

### Keyboard Efficiency

- Learn global shortcuts (`Q`, `ESC`, `D`, `H`)
- Use Tab navigation for speed
- Leverage context shortcuts (`F`, `A`, `S`)
- Remember ESC always goes back

### Data Management

- Regular news fetching for current sentiment
- Monitor database size and health
- Export data for backup
- Use demo mode for testing changes

### Analysis Best Practices

- Run quick analysis daily
- Use full analysis for important decisions
- Compare with news sentiment
- Track recommendation success rates

## 🔄 Updates and Maintenance

### Keeping Current
```bash
# Update dependencies
pip install --upgrade textual rich

# Pull latest code
git pull origin main

# Test with demo mode
python3 gold_digger_tui.py --demo
```

### Performance Optimization
- Regular database maintenance
- Monitor memory usage
- Optimize fetch intervals
- Clean old data periodically

## 📞 Support

### Getting Help

1. **Built-in Help**: Press `H` in any screen
2. **Demo Mode**: Test functionality safely
3. **Terminal Logs**: Check console output
4. **Configuration**: Verify settings

### Reporting Issues

Include this information:
- Operating system and terminal
- Python and package versions
- Error messages and logs
- Steps to reproduce

### Fallback Options

If TUI issues persist:
```bash
# Use classic terminal interface
./gold_digger.sh

# Direct script execution
python3 gold_digger_terminal.py

# Individual scripts
python3 gold_fetcher.py --analyze
```

---

🏆 **Gold Digger TUI** - Where modern terminal interfaces meet professional trading analysis.

*Experience the future of terminal applications with Gold Digger's beautiful, interactive TUI interface.*