#!/usr/bin/env python3
"""
Gold Digger Web Application Launcher
Simple launcher script for the Gold Digger web-based trading terminal.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import flask
        import pandas
        import yfinance
        import plotly
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def setup_environment():
    """Setup the environment for the web application."""
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))

    # Set Flask environment variables if not already set
    if 'FLASK_ENV' not in os.environ:
        os.environ['FLASK_ENV'] = 'development'

    # Set default port if not specified
    if 'PORT' not in os.environ:
        os.environ['PORT'] = '5000'

def initialize_data():
    """Initialize application data."""
    try:
        # Import and run initialization
        from init_web_data import main as init_main
        result = init_main()
        return result == 0
    except Exception as e:
        print(f"❌ Error initializing data: {e}")
        return False

def print_welcome():
    """Print welcome message and instructions."""
    print("🌟" + "="*60 + "🌟")
    print("    🥇 GOLD DIGGER - WEB TRADING TERMINAL 🥇")
    print("🌟" + "="*60 + "🌟")
    print()
    print("📊 Modern web-based interface for gold trading analysis")
    print("🔄 Real-time price monitoring and news analysis")
    print("🤖 AI-powered market insights and sentiment analysis")
    print()

def main():
    parser = argparse.ArgumentParser(description='Gold Digger Web Application')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--production', action='store_true', help='Run in production mode with Gunicorn')
    parser.add_argument('--check-deps', action='store_true', help='Check dependencies and exit')

    args = parser.parse_args()

    # Check dependencies
    if not check_dependencies():
        if args.check_deps:
            sys.exit(1)
        print("\nWould you like to install dependencies now? (y/n): ", end='')
        if input().lower().startswith('y'):
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
                print("✅ Dependencies installed successfully!")
            except subprocess.CalledProcessError:
                print("❌ Failed to install dependencies")
                sys.exit(1)
        else:
            sys.exit(1)

    if args.check_deps:
        print("✅ All dependencies are installed!")
        sys.exit(0)

    # Setup environment
    setup_environment()

    # Initialize data if needed
    if not initialize_data():
        print("❌ Failed to initialize application data")
        if not input("Continue anyway? (y/n): ").lower().startswith('y'):
            sys.exit(1)

    # Set port
    os.environ['PORT'] = str(args.port)

    # Print welcome message
    print_welcome()

    try:
        if args.production:
            # Production mode with Gunicorn
            print(f"🚀 Starting Gold Digger Web App in PRODUCTION mode...")
            print(f"🌐 Server will be available at: http://{args.host}:{args.port}")
            print("💡 Press Ctrl+C to stop the server")
            print()

            # Import and check if gunicorn is available
            try:
                import gunicorn
            except ImportError:
                print("❌ Gunicorn not found. Installing...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'gunicorn'])

            # Run with gunicorn
            cmd = [
                'gunicorn',
                '--bind', f'{args.host}:{args.port}',
                '--workers', '4',
                '--timeout', '120',
                '--access-logfile', '-',
                '--error-logfile', '-',
                'web.app:app'
            ]
            subprocess.run(cmd)

        else:
            # Development mode
            if args.debug:
                os.environ['FLASK_ENV'] = 'development'
                print(f"🚀 Starting Gold Digger Web App in DEBUG mode...")
            else:
                print(f"🚀 Starting Gold Digger Web App in DEVELOPMENT mode...")

            print(f"🌐 Dashboard will be available at: http://{args.host}:{args.port}")
            print("💡 Press Ctrl+C to stop the server")
            print()

            # Import the Flask app
            from web.app import app

            # Run the Flask app
            app.run(
                host=args.host,
                port=args.port,
                debug=args.debug,
                use_reloader=False  # Disable reloader to avoid double startup
            )

    except KeyboardInterrupt:
        print("\n👋 Gold Digger Web App stopped.")
        print("Thank you for using Gold Digger!")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the Gold Digger directory")
        print("and all dependencies are installed.")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Error starting web application: {e}")
        print("Please check your configuration and try again.")
        sys.exit(1)

if __name__ == '__main__':
    main()
