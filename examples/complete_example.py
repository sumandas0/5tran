#!/usr/bin/env python3
"""
Complete End-to-End Example: E-Commerce Pipeline with Auto-Deployment

This example demonstrates how to:
1. Generate a complete data pipeline from requirements
2. Auto-deploy Fivetran connector to start syncing
3. Query the data with natural language

Prerequisites:
- .env file with GEMINI_API_KEY, FIVETRAN_API_KEY, FIVETRAN_API_SECRET
- Fivetran group ID (destination)
- Source API credentials
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator import PipelineOrchestrator
from src.connectors.fivetran_manager import FivetranManager


def main():
    """Run complete e-commerce pipeline example."""
    
    print("=" * 80)
    print("🚀 5Tran Complete Example: E-Commerce Data Pipeline")
    print("=" * 80)
    print()
    
    # ============================================================================
    # Step 1: Get Fivetran Group ID
    # ============================================================================
    print("📋 Step 1: Listing Fivetran Groups (Destinations)")
    print("-" * 80)
    
    try:
        manager = FivetranManager()
        groups = manager.list_groups()
        
        if not groups:
            print("❌ No Fivetran groups found. Create one first:")
            print("   python scripts/create_fivetran_group.py --name 'Production DW'")
            return 1
        
        print(f"✅ Found {len(groups)} group(s):\n")
        for i, group in enumerate(groups, 1):
            print(f"   {i}. {group['name']} (ID: {group['id']})")
        print()
        
        # Use first group for demo
        group_id = groups[0]['id']
        print(f"🎯 Using group: {groups[0]['name']} ({group_id})")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure FIVETRAN_API_KEY and FIVETRAN_API_SECRET are set in .env")
        return 1
    
    # ============================================================================
    # Step 2: Define Requirements and OpenAPI Spec
    # ============================================================================
    print("📋 Step 2: Defining Requirements")
    print("-" * 80)
    
    requirements = """
    I want to sync data from our e-commerce platform API including:
    - Orders: Order history with customer info and line items
    - Customers: Customer profiles with lifetime spending
    - Products: Product catalog with inventory levels
    
    Calculate these business metrics:
    - Monthly revenue and growth rate
    - Customer lifetime value (CLV)
    - Top 10 products by revenue
    - Average order value (AOV)
    - Customer retention rate
    """
    
    print("Requirements:")
    print(requirements)
    print()
    
    # Load OpenAPI specification
    openapi_file = Path(__file__).parent / "ecommerce_api.json"
    with open(openapi_file, 'r') as f:
        openapi_spec = f.read()
    
    print(f"✅ Loaded OpenAPI spec: {openapi_file}")
    print()
    
    # ============================================================================
    # Step 3: Configure Source API Credentials
    # ============================================================================
    print("📋 Step 3: Configuring Source API")
    print("-" * 80)
    
    # REPLACE THESE WITH YOUR ACTUAL API CREDENTIALS
    source_api_credentials = {
        "api_url": "https://api.ecommerce-example.com/v1",
        "api_key": "your_api_key_here",  # Replace with real API key
        "auth_type": "bearer"
    }
    
    print(f"API URL: {source_api_credentials['api_url']}")
    print(f"Auth Type: {source_api_credentials['auth_type']}")
    print(f"API Key: {'*' * 20} (hidden)")
    print()
    
    # ============================================================================
    # Step 4: Create and Deploy Pipeline (ONE COMMAND!)
    # ============================================================================
    print("🚀 Step 4: Creating & Deploying Pipeline")
    print("-" * 80)
    print("This will:")
    print("  1. Analyze requirements with Gemini AI")
    print("  2. Parse OpenAPI specification")
    print("  3. Generate Fivetran Connector SDK code")
    print("  4. Deploy connector to Fivetran")
    print("  5. Create BigQuery tables")
    print("  6. Generate dbt models")
    print("  7. Start syncing data")
    print()
    
    input("Press Enter to continue...")
    print()
    
    orchestrator = PipelineOrchestrator()
    
    try:
        result = orchestrator.create_pipeline(
            requirements=requirements,
            openapi_spec=openapi_spec,
            auto_deploy=True,  # ✨ THE MAGIC FLAG!
            fivetran_group_id=group_id,
            source_api_credentials=source_api_credentials
        )
        
        print()
        print("=" * 80)
        print("✅ PIPELINE CREATED AND DEPLOYED SUCCESSFULLY!")
        print("=" * 80)
        print()
        
        # ========================================================================
        # Step 5: Review Generated Components
        # ========================================================================
        print("📦 Generated Components:")
        print("-" * 80)
        
        print("\n🔌 Fivetran Connector:")
        print(f"   Name: {result['fivetran']['connector_name']}")
        print(f"   Directory: {result['fivetran']['connector_dir']}")
        
        if result['fivetran'].get('deployed'):
            print(f"   ✅ Status: DEPLOYED")
            if result['fivetran'].get('connector_id'):
                print(f"   Connector ID: {result['fivetran']['connector_id']}")
            print(f"   🔄 Data is now syncing to your warehouse!")
        else:
            print(f"   ⚠️  Status: Generated but not deployed")
        
        print("\n📊 Data Entities:")
        for entity in result['analysis']['entities']:
            print(f"   • {entity}")
        
        print("\n📈 Business Metrics:")
        for metric in result['analysis']['business_metrics']:
            print(f"   • {metric}")
        
        print("\n💾 BigQuery:")
        print(f"   Dataset: {result['bigquery']['dataset']}")
        print(f"   Tables Created: {len(result['bigquery']['tables'])}")
        for table in result['bigquery']['tables']:
            print(f"   • {table}")
        
        print("\n🔨 dbt Models:")
        print(f"   Staging Models: {len(result['dbt']['staging_models'])}")
        for model in result['dbt']['staging_models']:
            print(f"   • {model}")
        print(f"   Mart Models: {len(result['dbt']['mart_models'])}")
        for model in result['dbt']['mart_models']:
            print(f"   • {model}")
        
        print()
        
        # ========================================================================
        # Step 6: Check Connector Status
        # ========================================================================
        if result['fivetran'].get('connector_id'):
            print("🔍 Step 5: Checking Connector Status")
            print("-" * 80)
            
            connector_id = result['fivetran']['connector_id']
            status = manager.get_connector_status(connector_id)
            
            print(f"Connector ID: {connector_id}")
            print(f"Status: {status['status']}")
            print(f"Sync State: {status['sync_state']}")
            print(f"Last Sync: {status.get('last_sync', 'N/A')}")
            print()
        
        # ========================================================================
        # Step 7: Natural Language Queries (after sync completes)
        # ========================================================================
        print("💬 Step 6: Natural Language Queries")
        print("-" * 80)
        print("Once data syncs, you can query with natural language:")
        print()
        
        example_queries = [
            "What is our total revenue this month?",
            "Show me the top 10 customers by lifetime value",
            "What are our best-selling products?",
            "Calculate the average order value for each customer segment",
            "Show me monthly revenue growth over the last 6 months"
        ]
        
        for i, query in enumerate(example_queries, 1):
            print(f"{i}. {query}")
        
        print()
        print("To run these queries:")
        print("  • Use the Gradio UI (SQL Chat tab)")
        print("  • Or programmatically: orchestrator.execute_nl_query('your question')")
        print()
        
        # ========================================================================
        # Summary
        # ========================================================================
        print("=" * 80)
        print("🎉 EXAMPLE COMPLETE!")
        print("=" * 80)
        print()
        print("What just happened:")
        print("  ✅ Generated Fivetran Connector SDK code")
        print("  ✅ Deployed connector to Fivetran (live!)")
        print("  ✅ Created BigQuery tables")
        print("  ✅ Generated dbt transformation models")
        print("  ✅ Started syncing data from source API")
        print()
        print("Next steps:")
        print("  1. Monitor sync progress in Fivetran dashboard")
        print("  2. Run dbt models: cd dbt_project && dbt run")
        print("  3. Query data using the Gradio UI")
        print("  4. Build dashboards on top of mart models")
        print()
        print("View generated files:")
        print(f"  • Connector: {result['fivetran']['connector_dir']}")
        print(f"  • dbt Models: {result['dbt']['project_dir']}/models/")
        print()
        
        return 0
        
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ ERROR")
        print("=" * 80)
        print(f"Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

