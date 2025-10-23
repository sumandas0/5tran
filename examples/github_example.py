#!/usr/bin/env python3
"""
GitHub API Pipeline Example

This example shows how to create a data pipeline for GitHub repositories,
issues, pull requests, and commits using a real GitHub Personal Access Token.

Prerequisites:
1. GitHub Personal Access Token
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: repo, read:user
   - Copy the token

2. Environment setup:
   - FIVETRAN_API_KEY and FIVETRAN_API_SECRET in .env
   - GEMINI_API_KEY in .env
   - GCP_PROJECT_ID (for BigQuery)

Usage:
    python examples/github_example.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator import PipelineOrchestrator
from src.connectors.fivetran_manager import FivetranManager


def main():
    """Run GitHub API pipeline example."""
    
    print("=" * 80)
    print("🚀 GitHub API Data Pipeline Example")
    print("=" * 80)
    print()
    print("This example creates a pipeline to sync GitHub data:")
    print("  • Repositories (your repos)")
    print("  • Issues")
    print("  • Pull Requests")
    print("  • Commits")
    print()
    
    # ============================================================================
    # Step 1: Get GitHub Personal Access Token
    # ============================================================================
    print("📋 Step 1: GitHub Authentication")
    print("-" * 80)
    print()
    print("You need a GitHub Personal Access Token.")
    print("Get one at: https://github.com/settings/tokens")
    print()
    print("Required scopes: repo, read:user")
    print()
    
    github_token = input("Enter your GitHub Personal Access Token: ").strip()
    
    if not github_token:
        print("❌ Token is required. Exiting.")
        return 1
    
    print("✅ Token received")
    print()
    
    # ============================================================================
    # Step 2: Get Fivetran Group ID
    # ============================================================================
    print("📋 Step 2: Fivetran Destination")
    print("-" * 80)
    
    try:
        manager = FivetranManager()
        groups = manager.list_groups()
        
        if not groups:
            print("❌ No Fivetran groups found.")
            print("Create one: python scripts/create_fivetran_group.py --name 'GitHub Data'")
            return 1
        
        print(f"Available groups:")
        for i, group in enumerate(groups, 1):
            print(f"  {i}. {group['name']} (ID: {group['id']})")
        print()
        
        group_id = groups[0]['id']
        print(f"🎯 Using: {groups[0]['name']}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    # ============================================================================
    # Step 3: Define Requirements
    # ============================================================================
    print("📋 Step 3: Pipeline Requirements")
    print("-" * 80)
    
    requirements = """
    I want to sync GitHub data for my repositories including:
    - Repositories: All repos I have access to
    - Issues: Track all issues across repositories
    - Pull Requests: Monitor PR activity and status
    - Commits: Track commit history
    
    Calculate these metrics:
    - Repository activity (commits, PRs, issues)
    - Issue resolution time
    - PR merge time
    - Most active contributors
    - Language distribution across repos
    """
    
    print(requirements)
    print()
    
    # Load GitHub OpenAPI spec
    openapi_file = Path(__file__).parent / "github_api.json"
    with open(openapi_file, 'r') as f:
        openapi_spec = f.read()
    
    print(f"✅ Loaded GitHub API spec")
    print()
    
    # ============================================================================
    # Step 4: Configure Authentication
    # ============================================================================
    print("📋 Step 4: Authentication Configuration")
    print("-" * 80)
    
    # GitHub uses Bearer token authentication
    auth_config = {
        "method": "bearer",
        "header_name": "Authorization",
        "header_prefix": "Bearer"
    }
    
    source_api_credentials = {
        "api_url": "https://api.github.com",
        "api_key": github_token,
        "auth_method": "bearer",
        "auth_header_name": "Authorization",
        "auth_header_prefix": "Bearer"
    }
    
    print("API: https://api.github.com")
    print("Auth: Bearer Token (GitHub PAT)")
    print(f"Token: {'*' * 20}")
    print()
    
    # ============================================================================
    # Step 5: Create and Deploy Pipeline
    # ============================================================================
    print("🚀 Step 5: Creating & Deploying Pipeline")
    print("-" * 80)
    
    input("Press Enter to continue...")
    print()
    
    orchestrator = PipelineOrchestrator()
    
    try:
        result = orchestrator.create_pipeline(
            requirements=requirements,
            openapi_spec=openapi_spec,
            auto_deploy=True,
            fivetran_group_id=group_id,
            source_api_credentials=source_api_credentials,
            auth_config=auth_config
        )
        
        print()
        print("=" * 80)
        print("✅ GITHUB PIPELINE CREATED!")
        print("=" * 80)
        print()
        
        # ========================================================================
        # Step 6: Review Results
        # ========================================================================
        print("📦 Generated Components:")
        print("-" * 80)
        
        print("\n🔌 Fivetran Connector:")
        print(f"   Name: {result['fivetran']['connector_name']}")
        print(f"   Directory: {result['fivetran']['connector_dir']}")
        
        if result['fivetran'].get('deployed'):
            print(f"   ✅ Status: DEPLOYED & SYNCING")
            print(f"   Connector ID: {result['fivetran'].get('connector_id', 'N/A')}")
        else:
            print(f"   ⚠️  Not deployed (see errors above)")
        
        print("\n📊 Data Entities:")
        for entity in result['analysis']['entities']:
            print(f"   • {entity}")
        
        print("\n💾 BigQuery Tables:")
        for table in result['bigquery']['tables']:
            print(f"   • {table}")
        
        print("\n🔨 dbt Models:")
        for model in result['dbt']['staging_models']:
            print(f"   • {model}")
        
        print()
        
        # ========================================================================
        # Step 7: Example Queries
        # ========================================================================
        print("💬 Example Queries (after sync completes):")
        print("-" * 80)
        
        queries = [
            "Show me all my repositories ordered by star count",
            "What are the open issues across all repositories?",
            "List the most recent pull requests",
            "Which repositories have the most commits this month?",
            "Show me issue resolution time by repository"
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"{i}. {query}")
        
        print()
        
        # ========================================================================
        # Summary
        # ========================================================================
        print("=" * 80)
        print("🎉 GITHUB PIPELINE COMPLETE!")
        print("=" * 80)
        print()
        print("What was created:")
        print("  ✅ Fivetran connector with GitHub authentication")
        print("  ✅ BigQuery tables for repos, issues, PRs, commits")
        print("  ✅ dbt transformation models")
        print("  ✅ Auto-deployed and syncing!")
        print()
        print("Next steps:")
        print("  1. Check Fivetran dashboard for sync progress")
        print("  2. View data in BigQuery once sync completes")
        print("  3. Run dbt models for transformations")
        print("  4. Query data using SQL Chat in the UI")
        print()
        print("Note: First sync may take a few minutes depending on repo count")
        print()
        
        return 0
        
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ ERROR")
        print("=" * 80)
        print(f"{e}")
        print()
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

