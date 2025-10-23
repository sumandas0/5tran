"""Main orchestrator for pipeline creation and management."""

from typing import Dict, Any, Optional, List
from pathlib import Path

from src.agent.gemini_agent import GeminiAgent
from src.connectors.openapi_parser import OpenAPIParser
from src.connectors.fivetran_manager import FivetranManager
from src.transformations.dbt_generator import DBTGenerator
from src.warehouse.bigquery_manager import BigQueryManager
from src.config import GCP_PROJECT_ID, BIGQUERY_DATASET


class PipelineOrchestrator:
    """Orchestrates the entire pipeline creation process."""
    
    def __init__(self):
        """Initialize orchestrator with all components."""
        try:
            self.agent = GeminiAgent()
        except Exception as e:
            print(f"⚠️  Warning: Failed to initialize Gemini agent: {e}")
            self.agent = None
        
        self.fivetran = FivetranManager()
        self.dbt = DBTGenerator()
        self.bigquery = BigQueryManager()
        
        self.current_pipeline = None
    
    def create_pipeline(
        self,
        requirements: str,
        openapi_spec: Optional[str] = None,
        auto_deploy: bool = False,
        fivetran_group_id: Optional[str] = None,
        source_api_credentials: Optional[Dict[str, str]] = None,
        auth_config: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a complete data pipeline from requirements.
        
        Args:
            requirements: Natural language requirements
            openapi_spec: Optional OpenAPI specification
            auto_deploy: If True, automatically deploy connector to Fivetran
            fivetran_group_id: Fivetran group ID for deployment (required if auto_deploy=True)
            source_api_credentials: Source API credentials for the connector
                                   {"api_url": "...", "api_key": "...", "auth_type": "bearer"}
        
        Returns:
            Pipeline information including deployment status
        """
        
        print("\n🚀 Starting pipeline creation...")
        print("=" * 50)
        
        # Step 1: Analyze requirements with Gemini
        print("\n📋 Step 1: Analyzing requirements...")
        if not self.agent:
            # Fallback if Gemini is not available
            analysis = self._fallback_analysis(requirements, openapi_spec)
        else:
            analysis = self.agent.analyze_requirements(requirements, openapi_spec)
        
        print(f"   Source: {analysis.get('source_name', 'Unknown')}")
        print(f"   Entities: {', '.join(analysis.get('entities', []))}")
        
        # Step 2: Parse OpenAPI spec if provided
        schema_info = {}
        endpoints = analysis.get('endpoints', [])
        
        if openapi_spec:
            print("\n📄 Step 2: Parsing OpenAPI specification...")
            try:
                parser = OpenAPIParser(openapi_spec)
                summary = parser.get_summary()
                
                schema_info = {
                    "base_url": summary["base_url"],
                    "auth_type": summary["auth_type"]
                }
                
                if not endpoints:
                    endpoints = summary["endpoints"][:5]  # Limit to first 5
                
                print(f"   Found {len(summary['endpoints'])} endpoints")
                print(f"   Entities: {', '.join(summary['entities'])}")
                
            except Exception as e:
                print(f"   ⚠️  Warning: Failed to parse OpenAPI spec: {e}")
        
        # Step 3: Generate Fivetran Connector SDK code
        print("\n🔧 Step 3: Generating Fivetran Connector SDK...")
        
        # Prepare endpoint configurations
        endpoint_configs = []
        for endpoint_path in endpoints:
            # Extract table name from endpoint
            table_name = endpoint_path.strip("/").split("/")[0].lower()
            if not table_name:
                table_name = "data"
            
            endpoint_configs.append({
                "table_name": table_name,
                "path": endpoint_path,
                "columns": [
                    {"name": "id", "type": "STRING"},
                    {"name": "data", "type": "JSON"},
                    {"name": "created_at", "type": "TIMESTAMP"},
                    {"name": "updated_at", "type": "TIMESTAMP"}
                ],
                "primary_keys": ["id"]
            })
        
        # Use auth_config if provided, otherwise fall back to schema_info
        final_auth_config = auth_config or {
            "method": schema_info.get('auth_type', 'bearer'),
            "header_name": "Authorization",
            "header_prefix": "Bearer"
        }
        
        # Generate connector code
        connector_info = self.fivetran.generate_connector_code(
            source_name=analysis.get('source_name', 'unknown_source'),
            api_url=schema_info.get('base_url', 'https://api.example.com'),
            endpoints=endpoint_configs,
            auth_config=final_auth_config
        )
        
        print(f"✓ Connector files generated in: {connector_info['connector_dir']}")
        
        # Auto-deploy if requested
        deployment_result = None
        if auto_deploy:
            if not fivetran_group_id:
                print("⚠️  Warning: auto_deploy=True but no fivetran_group_id provided. Skipping deployment.")
            elif not source_api_credentials:
                print("⚠️  Warning: auto_deploy=True but no source_api_credentials provided. Skipping deployment.")
            else:
                print("\n🚀 Step 3b: Auto-deploying connector to Fivetran...")
                try:
                    deployment_result = self.deploy_connector(
                        connector_dir=connector_info['connector_dir'],
                        group_id=fivetran_group_id,
                        api_credentials=source_api_credentials
                    )
                    print("✅ Connector deployed and syncing!")
                except Exception as e:
                    print(f"❌ Deployment failed: {e}")
                    print("   You can deploy manually later using the CLI scripts")
                    deployment_result = {"status": "failed", "error": str(e)}
        else:
            print("   Note: Use auto_deploy=True with credentials to deploy automatically")
        
        # Step 4: Create BigQuery schema
        print("\n💾 Step 4: Setting up BigQuery schema...")
        self.bigquery.create_dataset()
        
        # Create tables for each entity
        tables_created = []
        entities = analysis.get('entities', [])
        
        for entity in entities[:3]:  # Limit to first 3 entities
            table_name = f"raw_{analysis.get('source_name', 'source')}_{entity}".lower().replace(' ', '_')
            
            # Create basic schema
            schema = [
                {"name": "id", "type": "STRING"},
                {"name": "data", "type": "JSON"},
                {"name": "created_at", "type": "TIMESTAMP"}
            ]
            
            success = self.bigquery.create_table_from_schema(table_name, schema)
            if success:
                tables_created.append(table_name)
        
        # Step 5: Initialize dbt project
        print("\n📊 Step 5: Initializing dbt project...")
        self.dbt.initialize_project(
            project_id=GCP_PROJECT_ID or "your-gcp-project-id",
            dataset=BIGQUERY_DATASET
        )
        
        # Step 6: Generate dbt models
        print("\n🔨 Step 6: Generating dbt models...")
        
        # Create staging models
        staging_models = []
        source_name = analysis.get('source_name', 'source').lower().replace(' ', '_')
        
        for entity in entities[:3]:
            columns = [
                {"name": "id", "type": "STRING"},
                {"name": "data", "type": "JSON"},
                {"name": "created_at", "type": "TIMESTAMP"}
            ]
            
            model_file = self.dbt.create_staging_model(
                source_name=source_name,
                table_name=entity,
                columns=columns
            )
            staging_models.append(model_file.stem)
        
        # Create sources.yml
        tables_for_sources = [
            {"name": entity, "description": f"{entity} data from {source_name}", "columns": [
                {"name": "id", "type": "STRING"},
                {"name": "data", "type": "JSON"},
                {"name": "created_at", "type": "TIMESTAMP"}
            ]}
            for entity in entities[:3]
        ]
        
        self.dbt.create_sources_yml(source_name, tables_for_sources)
        
        # Create mart model
        mart_models = []
        if analysis.get('business_metrics'):
            mart_file = self.dbt.create_mart_model(
                mart_name=source_name,
                entities=entities,
                metrics=analysis.get('business_metrics', [])
            )
            mart_models.append(mart_file.stem)
        
        # Create schema.yml
        self.dbt.create_schema_yml(staging_models + mart_models)
        
        # Step 7: Store pipeline info
        print("\n✅ Pipeline creation complete!")
        print("=" * 50)
        
        pipeline_info = {
            "analysis": analysis,
            "fivetran": {
                "connector_name": connector_info['connector_name'],
                "connector_dir": connector_info['connector_dir'],
                "files": connector_info['files'],
                "deployed": deployment_result is not None and deployment_result.get('status') == 'deployed',
                "deployment": deployment_result,
                "connector_id": deployment_result.get('connector_id') if deployment_result else None
            },
            "bigquery": {
                "dataset": self.bigquery.dataset_id,
                "tables": tables_created
            },
            "dbt": {
                "project_dir": str(self.dbt.project_dir),
                "staging_models": staging_models,
                "mart_models": mart_models
            },
            "files_created": staging_models + mart_models + [connector_info['connector_name']]
        }
        
        self.current_pipeline = pipeline_info
        return pipeline_info
    
    def execute_nl_query(self, natural_language_query: str) -> Dict[str, Any]:
        """Execute a natural language query against the data warehouse."""
        
        print(f"\n🔍 Executing query: {natural_language_query}")
        
        # Get schema context
        schema_context = self.bigquery.get_schema_context()
        
        # Generate SQL
        if not self.agent:
            return {
                "sql": "-- Gemini agent not available",
                "error": "Gemini API key not configured"
            }
        
        sql = self.agent.generate_sql_from_nl(natural_language_query, schema_context)
        
        print(f"Generated SQL:\n{sql}\n")
        
        # Execute query
        result = self.bigquery.execute_query(sql)
        result['sql'] = sql
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of current pipeline."""
        
        if not self.current_pipeline:
            return None
        
        # Get connector status
        connectors = self.fivetran.list_connectors()
        
        # Get dbt models
        dbt_models = self.dbt.list_models()
        
        # Get BigQuery tables
        bigquery_tables = self.bigquery.list_tables()
        
        return {
            "connectors": connectors,
            "dbt_models": dbt_models,
            "bigquery_tables": bigquery_tables,
            "pipeline_info": self.current_pipeline
        }
    
    def deploy_connector(
        self,
        connector_dir: str,
        group_id: str,
        api_credentials: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Deploy a generated connector to Fivetran.
        
        Args:
            connector_dir: Path to connector directory
            group_id: Fivetran group ID for the destination
            api_credentials: Optional dict with 'api_key' for the source API
            
        Returns:
            Deployment result
        """
        print(f"\n🚀 Deploying connector: {connector_dir}")
        print("=" * 50)
        
        # If API credentials provided, create configuration.json
        if api_credentials:
            import json
            from pathlib import Path
            config_file = Path(connector_dir) / "configuration.json"
            with open(config_file, 'w') as f:
                json.dump(api_credentials, f, indent=2)
            print(f"✓ Created configuration.json")
        
        # Deploy using Fivetran SDK
        result = self.fivetran.deploy_connector(
            connector_dir=Path(connector_dir),
            group_id=group_id
        )
        
        if result['status'] == 'deployed':
            connector_id = result.get('connector_id')
            print(f"\n✅ Connector deployed successfully!")
            if connector_id:
                print(f"   Connector ID: {connector_id}")
            print(f"   Group ID: {group_id}")
            
            # Optionally trigger initial sync
            if connector_id:
                print(f"\n🔄 Triggering initial sync...")
                try:
                    sync_result = self.fivetran.trigger_sync(connector_id)
                    print(f"✓ Initial sync started")
                except Exception as e:
                    print(f"⚠️  Note: Could not trigger sync automatically: {e}")
                    print(f"   You can trigger it manually from the Fivetran dashboard")
        
        return result
    
    def _fallback_analysis(self, requirements: str, openapi_spec: Optional[str]) -> Dict[str, Any]:
        """Fallback analysis when Gemini is not available."""
        # Simple keyword extraction
        entities = []
        if "order" in requirements.lower():
            entities.append("orders")
        if "customer" in requirements.lower():
            entities.append("customers")
        if "product" in requirements.lower():
            entities.append("products")
        
        if not entities:
            entities = ["data"]
        
        return {
            "source_type": "rest_api",
            "source_name": "API Source",
            "endpoints": ["/data"],
            "entities": entities,
            "business_metrics": ["count", "total"],
            "transformations": ["basic staging"],
            "use_case": requirements[:100]
        }

