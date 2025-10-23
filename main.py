"""5Tran AI Pipeline Automation - Main Entry Point."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.cli.main import main as cli_main


def main():
    """Main entry point - launches CLI."""
    cli_main()


if __name__ == "__main__":
    main()
