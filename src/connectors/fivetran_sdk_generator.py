"""Fivetran Connector SDK skeleton generator."""

import json
from pathlib import Path
from typing import Dict, Any, List


class FivetranSDKGenerator:
    """Generates Fivetran Connector SDK Python skeleton."""
    
    def generate_connector(
        self,
        api_summary: Dict[str, Any],
        output_dir: Path,
        connector_name: str
    ) -> Dict[str, Path]:
        """
        Generate a complete Fivetran Connector SDK skeleton.
        
        Returns dict of generated file paths.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        files = {}
        
        # Generate connector.py (main connector logic)
        files['connector'] = self._generate_connector_py(api_summary, output_dir, connector_name)
        
        # Generate configuration.json
        files['config'] = self._generate_configuration_json(api_summary, output_dir)
        
        # Generate requirements.txt
        files['requirements'] = self._generate_requirements_txt(output_dir)
        
        # Generate README.md
        files['readme'] = self._generate_readme(api_summary, output_dir, connector_name)
        
        # Generate test_connector.py
        files['test'] = self._generate_test_file(output_dir, connector_name)
        
        return files
    
    def _generate_connector_py(self, api_summary: Dict[str, Any], output_dir: Path, connector_name: str) -> Path:
        """Generate main connector.py file."""
        
        auth_type = api_summary.get("auth_type", "bearer_token")
        base_url = api_summary.get("base_url", "https://api.example.com")
        entities = api_summary.get("entities", [])
        
        # Generate entity sync methods
        entity_methods = []
        for entity in entities:
            method = f'''
    def sync_{entity}(self, state: dict) -> Generator[dict, None, None]:
        """Sync {entity} data from API."""
        endpoint = "/{entity}"
        url = f"{{self.base_url}}{{endpoint}}"
        
        # Handle pagination
        page = state.get('{entity}_page', 1)
        has_more = True
        
        while has_more:
            params = {{
                'page': page,
                'limit': 100
            }}
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Adjust based on API response structure
            records = data if isinstance(data, list) else data.get('items', [])
            
            for record in records:
                yield {{
                    'table': '{entity}',
                    'data': record
                }}
            
            # Check for more pages
            has_more = len(records) > 0 and len(records) == params['limit']
            page += 1
            
            # Update state
            state['{entity}_page'] = page
'''
            entity_methods.append(method)
        
        entity_methods_str = ''.join(entity_methods)
        
        # Generate auth headers based on auth type
        if auth_type == "bearer_token":
            auth_code = '''
        token = self.configuration.get('api_token')
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })'''
        elif auth_type == "api_key":
            auth_code = '''
        api_key = self.configuration.get('api_key')
        self.session.headers.update({
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        })'''
        else:
            auth_code = '''
        # Configure authentication based on your API requirements
        self.session.headers.update({
            'Content-Type': 'application/json'
        })'''
        
        connector_code = f'''"""
Fivetran Connector for {api_summary.get('title', 'API')}

This connector syncs data from {api_summary.get('title', 'the API')} to your data warehouse.
"""

import requests
from typing import Generator, Dict, Any
from fivetran_connector_sdk import Connector, Operations


class {connector_name.title().replace('_', '')}Connector(Connector):
    """Fivetran connector for {api_summary.get('title', 'API')}."""
    
    def __init__(self, configuration: Dict[str, Any]):
        """Initialize connector with configuration."""
        self.configuration = configuration
        self.base_url = "{base_url}"
        self.session = requests.Session()
        self._setup_auth()
    
    def _setup_auth(self):
        """Setup authentication for API requests."""{auth_code}
    
    def schema(self) -> Dict[str, Any]:
        """
        Define the schema for tables to sync.
        
        Returns dict mapping table names to their schemas.
        """
        schema = {{}}
        
{self._generate_schema_definitions(entities)}
        
        return schema
    
    def update(self, state: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        """
        Main sync method - yields records to sync.
        
        Args:
            state: State dict from previous sync (for incremental syncs)
            
        Yields:
            Records to insert/update in warehouse
        """
        operations = Operations()
        
{self._generate_sync_calls(entities)}
    
{entity_methods_str}


def connector_instance(configuration: Dict[str, Any]) -> {connector_name.title().replace('_', '')}Connector:
    """Factory function to create connector instance."""
    return {connector_name.title().replace('_', '')}Connector(configuration)
'''
        
        connector_file = output_dir / "connector.py"
        with open(connector_file, 'w') as f:
            f.write(connector_code)
        
        return connector_file
    
    def _generate_schema_definitions(self, entities: List[str]) -> str:
        """Generate schema definitions for entities."""
        schemas = []
        for entity in entities:
            schema = f'''        schema['{entity}'] = {{
            'primary_key': ['id'],
            'columns': {{
                'id': {{'type': 'STRING', 'nullable': False}},
                'name': {{'type': 'STRING', 'nullable': True}},
                'created_at': {{'type': 'TIMESTAMP', 'nullable': True}},
                'updated_at': {{'type': 'TIMESTAMP', 'nullable': True}},
                # Add more columns based on your API schema
            }}
        }}
'''
            schemas.append(schema)
        return '\n'.join(schemas)
    
    def _generate_sync_calls(self, entities: List[str]) -> str:
        """Generate sync method calls."""
        calls = []
        for entity in entities:
            call = f'''        # Sync {entity}
        for record in self.sync_{entity}(state):
            yield record
'''
            calls.append(call)
        return '\n'.join(calls)
    
    def _generate_configuration_json(self, api_summary: Dict[str, Any], output_dir: Path) -> Path:
        """Generate configuration.json for connector."""
        
        auth_type = api_summary.get("auth_type", "bearer_token")
        
        # Define configuration fields based on auth type
        if auth_type == "bearer_token":
            auth_fields = [
                {
                    "name": "api_token",
                    "label": "API Token",
                    "description": "Bearer token for API authentication",
                    "required": True,
                    "type": "string"
                }
            ]
        elif auth_type == "api_key":
            auth_fields = [
                {
                    "name": "api_key",
                    "label": "API Key",
                    "description": "API key for authentication",
                    "required": True,
                    "type": "string"
                }
            ]
        else:
            auth_fields = [
                {
                    "name": "credentials",
                    "label": "API Credentials",
                    "description": "Authentication credentials",
                    "required": True,
                    "type": "string"
                }
            ]
        
        config = {
            "name": api_summary.get('title', 'Custom API Connector'),
            "description": api_summary.get('description', 'Sync data from custom API'),
            "version": "1.0.0",
            "configuration": {
                "fields": auth_fields + [
                    {
                        "name": "start_date",
                        "label": "Start Date",
                        "description": "Start date for historical sync (YYYY-MM-DD)",
                        "required": False,
                        "type": "string"
                    }
                ]
            },
            "supported_sync_modes": ["full_refresh", "incremental"],
            "tables": [
                {
                    "name": entity,
                    "sync_mode": "incremental",
                    "primary_key": ["id"]
                }
                for entity in api_summary.get("entities", [])
            ]
        }
        
        config_file = output_dir / "configuration.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config_file
    
    def _generate_requirements_txt(self, output_dir: Path) -> Path:
        """Generate requirements.txt for connector."""
        
        requirements = """# Fivetran Connector SDK dependencies
