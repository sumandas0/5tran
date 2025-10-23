"""Fivetran REST API client."""

import requests
import base64
import time
from typing import Dict, Any, Optional, List
from pathlib import Path


class FivetranAPIClient:
    """Client for Fivetran REST API."""
    
    BASE_URL = "https://api.fivetran.com/v1"
    
    def __init__(self, api_key: str, api_secret: str):
        """Initialize Fivetran API client."""
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        
        # Setup basic auth
        auth_string = f"{api_key}:{api_secret}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        self.session.headers.update({
            'Authorization': f'Basic {encoded_auth}',
            'Content-Type': 'application/json'
        })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make API request with error handling."""
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"Fivetran API error: {e}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg = f"Fivetran API error: {error_detail}"
                except:
                    error_msg = f"Fivetran API error: {e.response.text}"
            raise Exception(error_msg)
    
    # Group Management
    
    def create_group(self, name: str) -> Dict[str, Any]:
        """Create a new group."""
        data = {"name": name}
        return self._request("POST", "/groups", json=data)
    
    def list_groups(self) -> List[Dict[str, Any]]:
        """List all groups."""
        response = self._request("GET", "/groups")
        return response.get("data", {}).get("items", [])
    
    def get_group(self, group_id: str) -> Dict[str, Any]:
        """Get group details."""
        response = self._request("GET", f"/groups/{group_id}")
        return response.get("data", {})
    
    # Destination Management
    
    def create_destination(
        self,
        group_id: str,
        service: str,  # e.g., "big_query"
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new destination."""
        data = {
            "group_id": group_id,
            "service": service,
            "config": config
        }
        return self._request("POST", "/destinations", json=data)
    
    def list_destinations(self, group_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List destinations."""
        endpoint = f"/groups/{group_id}/destinations" if group_id else "/destinations"
        response = self._request("GET", endpoint)
        return response.get("data", {}).get("items", [])
    
    def get_destination(self, destination_id: str) -> Dict[str, Any]:
        """Get destination details."""
        response = self._request("GET", f"/destinations/{destination_id}")
        return response.get("data", {})
    
    # Connector Management
    
    def create_connector(
        self,
        group_id: str,
        service: str,  # e.g., "connector_sdk"
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new connector."""
        data = {
            "group_id": group_id,
            "service": service,
            "config": config
        }
        return self._request("POST", "/connectors", json=data)
    
    def update_connector(
        self,
        connector_id: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update connector configuration."""
        return self._request("PATCH", f"/connectors/{connector_id}", json=config)
    
    def get_connector(self, connector_id: str) -> Dict[str, Any]:
        """Get connector details."""
        response = self._request("GET", f"/connectors/{connector_id}")
        return response.get("data", {})
    
    def list_connectors(self, group_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List connectors."""
        endpoint = f"/groups/{group_id}/connectors" if group_id else "/connectors"
        response = self._request("GET", endpoint)
        return response.get("data", {}).get("items", [])
    
    def sync_connector(self, connector_id: str) -> Dict[str, Any]:
        """Trigger a connector sync."""
        return self._request("POST", f"/connectors/{connector_id}/sync")
    
    def test_connector(self, connector_id: str) -> Dict[str, Any]:
        """Test connector setup."""
        return self._request("POST", f"/connectors/{connector_id}/test")
    
    def get_connector_state(self, connector_id: str) -> Dict[str, Any]:
        """Get connector sync state."""
        response = self._request("GET", f"/connectors/{connector_id}/state")
        return response.get("data", {})
    
    # Connector SDK specific
    
    def upload_connector_sdk(
        self,
        connector_id: str,
        connector_dir: Path
    ) -> Dict[str, Any]:
        """
        Upload connector SDK files.
        
        Note: This is a simplified version. Actual implementation may require
        packaging and using Fivetran's SDK upload endpoints.
        """
        # This would typically involve:
        # 1. Package connector files into a zip
        # 2. Upload to Fivetran's SDK endpoint
        # 3. Register the connector
        
        raise NotImplementedError(
            "Connector SDK upload requires additional packaging. "
            "Please refer to Fivetran SDK documentation for manual deployment."
        )
    
    # Transformations (dbt)
    
    def create_transformation(
        self,
        connector_id: str,
        dbt_project_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a dbt transformation for a connector."""
        data = {
            "connector_id": connector_id,
            "config": dbt_project_config
        }
        return self._request("POST", "/transformations", json=data)
    
    def trigger_transformation(self, transformation_id: str) -> Dict[str, Any]:
        """Trigger a transformation run."""
        return self._request("POST", f"/transformations/{transformation_id}/run")
    
    # Monitoring
    
    def wait_for_connector_setup(
        self,
        connector_id: str,
        timeout: int = 300,
        poll_interval: int = 10
    ) -> Dict[str, Any]:
        """
        Wait for connector to complete setup.
        
        Args:
            connector_id: ID of connector
            timeout: Maximum seconds to wait
            poll_interval: Seconds between status checks
            
        Returns:
            Final connector state
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            connector = self.get_connector(connector_id)
            status = connector.get("status", {}).get("setup_state")
            
            if status == "connected":
                return connector
            elif status in ["broken", "incomplete"]:
                raise Exception(f"Connector setup failed: {status}")
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Connector setup timed out after {timeout}s")
    
    def get_sync_status(self, connector_id: str) -> Dict[str, Any]:
        """Get current sync status of connector."""
        connector = self.get_connector(connector_id)
        return {
            "connector_id": connector_id,
            "setup_state": connector.get("status", {}).get("setup_state"),
            "sync_state": connector.get("status", {}).get("sync_state"),
            "update_state": connector.get("status", {}).get("update_state"),
            "is_historical_sync": connector.get("status", {}).get("is_historical_sync"),
            "succeeded_at": connector.get("succeeded_at"),
            "failed_at": connector.get("failed_at")
        }

