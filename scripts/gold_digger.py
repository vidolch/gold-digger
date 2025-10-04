#!/usr/bin/env python3
"""
Gold Digger - Simple Launcher Script
Quick access to the Gold Digger Terminal application.
"""

import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from gold_digger_terminal import main
except ImportError as e:
    print("❌ Error importing Gold Digger Terminal:")
    print(f"   {e}")
    print("\nPlease ensure you are in the correct directory and all dependencies are installed.")
    print("Run: python3 configure.py --quick")
    sys.exit(1)

if __name__ == "__main__":
    main()
