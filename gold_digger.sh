#!/bin/bash

# Gold Digger Terminal Launcher
# A simple wrapper script for the Gold Digger unified terminal application

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}"
    echo "=================================="
    echo "🏆 Gold Digger Terminal Launcher"
    echo "=================================="
    echo -e "${NC}"
}

# Check if we're in the right directory
if [ ! -f "gold_digger_terminal.py" ]; then
    print_error "gold_digger_terminal.py not found!"
    print_error "Please run this script from the gold-digger directory"
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed or not in PATH"
    exit 1
fi

print_header

# Check if virtual environment exists
if [ -d "venv" ]; then
    print_status "Activating virtual environment..."
    source venv/bin/activate
fi

# Check for basic dependencies
print_status "Checking dependencies..."
python3 -c "import yfinance, pandas, ollama" 2>/dev/null
if [ $? -ne 0 ]; then
    print_warning "Some dependencies might be missing"
    print_status "You can install them by running option 22 in the terminal"
fi

# Parse command line arguments
case "$1" in
    --test)
        print_status "Running system test..."
        python3 gold_digger_terminal.py --test
        ;;
    --config)
        print_status "Showing configuration..."
        python3 gold_digger_terminal.py --config
        ;;
    --quick)
        print_status "Running quick analysis..."
        python3 gold_digger_terminal.py --quick-analysis
        ;;
    --setup)
        print_status "Running setup wizard..."
        python3 configure.py --quick
        ;;
    --tui)
        print_status "Starting Gold Digger TUI (modern interface)..."
        python3 gold_digger_tui.py
        ;;
    --help|-h)
        echo "Gold Digger Terminal Launcher"
        echo ""
        echo "Usage: $0 [OPTION]"
        echo ""
        echo "Options:"
        echo "  --test      Test system setup"
        echo "  --config    Show configuration"
        echo "  --quick     Run quick analysis"
        echo "  --setup     Run setup wizard"
        echo "  --tui       Launch modern TUI interface"
        echo "  --help      Show this help"
        echo ""
        echo "Run without arguments to start interactive terminal"
        ;;
    *)
        print_status "Starting Gold Digger Terminal..."
        print_status "💡 Try --tui for the modern interface!"
        python3 gold_digger_terminal.py
        ;;
esac

# Check exit status
if [ $? -eq 0 ]; then
    print_status "Gold Digger Terminal completed successfully"
else
    print_error "Gold Digger Terminal exited with error"
    exit 1
fi
