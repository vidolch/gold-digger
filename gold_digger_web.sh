#!/bin/bash

# Gold Digger Web Application Launcher Script
# Simple shell script to launch the Gold Digger web-based trading terminal

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    printf "${1}${2}${NC}\n"
}

# Function to print header
print_header() {
    echo
    print_color $YELLOW "🌟============================================================🌟"
    print_color $YELLOW "    🥇 GOLD DIGGER - WEB TRADING TERMINAL 🥇"
    print_color $YELLOW "🌟============================================================🌟"
    echo
    print_color $CYAN "📊 Modern web-based interface for gold trading analysis"
    print_color $CYAN "🔄 Real-time price monitoring and news analysis"
    print_color $CYAN "🤖 AI-powered market insights and sentiment analysis"
    echo
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python installation
check_python() {
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        print_color $RED "❌ Python not found! Please install Python 3.7 or higher."
        exit 1
    fi

    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    if [ "$PYTHON_MAJOR" -lt 3 ] || [ "$PYTHON_MAJOR" -eq 3 -a "$PYTHON_MINOR" -lt 7 ]; then
        print_color $RED "❌ Python 3.7 or higher required. Found: $PYTHON_VERSION"
        exit 1
    fi

    print_color $GREEN "✅ Python $PYTHON_VERSION found"
}

# Function to check and setup virtual environment
setup_venv() {
    if [ ! -d "venv" ]; then
        print_color $YELLOW "📦 Creating virtual environment..."
        $PYTHON_CMD -m venv venv
    fi

    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_color $GREEN "✅ Virtual environment activated"
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
        print_color $GREEN "✅ Virtual environment activated (Windows)"
    else
        print_color $RED "❌ Failed to activate virtual environment"
        exit 1
    fi
}

# Function to install dependencies
install_deps() {
    print_color $YELLOW "📦 Checking dependencies..."

    if ! pip show flask >/dev/null 2>&1; then
        print_color $YELLOW "📦 Installing dependencies..."
        pip install -r requirements.txt
        print_color $GREEN "✅ Dependencies installed successfully!"
    else
        print_color $GREEN "✅ Dependencies already installed"
    fi
}

# Function to check database and data
check_data() {
    if [ ! -f "gold_prices.db" ]; then
        print_color $YELLOW "🔄 No database found. Fetching initial data..."
        $PYTHON_CMD gold_fetcher.py --quick
    fi
    print_color $GREEN "✅ Data files ready"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  --port PORT        Set port number (default: 5000)"
    echo "  --host HOST        Set host address (default: localhost)"
    echo "  --debug            Run in debug mode"
    echo "  --production       Run in production mode with Gunicorn"
    echo "  --no-browser       Don't open browser automatically"
    echo "  --setup-only       Setup environment and exit"
    echo "  --help             Show this help message"
    echo
    echo "Examples:"
    echo "  $0                 # Start with default settings"
    echo "  $0 --port 8080     # Start on port 8080"
    echo "  $0 --debug         # Start in debug mode"
    echo "  $0 --production    # Start in production mode"
}

# Function to open browser (if available and desired)
open_browser() {
    local url="http://$HOST:$PORT"

    if [ "$NO_BROWSER" != "true" ]; then
        print_color $CYAN "🌐 Opening browser to $url"

        # Try different browser commands based on OS
        if command_exists xdg-open; then
            xdg-open "$url" >/dev/null 2>&1 &
        elif command_exists open; then
            open "$url" >/dev/null 2>&1 &
        elif command_exists start; then
            start "$url" >/dev/null 2>&1 &
        else
            print_color $YELLOW "⚠️  Could not open browser automatically."
            print_color $YELLOW "   Please open your browser and go to: $url"
        fi
    fi
}

# Default values
PORT=5000
HOST="localhost"
DEBUG=false
PRODUCTION=false
NO_BROWSER=false
SETUP_ONLY=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --debug)
            DEBUG=true
            shift
            ;;
        --production)
            PRODUCTION=true
            shift
            ;;
        --no-browser)
            NO_BROWSER=true
            shift
            ;;
        --setup-only)
            SETUP_ONLY=true
            shift
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        *)
            print_color $RED "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_header

    # Check if we're in the right directory
    if [ ! -f "gold_digger_web.py" ]; then
        print_color $RED "❌ Please run this script from the gold-digger directory"
        exit 1
    fi

    # Setup environment
    check_python
    setup_venv
    install_deps
    check_data

    if [ "$SETUP_ONLY" = true ]; then
        print_color $GREEN "✅ Environment setup complete!"
        exit 0
    fi

    # Prepare launch command
    if [ "$PRODUCTION" = true ]; then
        print_color $BLUE "🚀 Starting Gold Digger Web App in PRODUCTION mode..."
        LAUNCH_CMD="$PYTHON_CMD gold_digger_web.py --production --port $PORT --host $HOST"
    elif [ "$DEBUG" = true ]; then
        print_color $BLUE "🚀 Starting Gold Digger Web App in DEBUG mode..."
        LAUNCH_CMD="$PYTHON_CMD gold_digger_web.py --debug --port $PORT --host $HOST"
    else
        print_color $BLUE "🚀 Starting Gold Digger Web App in DEVELOPMENT mode..."
        LAUNCH_CMD="$PYTHON_CMD gold_digger_web.py --port $PORT --host $HOST"
    fi

    print_color $GREEN "🌐 Dashboard will be available at: http://$HOST:$PORT"
    print_color $YELLOW "💡 Press Ctrl+C to stop the server"
    echo

    # Small delay to let user read the messages
    sleep 2

    # Open browser
    open_browser

    # Launch the application
    exec $LAUNCH_CMD
}

# Trap Ctrl+C
trap 'echo; print_color $YELLOW "👋 Gold Digger Web App stopped. Thank you for using Gold Digger!"' INT

# Run main function
main "$@"
