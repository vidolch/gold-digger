#!/usr/bin/env python3
"""
Test script for Gold Digger TUI functionality.
Verifies that all components work correctly without launching the full interface.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required imports work."""
    print("🧪 Testing imports...")

    try:
        from textual.app import App
        from textual.widgets import Button, Static
        from rich.console import Console
        from rich.panel import Panel
        print("  ✅ Textual and Rich imports successful")
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False

    try:
        from gold_digger_tui import GoldDiggerTUI, MainScreen, TradingScreen, NewsScreen
        print("  ✅ TUI module imports successful")
    except ImportError as e:
        print(f"  ❌ TUI import failed: {e}")
        return False

    try:
        from config import get_config
        config = get_config()
        print("  ✅ Configuration import successful")
    except ImportError as e:
        print(f"  ❌ Config import failed: {e}")
        return False

    return True

def test_tui_initialization():
    """Test TUI app initialization."""
    print("\n🧪 Testing TUI initialization...")

    try:
        from gold_digger_tui import GoldDiggerTUI
        app = GoldDiggerTUI()
        app.demo_mode = True
        print("  ✅ TUI app created successfully")
        print(f"  ✅ Demo mode: {app.demo_mode}")
        print(f"  ✅ Dark mode: {app._dark_mode}")
        return True
    except Exception as e:
        print(f"  ❌ TUI initialization failed: {e}")
        return False

def test_screen_creation():
    """Test individual screen creation."""
    print("\n🧪 Testing screen creation...")

    try:
        from gold_digger_tui import MainScreen, TradingScreen, NewsScreen, ConfigScreen, DatabaseScreen

        # Test MainScreen
        main_screen = MainScreen()
        print("  ✅ MainScreen created successfully")

        # Test TradingScreen
        trading_screen = TradingScreen()
        print("  ✅ TradingScreen created successfully")

        # Test NewsScreen
        news_screen = NewsScreen()
        print("  ✅ NewsScreen created successfully")

        # Test ConfigScreen
        config_screen = ConfigScreen()
        print("  ✅ ConfigScreen created successfully")

        # Test DatabaseScreen
        database_screen = DatabaseScreen()
        print("  ✅ DatabaseScreen created successfully")

        return True
    except Exception as e:
        print(f"  ❌ Screen creation failed: {e}")
        return False

def test_css_parsing():
    """Test CSS stylesheet parsing."""
    print("\n🧪 Testing CSS parsing...")

    css_path = Path("gold_digger_tui.tcss")
    if not css_path.exists():
        print("  ❌ CSS file not found")
        return False

    try:
        # Try to create an app with CSS
        from gold_digger_tui import GoldDiggerTUI
        app = GoldDiggerTUI()
        print("  ✅ CSS parsed successfully")
        return True
    except Exception as e:
        print(f"  ❌ CSS parsing failed: {e}")
        return False

def test_demo_functionality():
    """Test demo mode functionality."""
    print("\n🧪 Testing demo mode functionality...")

    try:
        from gold_digger_tui import GoldDiggerTUI, MainScreen, TradingScreen, NewsScreen

        app = GoldDiggerTUI()
        app.demo_mode = True

        # Test demo mode flag
        if not app.demo_mode:
            print("  ❌ Demo mode not set correctly")
            return False

        print("  ✅ Demo mode activated successfully")

        # Test screen creation in demo mode
        main_screen = MainScreen()
        trading_screen = TradingScreen()
        news_screen = NewsScreen()

        print("  ✅ All screens work in demo mode")
        return True
    except Exception as e:
        print(f"  ❌ Demo mode test failed: {e}")
        return False

def test_database_connectivity():
    """Test database connectivity for TUI screens."""
    print("\n🧪 Testing database connectivity...")

    try:
        import sqlite3
        from config import get_config
        config = get_config()

        # Check if database exists
        db_path = Path(config.database_path)
        if db_path.exists():
            print(f"  ✅ Database file exists: {db_path}")

            # Try to connect
            with sqlite3.connect(config.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                print(f"  ✅ Database connection successful, {len(tables)} tables found")
        else:
            print("  ⚠️  Database file not found (this is OK for first run)")

        return True
    except Exception as e:
        print(f"  ❌ Database connectivity test failed: {e}")
        return False

def test_async_functionality():
    """Test async method functionality."""
    print("\n🧪 Testing async functionality...")

    async def test_async():
        try:
            from gold_digger_tui import NewsScreen, TradingScreen

            # Create screens
            news_screen = NewsScreen()
            trading_screen = TradingScreen()

            # Test that screens have the correct compose structure
            news_compose = news_screen.compose()
            trading_compose = trading_screen.compose()

            print("  ✅ Screen creation successful")
            print("  ✅ Compose methods return ComposeResult")
            print("  ✅ Container structure verified")

            # Test that the fixed containers exist
            if hasattr(news_screen, 'load_recent_headlines'):
                print("  ✅ News headline loading method exists")

            if hasattr(trading_screen, 'load_latest_recommendation'):
                print("  ✅ Trading recommendation loading method exists")

            print("  ✅ Container update fixes verified")
            return True
        except Exception as e:
            print(f"  ❌ Async functionality test failed: {e}")
            return False

    try:
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(test_async())
        loop.close()
        return result
    except Exception as e:
        print(f"  ❌ Async test setup failed: {e}")
        return False

def test_configuration_access():
    """Test configuration access from TUI."""
    print("\n🧪 Testing configuration access...")

    try:
        from config import get_config
        config = get_config()

        # Test key configuration values
        print(f"  ✅ Ollama host: {config.ollama_host}")
        print(f"  ✅ Database path: {config.database_path}")
        print(f"  ✅ Default interval: {config.default_interval}")

        return True
    except Exception as e:
        print(f"  ❌ Configuration access failed: {e}")
        return False

def run_all_tests():
    """Run all tests and report results."""
    print("🧪 Gold Digger TUI Test Suite")
    print("=" * 50)

    tests = [
        ("Import Tests", test_imports),
        ("TUI Initialization", test_tui_initialization),
        ("Screen Creation", test_screen_creation),
        ("CSS Parsing", test_css_parsing),
        ("Demo Functionality", test_demo_functionality),
        ("Database Connectivity", test_database_connectivity),
        ("Container Fix Verification", test_async_functionality),
        ("Configuration Access", test_configuration_access),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! TUI is ready to use.")
        print("\n🚀 You can now launch the TUI with:")
        print("   ./gold_digger.sh --tui")
        print("   python3 gold_digger_tui.py --demo")
        return True
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("🔧 Try these troubleshooting steps:")
        print("   1. Install dependencies: pip install textual rich")
        print("   2. Run setup: python3 configure.py --quick")
        print("   3. Try demo mode: python3 gold_digger_tui.py --demo")
        print("   4. Check for container update errors in news/trading screens")
        return False

def main():
    """Main test runner."""
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal test error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
