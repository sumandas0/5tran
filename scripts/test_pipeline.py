"""Simple test script to verify pipeline creation."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator import PipelineOrchestrator
from src.config import validate_config


def test_basic_pipeline():
    """Test basic pipeline creation without OpenAPI spec."""
    print("🧪 Testing 5Tran Pipeline Creation")
    print("=" * 50)
    
    # Validate config
    print("\n1. Validating configuration...")
    config_valid = validate_config()
    
    if not config_valid:
        print("⚠️  Some configuration is missing, but continuing in dev mode...")
    
    # Create orchestrator
    print("\n2. Initializing orchestrator...")
    orchestrator = PipelineOrchestrator()
    
    # Test requirements
    requirements = """
    I want to create a pipeline for our e-commerce store. We need to sync 
    orders, customers, and products from our API. Calculate monthly revenue, 
    customer lifetime value, and identify our top customers.
    """
    
    print("\n3. Creating pipeline...")
    print(f"Requirements: {requirements.strip()}")
    
    try:
        result = orchestrator.create_pipeline(
            requirements=requirements,
            openapi_spec=None
        )
        
        print("\n✅ Pipeline created successfully!")
        print("\nResults:")
        print(f"  - Source: {result['analysis']['source_name']}")
        print(f"  - Entities: {', '.join(result['analysis']['entities'])}")
        print(f"  - Staging Models: {len(result['dbt']['staging_models'])}")
        print(f"  - Mart Models: {len(result['dbt']['mart_models'])}")
        print(f"  - BigQuery Tables: {len(result['bigquery']['tables'])}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Pipeline creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_openapi():
    """Test pipeline creation with OpenAPI spec."""
    print("\n" + "=" * 50)
    print("🧪 Testing with OpenAPI Spec")
    print("=" * 50)
    
    # Read example OpenAPI spec
    example_file = Path(__file__).parent.parent / "examples" / "ecommerce_api.json"
    
    if not example_file.exists():
        print("⚠️  Example OpenAPI file not found, skipping...")
        return True
    
    with open(example_file, 'r') as f:
        openapi_spec = f.read()
    
    print("\n1. Creating orchestrator...")
    orchestrator = PipelineOrchestrator()
    
    requirements = "Create a pipeline for our e-commerce API with orders, customers, and products."
    
    print("\n2. Creating pipeline with OpenAPI spec...")
    
    try:
        result = orchestrator.create_pipeline(
            requirements=requirements,
            openapi_spec=openapi_spec
        )
        
        print("\n✅ Pipeline with OpenAPI created successfully!")
        print("\nResults:")
        print(f"  - Source: {result['analysis']['source_name']}")
        print(f"  - Endpoints: {len(result['analysis'].get('endpoints', []))}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Pipeline creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("🚀 5Tran Pipeline Test Suite")
    print()
    
    results = []
    
    # Test 1: Basic pipeline
    results.append(("Basic Pipeline", test_basic_pipeline()))
    
    # Test 2: With OpenAPI
    results.append(("OpenAPI Pipeline", test_with_openapi()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return all(p for _, p in results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

