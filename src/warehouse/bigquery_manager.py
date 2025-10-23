"""BigQuery schema and table management."""

from typing import Dict, Any, List, Optional
from google.cloud import bigquery
from src.config import GCP_PROJECT_ID, BIGQUERY_DATASET, DEV_MODE


class BigQueryManager:
    """Manages BigQuery datasets and tables."""
    
    def __init__(self, project_id: Optional[str] = None, dataset_id: Optional[str] = None):
        """Initialize BigQuery manager."""
        self.project_id = project_id or GCP_PROJECT_ID
        self.dataset_id = dataset_id or BIGQUERY_DATASET
        
        try:
            self.client = bigquery.Client(project=self.project_id)
            self.mock_mode = False
        except Exception as e:
            print(f"⚠️  BigQuery client initialization failed: {e}")
            print("Running in mock mode for development")
            self.client = None
            self.mock_mode = True
    
    def create_dataset(self, dataset_id: Optional[str] = None) -> bool:
        """Create BigQuery dataset if it doesn't exist."""
        dataset_id = dataset_id or self.dataset_id
        
        if self.mock_mode:
            print(f"🔧 Mock: Would create dataset {dataset_id}")
            return True
        
        try:
            dataset_ref = self.client.dataset(dataset_id)
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"
            
            self.client.create_dataset(dataset, exists_ok=True)
            print(f"✓ Created dataset: {dataset_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create dataset: {e}")
            return False
    
    def create_table_from_schema(
        self,
        table_name: str,
        schema: List[Dict[str, str]],
        dataset_id: Optional[str] = None
    ) -> bool:
        """Create a BigQuery table from schema definition."""
        dataset_id = dataset_id or self.dataset_id
        table_ref = f"{self.project_id}.{dataset_id}.{table_name}"
        
        if self.mock_mode:
            print(f"🔧 Mock: Would create table {table_ref} with {len(schema)} columns")
            return True
        
        try:
            # Convert schema to BigQuery format
            bq_schema = []
            for field in schema:
                field_name = field.get("name", field.get("field", "unknown"))
                field_type = self._map_type_to_bigquery(field.get("type", "STRING"))
                field_mode = field.get("mode", "NULLABLE")
                
                bq_schema.append(
                    bigquery.SchemaField(field_name, field_type, mode=field_mode)
                )
            
            # Add metadata columns
            bq_schema.append(bigquery.SchemaField("_loaded_at", "TIMESTAMP", mode="NULLABLE"))
            bq_schema.append(bigquery.SchemaField("_source", "STRING", mode="NULLABLE"))
            
            table = bigquery.Table(table_ref, schema=bq_schema)
            self.client.create_table(table, exists_ok=True)
            
            print(f"✓ Created table: {table_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create table {table_name}: {e}")
            return False
    
    def _map_type_to_bigquery(self, data_type: str) -> str:
        """Map common data types to BigQuery types."""
        type_mapping = {
            "string": "STRING",
            "text": "STRING",
            "integer": "INTEGER",
            "int": "INTEGER",
            "number": "NUMERIC",
            "float": "FLOAT64",
            "double": "FLOAT64",
            "boolean": "BOOLEAN",
            "bool": "BOOLEAN",
            "date": "DATE",
            "datetime": "DATETIME",
            "timestamp": "TIMESTAMP",
            "array": "ARRAY",
            "object": "STRUCT",
            "json": "JSON"
        }
        
        return type_mapping.get(data_type.lower(), "STRING")
    
    def execute_query(self, sql: str) -> Any:
        """Execute SQL query and return results."""
        if self.mock_mode:
            print(f"🔧 Mock: Would execute query:\n{sql[:200]}...")
            return {
                "rows": [],
                "schema": [],
                "message": "Mock query execution (dev mode)"
            }
        
        try:
            query_job = self.client.query(sql)
            results = query_job.result()
            
            # Convert to list of dicts
            rows = [dict(row) for row in results]
            
            return {
                "rows": rows,
                "schema": [field.name for field in results.schema],
                "row_count": len(rows)
            }
            
        except Exception as e:
            print(f"❌ Query execution failed: {e}")
            return {
                "error": str(e),
                "rows": [],
                "schema": []
            }
    
    def list_tables(self, dataset_id: Optional[str] = None) -> List[str]:
        """List all tables in dataset."""
        dataset_id = dataset_id or self.dataset_id
        
        if self.mock_mode:
            return ["mock_table_1", "mock_table_2"]
        
        try:
            tables = self.client.list_tables(dataset_id)
            return [table.table_id for table in tables]
        except Exception as e:
            print(f"❌ Failed to list tables: {e}")
            return []
    
    def get_schema_context(self) -> str:
        """Get schema information as context for SQL generation."""
        if self.mock_mode:
            return """
Available Tables:
- mock_table_1 (id INTEGER, name STRING, created_at TIMESTAMP)
- mock_table_2 (id INTEGER, amount NUMERIC, date DATE)
"""
        
        try:
            tables = self.list_tables()
            context = f"Dataset: {self.dataset_id}\n\nAvailable Tables:\n"
            
            for table_name in tables:
                table_ref = f"{self.project_id}.{self.dataset_id}.{table_name}"
                table = self.client.get_table(table_ref)
                
                context += f"\n{table_name}:\n"
                for field in table.schema:
                    context += f"  - {field.name} ({field.field_type})\n"
            
            return context
            
        except Exception as e:
            print(f"❌ Failed to get schema context: {e}")
            return "No schema information available"
    
    def get_table_preview(self, table_name: str, limit: int = 10) -> Dict[str, Any]:
        """Get preview of table data."""
        dataset_id = self.dataset_id
        sql = f"SELECT * FROM `{self.project_id}.{dataset_id}.{table_name}` LIMIT {limit}"
        
        return self.execute_query(sql)

