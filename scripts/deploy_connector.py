#!/usr/bin/env python3
"""
CLI script to deploy Fivetran Connector SDK connectors.

Usage:
    python scripts/deploy_connector.py --connector-dir PATH --group-id ID [--api-key KEY]
"""

import argparse
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator import PipelineOrchestrator


def main():
    """Main deployment script."""
    parser = argparse.ArgumentParser(
        description='Deploy a Fivetran Connector SDK connector'
    )
    
    parser.add_argument(
        '--connector-dir',
        required=True,
        help='Path to the connector directory containing connector.py'
    )
    
    parser.add_argument(
        '--group-id',
        required=True,
        help='Fivetran group ID (destination)'
    )
    
    parser.add_argument(
        '--api-url',
        help='Source API base URL'
    )
    
    parser.add_argument(
        '--api-key',
        help='Source API key for authentication'
    )
    
    parser.add_argument(
        '--auth-type',
        default='bearer',
        choices=['bearer', 'api_key', 'oauth2'],
        help='Authentication type (default: bearer)'
    )
    
    parser.add_argument(
        '--config-file',
        help='Path to configuration.json file (alternative to individual params)'
    )
    
    args = parser.parse_args()
    
    print("🚀 5Tran Connector Deployment Tool")
    print("=" * 60)
    
    # Validate connector directory
    connector_dir = Path(args.connector_dir)
    if not connector_dir.exists():
        print(f"❌ Error: Connector directory not found: {connector_dir}")
        return 1
    
    connector_file = connector_dir / "connector.py"
    if not connector_file.exists():
        print(f"❌ Error: connector.py not found in {connector_dir}")
        return 1
    
    # Prepare API credentials
    api_credentials = None
    
    if args.config_file:
        # Load from config file
        config_path = Path(args.config_file)
        if not config_path.exists():
            print(f"❌ Error: Config file not found: {config_path}")
            return 1
        
        with open(config_path, 'r') as f:
            api_credentials = json.load(f)
        print(f"✓ Loaded configuration from {config_path}")
    
    elif args.api_url and args.api_key:
        # Create from command-line args
        api_credentials = {
            "api_url": args.api_url,
            "api_key": args.api_key,
            "auth_type": args.auth_type
        }
        print("✓ Using API credentials from command-line arguments")
    
    else:
        # Check if configuration.json already exists
        config_file = connector_dir / "configuration.json"
        if config_file.exists():
            print(f"✓ Using existing configuration.json in connector directory")
        else:
            print("⚠️  No API credentials provided. Make sure configuration.json exists in the connector directory.")
            response = input("Continue? (y/n): ")
            if response.lower() != 'y':
                print("Deployment cancelled.")
                return 0
    
    # Deploy connector
    try:
        orchestrator = PipelineOrchestrator()
        
        result = orchestrator.deploy_connector(
            connector_dir=str(connector_dir),
            group_id=args.group_id,
            api_credentials=api_credentials
        )
        
        print("\n" + "=" * 60)
        print("✅ Deployment completed successfully!")
        print("\nNext steps:")
        print("1. Check connector status in Fivetran dashboard")
        print("2. Monitor the initial sync progress")
        print("3. Verify data arrives in your destination")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        import traceback
        print("\nFull error:")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

