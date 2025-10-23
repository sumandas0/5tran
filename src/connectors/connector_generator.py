"""Fivetran Connector SDK code generator."""

from typing import Dict, Any, List
from pathlib import Path
import json


class ConnectorGenerator:
    """Generate Fivetran Connector SDK compliant connector.py files."""
    
    CONNECTOR_TEMPLATE = '''"""
Fivetran Connector SDK - {source_name}
Auto-generated connector for {source_name} API.
"""

import requests
from typing import Any
from fivetran_connector_sdk import Connector
from fivetran_connector_sdk import Operations as op
from fivetran_connector_sdk import Logging as log


def schema(configuration: dict[str, Any]):
    """
    Define the schema of tables and columns.
    
    Args:
        configuration: Configuration dict containing API credentials and settings
        
    Returns:
        Schema definition for Fivetran
    """
    return [
{table_schemas}
    ]


def update(configuration: dict[str, Any], state: dict[str, Any]):
    """
    Extract data from source and yield operations.
    
    Args:
        configuration: Configuration dict with API credentials
        state: State dict for incremental syncs
        
    Yields:
        Operations for upserting data and updating state
    """
    # Extract configuration
    api_url = configuration.get("api_url")
    api_key = configuration.get("api_key")
    auth_method = configuration.get("auth_method", "{auth_method}")
    header_name = configuration.get("auth_header_name", "{auth_header_name}")
    header_prefix = configuration.get("auth_header_prefix", "{auth_header_prefix}")
    
    # Setup authentication headers
    headers = {{}}
    if auth_method == "bearer":
        headers[header_name] = f"{{header_prefix}} {{api_key}}".strip()
    elif auth_method == "api_key_header":
        headers[header_name] = api_key
    elif auth_method == "basic_auth":
        import base64
        credentials = base64.b64encode(api_key.encode()).decode()
        headers[header_name] = f"Basic {{credentials}}"
    elif auth_method == "custom_header":
        headers[header_name] = f"{{header_prefix}} {{api_key}}".strip() if header_prefix else api_key
    else:
        # Default to bearer
        headers["Authorization"] = f"Bearer {{api_key}}"
    
    log.info(f"Starting sync for {{api_url}}")
    
{endpoint_extraction}
    
    # Update final state
    op.checkpoint(state)
    log.info("Sync completed successfully")


def get_endpoint_data(url: str, headers: dict, params: dict = None) -> list:
    """
    Fetch data from API endpoint with pagination support.
    
    Args:
        url: API endpoint URL
        headers: Request headers
        params: Query parameters
        
    Returns:
        List of records from API
    """
    all_records = []
    page = 1
    has_more = True
    
    while has_more:
        try:
            request_params = params or {{}}
            request_params.update({{
                "page": page,
                "per_page": 100
            }})
            
            response = requests.get(url, headers=headers, params=request_params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Handle different response structures
            if isinstance(data, list):
                records = data
            elif isinstance(data, dict):
                # Try common pagination keys
                records = (
                    data.get("data") or 
                    data.get("results") or 
                    data.get("items") or 
                    [data]
                )
            else:
                records = [data]
            
            if not records:
                has_more = False
            else:
                all_records.extend(records)
                page += 1
                
                # Check if more pages exist
                if isinstance(data, dict):
                    has_more = (
                        data.get("has_more", False) or
                        data.get("next") is not None or
                        len(records) == 100
                    )
                else:
                    has_more = len(records) == 100
                    
        except requests.exceptions.RequestException as e:
            log.warning(f"Error fetching data: {{e}}")
            has_more = False
    
    return all_records


# Initialize connector
connector = Connector(update=update, schema=schema)


if __name__ == "__main__":
    # Required for Fivetran to run the connector
    connector.debug()
'''
    
    @staticmethod
    def generate_table_schema(table_name: str, columns: List[Dict[str, str]], 
                             primary_keys: List[str] = None) -> str:
        """Generate schema definition for a table."""
        primary_keys = primary_keys or ["id"]
        
        schema_lines = [
            f'        {{',
            f'            "name": "{table_name}",',
            f'            "columns": {{'
        ]
        
        for col in columns:
            col_name = col.get("name", "unknown")
            col_type = col.get("type", "STRING")
            schema_lines.append(f'                "{col_name}": "{col_type}",')
        
        # Remove trailing comma from last column
        if schema_lines[-1].endswith(','):
            schema_lines[-1] = schema_lines[-1][:-1]
        
        schema_lines.append('            },')
        schema_lines.append(f'            "primary_key": {json.dumps(primary_keys)}')
        schema_lines.append('        }')
        
        return '\n'.join(schema_lines)
    
    @staticmethod
    def generate_endpoint_extraction(endpoint: str, table_name: str, 
                                     primary_key: str = "id") -> str:
        """Generate extraction code for an endpoint."""
        return f'''    # Extract {table_name}
    {table_name}_url = f"{{api_url}}{endpoint}"
    log.info(f"Fetching {table_name} from {{{table_name}_url}}")
    
    {table_name}_records = get_endpoint_data({table_name}_url, headers)
    log.info(f"Retrieved {{{len({table_name}_records)}}} {table_name} records")
    
    for record in {table_name}_records:
        # Ensure primary key exists
        if "{primary_key}" not in record:
            log.warning(f"Skipping record without {primary_key}: {{record}}")
            continue
        
        op.upsert(
            table="{table_name}",
            data=record
        )
    
    # Update state for this table
    if {table_name}_records:
        state["{table_name}_last_sync"] = {table_name}_records[-1].get("updated_at") or {table_name}_records[-1].get("created_at")
'''
    
    def generate_connector(
        self,
        source_name: str,
        api_url: str,
        endpoints: List[Dict[str, Any]],
        auth_config: Dict[str, str] = None
    ) -> str:
        """
        Generate complete connector.py code.
        
        Args:
            source_name: Name of the source system
            api_url: Base URL for the API
            endpoints: List of endpoint configurations
            auth_config: Authentication configuration dict
            
        Returns:
            Complete connector.py code
        """
        if auth_config is None:
            auth_config = {
                "method": "bearer",
                "header_name": "Authorization",
                "header_prefix": "Bearer"
            }
        # Generate table schemas
        table_schemas = []
        endpoint_extractions = []
        
        for endpoint_config in endpoints:
            table_name = endpoint_config.get("table_name", "data")
            endpoint_path = endpoint_config.get("path", "/data")
            columns = endpoint_config.get("columns", [
                {"name": "id", "type": "STRING"},
                {"name": "data", "type": "JSON"},
                {"name": "created_at", "type": "TIMESTAMP"}
            ])
            primary_keys = endpoint_config.get("primary_keys", ["id"])
            
            # Generate schema for this table
            table_schema = self.generate_table_schema(
                table_name=table_name,
                columns=columns,
                primary_keys=primary_keys
            )
            table_schemas.append(table_schema)
            
            # Generate extraction code for this endpoint
            extraction_code = self.generate_endpoint_extraction(
                endpoint=endpoint_path,
                table_name=table_name,
                primary_key=primary_keys[0] if primary_keys else "id"
            )
            endpoint_extractions.append(extraction_code)
        
        # Combine all schemas and extractions
        all_table_schemas = ',\n'.join(table_schemas)
        all_extractions = '\n'.join(endpoint_extractions)
        
        # Generate final connector code with auth config
        connector_code = self.CONNECTOR_TEMPLATE.format(
            source_name=source_name,
            table_schemas=all_table_schemas,
            endpoint_extraction=all_extractions,
            auth_method=auth_config.get("method", "bearer"),
            auth_header_name=auth_config.get("header_name", "Authorization"),
            auth_header_prefix=auth_config.get("header_prefix", "Bearer")
        )
        
        return connector_code
    
    def generate_requirements_txt(self, additional_packages: List[str] = None) -> str:
        """Generate requirements.txt for the connector."""
        base_requirements = [
            "fivetran-connector-sdk>=2.0.0",
            "requests>=2.31.0"
        ]
        
        if additional_packages:
            base_requirements.extend(additional_packages)
        
        return '\n'.join(base_requirements)
    
    def generate_configuration_json(
        self,
        api_url: str,
        api_key_placeholder: str = "YOUR_API_KEY_HERE",
        auth_config: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Generate configuration.json template."""
        if auth_config is None:
            auth_config = {
                "method": "bearer",
                "header_name": "Authorization",
                "header_prefix": "Bearer"
            }
        
        return {
            "api_url": api_url,
            "api_key": api_key_placeholder,
            "auth_method": auth_config.get("method", "bearer"),
            "auth_header_name": auth_config.get("header_name", "Authorization"),
            "auth_header_prefix": auth_config.get("header_prefix", "Bearer")
        }
    
    def save_connector_files(
        self,
        output_dir: Path,
        connector_code: str,
        requirements: str,
        configuration: Dict[str, Any]
    ):
        """
        Save all connector files to output directory.
        
        Args:
            output_dir: Directory to save files
            connector_code: Generated connector.py code
            requirements: requirements.txt content
            configuration: configuration.json content
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save connector.py
        connector_file = output_dir / "connector.py"
        connector_file.write_text(connector_code)
        
        # Save requirements.txt
        requirements_file = output_dir / "requirements.txt"
        requirements_file.write_text(requirements)
        
        # Save configuration.json template
        config_file = output_dir / "configuration.json.template"
        with open(config_file, 'w') as f:
            json.dump(configuration, f, indent=2)
        
        # Create README
        readme = f"""# Fivetran Connector

## Setup

1. Copy configuration.json.template to configuration.json
2. Fill in your API credentials in configuration.json
3. Deploy the connector:

```bash
fivetran deploy
```

## Testing Locally

```bash
fivetran debug
```

## Files

- `connector.py`: Main connector implementation
- `requirements.txt`: Python dependencies
- `configuration.json`: API credentials (do not commit!)
"""
        
        readme_file = output_dir / "README.md"
        readme_file.write_text(readme)
        
        return {
            "connector_py": str(connector_file),
            "requirements_txt": str(requirements_file),
            "config_template": str(config_file),
            "readme": str(readme_file)
        }

