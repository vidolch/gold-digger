#!/usr/bin/env python3
"""
Gold Digger TUI Launcher
A dedicated launcher for the modern TUI interface with dependency checking.
"""

import sys
import os
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required TUI dependencies are installed."""
    missing_deps = []

    # Check in current Python environment
    try:
        import textual
    except ImportError:
        missing_deps.append('textual')

    try:
        import rich
    except ImportError:
        missing_deps.append('rich')

    # If we're in a virtual environment, dependencies might be available there
    if Path("venv").exists() and missing_deps:
        # Try checking in virtual environment
        venv_python = Path("venv/bin/python3")
        if venv_python.exists():
            try:
                import subprocess
                result = subprocess.run([
                    str(venv_python), '-c',
                    'import textual, rich; print("ok")'
                ], capture_output=True, text=True)
                if result.returncode == 0 and "ok" in result.stdout:
                    # Dependencies are available in venv
                    return []
            except:
                pass

    return missing_deps

def install_dependencies(deps):
    """Install missing dependencies."""
    print("🔧 Installing missing dependencies...")
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install'
        ] + deps)
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies automatically")
        print(f"Please install manually: pip install {' '.join(deps)}")
        return False

def main():
    """Main launcher function."""
    print("🏆 Gold Digger TUI Launcher")
    print("=" * 40)

    # Check if we're in the right directory
    if not Path("gold_digger_tui.py").exists():
        print("❌ gold_digger_tui.py not found!")
        print("Please run this script from the gold-digger directory")
        sys.exit(1)

    # Activate virtual environment first if available
    if Path("venv").exists():
        print("🔄 Virtual environment detected...")
        venv_python = Path("venv/bin/python3")
        if venv_python.exists():
            print("🚀 Launching TUI with virtual environment...")
            try:
                os.execv(str(venv_python), [str(venv_python), "gold_digger_tui.py"] + sys.argv[1:])
            except Exception as e:
                print(f"❌ Error with virtual environment: {e}")
                print("Falling back to system Python...")

    # Check dependencies
    missing_deps = check_dependencies()
    if missing_deps:
        print(f"⚠️  Missing dependencies: {', '.join(missing_deps)}")
        print("Installing dependencies automatically...")

        try:
            if not install_dependencies(missing_deps):
                print("❌ Failed to install dependencies")
                print("\nManual installation:")
                print(f"  pip install {' '.join(missing_deps)}")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Installation error: {e}")
            print("\nManual installation:")
            print(f"  pip install {' '.join(missing_deps)}")
            sys.exit(1)

    # Launch TUI
    print("🚀 Launching Gold Digger TUI...")
    try:
        from gold_digger_tui import main as tui_main
        tui_main()
    except KeyboardInterrupt:
        print("\n👋 TUI terminated by user")
    except Exception as e:
        print(f"❌ Error launching TUI: {e}")
        print("\nTry running the basic terminal instead:")
        print("  python3 gold_digger_terminal.py")
        print("\nOr try with virtual environment:")
        print("  source venv/bin/activate && python3 gold_digger_tui.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
