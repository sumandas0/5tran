"""Fivetran connector management and deployment."""

import json
import subprocess
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
import requests

from src.config import (
    FIVETRAN_API_KEY,
    FIVETRAN_API_SECRET,
    CONFIGS_DIR
)
from src.connectors.connector_generator import ConnectorGenerator


class FivetranManager:
    """Manages Fivetran connector SDK deployment and API operations."""
    
    FIVETRAN_API_BASE = "https://api.fivetran.com/v1"
    
    def __init__(self):
        """Initialize Fivetran manager with real API credentials."""
        if not FIVETRAN_API_KEY or not FIVETRAN_API_SECRET:
            raise ValueError(
                "Fivetran API credentials required. Set FIVETRAN_API_KEY and "
                "FIVETRAN_API_SECRET in your .env file"
            )
        
        self.api_key = FIVETRAN_API_KEY
        self.api_secret = FIVETRAN_API_SECRET
        self.configs_dir = CONFIGS_DIR / "fivetran"
        self.connectors_dir = CONFIGS_DIR / "fivetran" / "connectors"
        self.configs_dir.mkdir(parents=True, exist_ok=True)
        self.connectors_dir.mkdir(parents=True, exist_ok=True)
        
        self.generator = ConnectorGenerator()
        self.session = requests.Session()
        self.session.auth = (self.api_key, self.api_secret)
        self.session.headers.update({
            "Content-Type": "application/json"
        })
    
    def _make_api_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Fivetran API."""
        url = f"{self.FIVETRAN_API_BASE}/{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            elif method.upper() == "PATCH":
                response = self.session.patch(url, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            error_detail = e.response.text if e.response else str(e)
            raise Exception(f"Fivetran API error: {error_detail}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def generate_connector_code(
        self,
        source_name: str,
        api_url: str,
        endpoints: List[Dict[str, Any]],
        auth_config: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Generate Fivetran Connector SDK code files.
        
        Args:
            source_name: Name of the source system
            api_url: Base URL for the API
            endpoints: List of endpoint configurations with table_name, path, columns
            auth_config: Authentication configuration dict with method, header_name, header_prefix
            
        Returns:
            Dict with file paths and connector info
        """
        if auth_config is None:
            auth_config = {
                "method": "bearer",
                "header_name": "Authorization",
                "header_prefix": "Bearer"
            }
        
        connector_name = source_name.lower().replace(' ', '_').replace('-', '_')
        connector_dir = self.connectors_dir / connector_name
        
        print(f"📝 Generating Fivetran Connector SDK code for {source_name}...")
        
        # Generate connector code
        connector_code = self.generator.generate_connector(
            source_name=source_name,
            api_url=api_url,
            endpoints=endpoints,
            auth_config=auth_config
        )
        
        # Generate requirements.txt
        requirements = self.generator.generate_requirements_txt()
        
        # Generate configuration template
        configuration = self.generator.generate_configuration_json(
            api_url=api_url,
            auth_config=auth_config
        )
        
        # Save all files
        files = self.generator.save_connector_files(
            output_dir=connector_dir,
            connector_code=connector_code,
            requirements=requirements,
            configuration=configuration
        )
        
        print(f"✓ Generated connector files in: {connector_dir}")
        print(f"  - connector.py")
        print(f"  - requirements.txt")
        print(f"  - configuration.json.template")
        print(f"  - README.md")
        
        return {
            "connector_name": connector_name,
            "connector_dir": str(connector_dir),
            "files": files,
            "source_name": source_name
        }
    
    def deploy_connector(
        self,
        connector_dir: Path,
        group_id: str,
        destination_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Deploy connector using Fivetran SDK CLI.
        
        Args:
            connector_dir: Path to connector directory with connector.py
            group_id: Fivetran group ID
            destination_id: Optional destination ID
            
        Returns:
            Deployment result with connector details
        """
        if isinstance(connector_dir, str):
            connector_dir = Path(connector_dir)
        
        if not connector_dir.exists():
            raise FileNotFoundError(f"Connector directory not found: {connector_dir}")
        
        connector_file = connector_dir / "connector.py"
        if not connector_file.exists():
            raise FileNotFoundError(f"connector.py not found in {connector_dir}")
        
        print(f"🚀 Deploying connector from {connector_dir}...")
        print(f"   Group ID: {group_id}")
        
        try:
            # Change to connector directory
            import os
            original_dir = os.getcwd()
            os.chdir(connector_dir)
            
            # Run fivetran deploy command
            cmd = [
                "fivetran", "deploy",
                "--api-key", self.api_key,
                "--api-secret", self.api_secret,
                "--group-id", group_id
            ]
            
            if destination_id:
                cmd.extend(["--destination-id", destination_id])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            os.chdir(original_dir)
            
            print("✓ Connector deployed successfully!")
            print(result.stdout)
            
            # Extract connector ID from output (if available)
            connector_id = self._extract_connector_id(result.stdout)
            
            return {
                "status": "deployed",
                "connector_id": connector_id,
                "group_id": group_id,
                "message": "Connector deployed successfully",
                "output": result.stdout
            }
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Deployment failed: {e.stderr}")
            raise Exception(f"Connector deployment failed: {e.stderr}")
        except Exception as e:
            os.chdir(original_dir)
            raise Exception(f"Deployment error: {str(e)}")
    
    def _extract_connector_id(self, output: str) -> Optional[str]:
        """Extract connector ID from deployment output."""
        # Parse deployment output for connector ID
        # Format varies, so this is a best-effort extraction
        for line in output.split('\n'):
            if 'connector' in line.lower() and 'id' in line.lower():
                # Try to extract ID-like strings
                parts = line.split()
                for part in parts:
                    if len(part) > 10 and '_' in part:
                        return part
        return None
    
    def get_connector_status(self, connector_id: str) -> Dict[str, Any]:
        """
        Get connector sync status from Fivetran API.
        
        Args:
            connector_id: Fivetran connector ID
            
        Returns:
            Connector status information
        """
        print(f"📊 Fetching status for connector: {connector_id}")
        
        try:
            response = self._make_api_request("GET", f"connectors/{connector_id}")
            data = response.get("data", {})
            
            return {
                "connector_id": connector_id,
                "status": data.get("status", {}).get("setup_state", "unknown"),
                "sync_state": data.get("status", {}).get("sync_state", "unknown"),
                "last_sync": data.get("succeeded_at"),
                "failed_at": data.get("failed_at"),
                "sync_frequency": data.get("sync_frequency"),
                "paused": data.get("paused", False),
                "schema": data.get("schema"),
                "service": data.get("service")
            }
        except Exception as e:
            print(f"❌ Failed to get connector status: {e}")
            raise
    
    def trigger_sync(self, connector_id: str) -> Dict[str, Any]:
        """
        Trigger a manual sync for a connector.
        
        Args:
            connector_id: Fivetran connector ID
            
        Returns:
            Sync trigger result
        """
        print(f"▶️  Triggering sync for connector: {connector_id}")
        
        try:
            response = self._make_api_request(
                "POST",
                f"connectors/{connector_id}/force"
            )
            
            print("✓ Sync triggered successfully")
            return {
                "status": "success",
                "message": "Sync triggered",
                "data": response.get("data", {})
            }
        except Exception as e:
            print(f"❌ Failed to trigger sync: {e}")
            raise
    
    def list_connectors(self, group_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List connectors from Fivetran API.
        
        Args:
            group_id: Optional group ID to filter connectors
            
        Returns:
            List of connector information
        """
        print("📋 Fetching connectors from Fivetran...")
        
        try:
            endpoint = "connectors"
            if group_id:
                endpoint = f"groups/{group_id}/connectors"
            
            response = self._make_api_request("GET", endpoint)
            connectors_data = response.get("data", {}).get("items", [])
            
            connectors = []
            for conn in connectors_data:
                connectors.append({
                    "id": conn.get("id"),
                    "name": conn.get("schema"),
                    "service": conn.get("service"),
                    "status": conn.get("status", {}).get("setup_state"),
                    "sync_state": conn.get("status", {}).get("sync_state"),
                    "connected_by": conn.get("connected_by"),
                    "created_at": conn.get("created_at"),
                    "group_id": conn.get("group_id")
                })
            
            print(f"✓ Found {len(connectors)} connector(s)")
            return connectors
            
        except Exception as e:
            print(f"⚠️  Failed to list connectors: {e}")
            # Fallback to local connector directories
            return self._list_local_connectors()
    
    def _list_local_connectors(self) -> List[Dict[str, Any]]:
        """List locally generated connectors as fallback."""
        connectors = []
        
        if not self.connectors_dir.exists():
            return connectors
        
        for connector_dir in self.connectors_dir.iterdir():
            if connector_dir.is_dir() and (connector_dir / "connector.py").exists():
                connectors.append({
                    "name": connector_dir.name,
                    "path": str(connector_dir),
                    "status": "local",
                    "type": "connector_sdk"
                })
        
        return connectors
    
    def list_groups(self) -> List[Dict[str, Any]]:
        """
        List all Fivetran groups (destinations).
        
        Returns:
            List of group information
        """
        print("📋 Fetching Fivetran groups...")
        
        try:
            response = self._make_api_request("GET", "groups")
            groups_data = response.get("data", {}).get("items", [])
            
            groups = []
            for group in groups_data:
                groups.append({
                    "id": group.get("id"),
                    "name": group.get("name"),
                    "created_at": group.get("created_at")
                })
            
            print(f"✓ Found {len(groups)} group(s)")
            return groups
            
        except Exception as e:
            print(f"❌ Failed to list groups: {e}")
            raise
    
    def create_group(self, group_name: str) -> Dict[str, Any]:
        """
        Create a new Fivetran group.
        
        Args:
            group_name: Name for the new group
            
        Returns:
            Created group information
        """
        print(f"➕ Creating Fivetran group: {group_name}")
        
        try:
            data = {"name": group_name}
            response = self._make_api_request("POST", "groups", data)
            
            group_data = response.get("data", {})
            print(f"✓ Group created: {group_data.get('id')}")
            
            return {
                "id": group_data.get("id"),
                "name": group_data.get("name"),
                "created_at": group_data.get("created_at")
            }
            
        except Exception as e:
            print(f"❌ Failed to create group: {e}")
            raise

