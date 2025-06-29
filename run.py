#!/usr/bin/env python3
"""
ASN Analyzer Launcher
Robust entry point that avoids module import warnings
"""

import sys
from pathlib import Path

def main():
    """Main launcher function that handles imports and execution"""
    # Get the project root directory
    project_root = Path(__file__).parent.absolute()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    try:
        from src.main import cli 
        cli()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure you're running from the project root directory")
        print("Current directory:", os.getcwd())
        print("Expected directory structure:")
        print("  asn-analyzer/")
        print("  ├── run.py")
        print("  ├── src/")
        print("  │   ├── main.py")
        print("  │   └── ...")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()