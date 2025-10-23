#!/usr/bin/env python3
"""
Quick helper to get Fivetran group ID for UI.

Usage:
    python scripts/get_group_id.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.connectors.fivetran_manager import FivetranManager


def main():
    """Get first group ID."""
    try:
        manager = FivetranManager()
        groups = manager.list_groups()
        
        if not groups:
            print("No groups found. Create one first:")
            print("  python scripts/create_fivetran_group.py --name 'My Group'")
            return 1
        
        # Print first group ID (most common use case)
        print(groups[0]['id'])
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

