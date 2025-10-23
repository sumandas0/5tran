#!/usr/bin/env python3
"""
CLI script to create a new Fivetran group.

Usage:
    python scripts/create_fivetran_group.py --name "My Group"
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.connectors.fivetran_manager import FivetranManager


def main():
    """Create a new Fivetran group."""
    parser = argparse.ArgumentParser(
        description='Create a new Fivetran group (destination)'
    )
    
    parser.add_argument(
        '--name',
        required=True,
        help='Name for the new group'
    )
    
    args = parser.parse_args()
    
    print("➕ Creating Fivetran Group")
    print("=" * 60)
    
    try:
        manager = FivetranManager()
        group = manager.create_group(args.name)
        
        print("\n✅ Group created successfully!")
        print(f"\nGroup Details:")
        print(f"  Name: {group['name']}")
        print(f"  ID: {group['id']}")
        print(f"  Created: {group.get('created_at', 'N/A')}")
        
        print("\n" + "=" * 60)
        print("Next steps:")
        print("1. Configure a destination in the Fivetran dashboard")
        print("2. Use this group ID to deploy connectors:")
        print(f"   python scripts/deploy_connector.py --connector-dir PATH --group-id {group['id']}")
        
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

