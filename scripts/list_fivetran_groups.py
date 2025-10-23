#!/usr/bin/env python3
"""
CLI script to list Fivetran groups (destinations).

Usage:
    python scripts/list_fivetran_groups.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.connectors.fivetran_manager import FivetranManager


def main():
    """List all Fivetran groups."""
    print("🔍 Fetching Fivetran Groups")
    print("=" * 60)
    
    try:
        manager = FivetranManager()
        groups = manager.list_groups()
        
        if not groups:
            print("\nNo groups found.")
            print("\nTo create a group, use:")
            print("  python scripts/create_fivetran_group.py --name 'My Group'")
            return 0
        
        print(f"\nFound {len(groups)} group(s):\n")
        
        for i, group in enumerate(groups, 1):
            print(f"{i}. {group['name']}")
            print(f"   ID: {group['id']}")
            print(f"   Created: {group.get('created_at', 'N/A')}")
            print()
        
        print("=" * 60)
        print("\nTo deploy a connector to a group, use:")
        print("  python scripts/deploy_connector.py --connector-dir PATH --group-id GROUP_ID")
        
        return 0
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nMake sure you have set the following in your .env file:")
        print("  - FIVETRAN_API_KEY")
        print("  - FIVETRAN_API_SECRET")
        return 1
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