fivetran-connector-sdk>=1.0.0
requests>=2.31.0
python-dateutil>=2.8.2
"""
        
        req_file = output_dir / "requirements.txt"
        with open(req_file, 'w') as f:
            f.write(requirements)
        
        return req_file
    
    def _generate_readme(self, api_summary: Dict[str, Any], output_dir: Path, connector_name: str) -> Path:
        """Generate README.md for connector."""
        
        readme = f"""# {api_summary.get('title', 'API')} Fivetran Connector

This is a custom Fivetran connector built with the Fivetran Connector SDK.

## Overview

- **API**: {api_summary.get('title', 'Custom API')}
- **Base URL**: {api_summary.get('base_url', 'N/A')}
- **Auth Type**: {api_summary.get('auth_type', 'N/A')}
- **Entities**: {', '.join(api_summary.get('entities', []))}

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure authentication in `configuration.json`

3. Test the connector:
   ```bash
   python test_connector.py
   ```

## Configuration

The connector requires the following configuration:

- **api_token**: Your API authentication token
- **start_date** (optional): Historical sync start date

## Tables Synced

{self._generate_tables_doc(api_summary.get('entities', []))}

## Development

To modify this connector:

1. Update `connector.py` with your custom logic
2. Adjust schema definitions in the `schema()` method
3. Modify sync methods for each entity
4. Test locally before deploying

## Deployment

Deploy this connector to Fivetran using:

```bash
5tran deploy --config ../.5tran.yml
```

## Resources

- [Fivetran Connector SDK Documentation](https://fivetran.com/docs/connectors/connector-sdk)
- [API Documentation]({api_summary.get('base_url', '')})
"""
        
        readme_file = output_dir / "README.md"
        with open(readme_file, 'w') as f:
            f.write(readme)
        
        return readme_file
    
    def _generate_tables_doc(self, entities: List[str]) -> str:
        """Generate tables documentation."""
        docs = []
        for entity in entities:
            docs.append(f"- **{entity}**: Syncs {entity} data with incremental updates")
        return '\n'.join(docs)
    
    def _generate_test_file(self, output_dir: Path, connector_name: str) -> Path:
        """Generate test file for connector."""
        
        test_code = f'''"""Test file for {connector_name} connector."""

import json
from connector import connector_instance


def test_connector():
    """Test connector functionality."""
    
    # Load configuration
    with open('configuration.json', 'r') as f:
        config_template = json.load(f)
    
    # Create test configuration
    # TODO: Add your actual credentials here for testing
    test_config = {{
        'api_token': 'YOUR_TEST_TOKEN_HERE',
        'start_date': '2024-01-01'
    }}
    
    # Create connector instance
    connector = connector_instance(test_config)
    
    # Test schema
    print("Testing schema...")
    schema = connector.schema()
    print(f"Tables: {{list(schema.keys())}}")
    
    # Test sync (limited)
    print("\\nTesting sync...")
    state = {{}}
    count = 0
    
    for record in connector.update(state):
        print(f"Record from {{record['table']}}: {{list(record['data'].keys())}}")
        count += 1
        if count >= 5:  # Limit to 5 records for testing
            break
    
    print(f"\\nTest completed! Synced {{count}} records")


if __name__ == '__main__':
    test_connector()
'''
        
        test_file = output_dir / "test_connector.py"
        with open(test_file, 'w') as f:
            f.write(test_code)
        
        return test_file

