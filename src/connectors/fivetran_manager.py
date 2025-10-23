"""Fivetran connector configuration generator."""

import json
from typing import Dict, Any, List
from pathlib import Path
from src.config import MOCK_FIVETRAN, CONFIGS_DIR


class FivetranManager:
    """Manages Fivetran connector configurations."""
    
    def __init__(self, mock_mode: bool = MOCK_FIVETRAN):
        """Initialize Fivetran manager."""
        self.mock_mode = mock_mode
        self.configs_dir = CONFIGS_DIR / "fivetran"
        self.configs_dir.mkdir(parents=True, exist_ok=True)
    
    def create_connector_config(
        self,
        source_name: str,
        source_type: str,
        endpoints: List[str],
        schema_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate Fivetran connector configuration."""
        
        # Create connector configuration
        config = {
            "connector_name": f"{source_name.lower().replace(' ', '_')}_connector",
            "service": "rest_api",
            "config": {
                "source_name": source_name,
                "source_type": source_type,
                "base_url": schema_info.get("base_url", "https://your-api-endpoint.com"),
                "auth_type": schema_info.get("auth_type", "bearer_token"),
                "endpoints": []
            }
        }
        
        # Add endpoint configurations
        for endpoint in endpoints:
            endpoint_config = {
                "path": endpoint,
                "method": "GET",
                "primary_key": ["id"],
                "sync_mode": "full_refresh",
                "pagination": {
                    "type": "offset",
                    "limit": 100
                }
            }
            config["config"]["endpoints"].append(endpoint_config)
        
        # Save configuration
        config_file = self.configs_dir / f"{config['connector_name']}.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✓ Created Fivetran config: {config_file}")
        
        return config
    
    def create_connector(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create Fivetran connector (mocked for dev)."""
        
        if self.mock_mode:
            # Mock response for development
            connector_id = f"mock_{config['connector_name']}"
            response = {
                "connector_id": connector_id,
                "status": "connected",
                "schema": config.get("config", {}).get("source_name", "unknown"),
                "message": "Mock connector created successfully (dev mode)"
            }
            print(f"🔧 Mock Fivetran connector created: {connector_id}")
            return response
        
        # TODO: Implement actual Fivetran API call
        # from fivetran import Fivetran
        # client = Fivetran(api_key=FIVETRAN_API_KEY, api_secret=FIVETRAN_API_SECRET)
        # response = client.create_connector(config)
        
        raise NotImplementedError("Production Fivetran API not yet implemented")
    
    def get_connector_status(self, connector_id: str) -> Dict[str, Any]:
        """Get connector sync status (mocked for dev)."""
        
        if self.mock_mode:
            return {
                "connector_id": connector_id,
                "status": "syncing",
                "last_sync": "2024-01-01T12:00:00Z",
                "sync_frequency": "360",
                "message": "Mock status (dev mode)"
            }
        
        # TODO: Implement actual Fivetran API call
        raise NotImplementedError("Production Fivetran API not yet implemented")
    
    def list_connectors(self) -> List[Dict[str, Any]]:
        """List all configured connectors."""
        connectors = []
        
        for config_file in self.configs_dir.glob("*.json"):
            with open(config_file, 'r') as f:
                config = json.load(f)
                connectors.append({
                    "name": config["connector_name"],
                    "file": str(config_file),
                    "config": config
                })
        
        return connectors

