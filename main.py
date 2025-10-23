"""5Tran AI Pipeline Automation - Main Entry Point."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Main entry point."""
    print("🚀 5Tran AI Pipeline Automation")
    print("=" * 50)
    print()
    print("To start the Gradio UI, run:")
    print("  python src/ui/app.py")
    print()
    print("Or import and use programmatically:")
    print("  from src.orchestrator import PipelineOrchestrator")
    print()
    print("For examples, see: examples/README.md")
    print()


if __name__ == "__main__":
    main()
