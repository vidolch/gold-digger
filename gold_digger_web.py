#!/usr/bin/env python3
"""
Gold Digger Web Application Launcher
Simple launcher script for the Gold Digger web-based trading terminal.

This script provides a convenient way to launch the web interface with
various configuration options while handling the new organized structure.
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
    # Get project root directory
    project_root = Path(__file__).parent

    # Add src directory to Python path for imports
    src_dir = project_root / 'src'
    config_dir = project_root / 'config'

    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    if str(config_dir) not in sys.path:
        sys.path.insert(0, str(config_dir))
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

def launch_web_app(port=5000, host='localhost', debug=False, production=False):
    """Launch the Gold Digger web application."""

    print("🚀 Gold Digger Web Application")
    print("=" * 40)

    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)

    # Setup environment
    setup_environment()

    # Set environment variables
    os.environ['PORT'] = str(port)
    os.environ['HOST'] = host

    if production:
        os.environ['FLASK_ENV'] = 'production'
        print(f"🌐 Starting in PRODUCTION mode on http://{host}:{port}")
    elif debug:
        os.environ['FLASK_ENV'] = 'development'
        print(f"🔧 Starting in DEBUG mode on http://{host}:{port}")
    else:
        os.environ['FLASK_ENV'] = 'development'
        print(f"🌐 Starting in DEVELOPMENT mode on http://{host}:{port}")

    try:
        # Import and run the web app from the web directory
        web_dir = Path(__file__).parent / 'web'
        sys.path.insert(0, str(web_dir))

        # Change to web directory
        os.chdir(web_dir)

        # Import and run the web app
        from app import main as web_main
        web_main()

    except ImportError as e:
        print(f"❌ Error importing web application: {e}")
        print("Make sure you're running from the gold-digger directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting web application: {e}")
        sys.exit(1)

def main():
    """Main entry point with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description='Gold Digger Web Application Launcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gold_digger_web.py                    # Start with defaults
  python gold_digger_web.py --port 8080        # Custom port
  python gold_digger_web.py --debug            # Debug mode
  python gold_digger_web.py --production       # Production mode
  python gold_digger_web.py --host 0.0.0.0     # Allow external access
        """
    )

    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port number for the web server (default: 5000)'
    )

    parser.add_argument(
        '--host',
        type=str,
        default='localhost',
        help='Host address for the web server (default: localhost)'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Run in debug mode with auto-reload'
    )

    parser.add_argument(
        '--production',
        action='store_true',
        help='Run in production mode'
    )

    args = parser.parse_args()

    # Launch the web application
    try:
        launch_web_app(
            port=args.port,
            host=args.host,
            debug=args.debug,
            production=args.production
        )
    except KeyboardInterrupt:
        print("\n👋 Gold Digger Web App stopped. Thank you for using Gold Digger!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
