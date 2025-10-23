"""OpenAPI specification parser."""

import json
import yaml
from typing import Dict, Any, List, Optional


class OpenAPIParser:
    """Parse OpenAPI/Swagger specifications."""
    
    def __init__(self, spec_content: str, spec_format: str = "auto"):
        """Initialize parser with OpenAPI spec content."""
        self.spec_format = spec_format
        self.spec = self._parse_spec(spec_content, spec_format)
    
    def _parse_spec(self, content: str, format_type: str) -> Dict[str, Any]:
        """Parse OpenAPI spec from JSON or YAML."""
        try:
            if format_type == "json" or (format_type == "auto" and content.strip().startswith("{")):
                return json.loads(content)
            else:
                return yaml.safe_load(content)
        except Exception as e:
            raise ValueError(f"Failed to parse OpenAPI spec: {str(e)}")
    
    def get_base_url(self) -> str:
        """Extract base URL from spec."""
        if "servers" in self.spec and self.spec["servers"]:
            return self.spec["servers"][0].get("url", "")
        return ""
    
    def get_endpoints(self) -> List[str]:
        """Extract all API endpoints."""
        endpoints = []
        paths = self.spec.get("paths", {})
        
        for path, methods in paths.items():
            for method in methods.keys():
                if method.lower() in ["get", "post"]:
                    endpoints.append(path)
                    break
        
        return endpoints
    
    def get_endpoint_schema(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Get response schema for an endpoint."""
        paths = self.spec.get("paths", {})
        
        if endpoint not in paths:
            return None
        
        # Look for GET method first
        for method in ["get", "post"]:
            if method not in paths[endpoint]:
                continue
            
            responses = paths[endpoint][method].get("responses", {})
            
            # Look for successful response (200, 201)
            for status_code in ["200", "201"]:
                if status_code in responses:
                    content = responses[status_code].get("content", {})
                    
                    # Get JSON schema
                    if "application/json" in content:
                        schema = content["application/json"].get("schema", {})
                        return self._resolve_schema(schema)
        
        return None
    
    def _resolve_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve schema references."""
        # Handle $ref
        if "$ref" in schema:
            ref_path = schema["$ref"].split("/")
            ref_schema = self.spec
            
            for part in ref_path:
                if part == "#":
                    continue
                ref_schema = ref_schema.get(part, {})
            
            return ref_schema
        
        return schema
    
    def get_auth_type(self) -> str:
        """Determine authentication type."""
        security_schemes = self.spec.get("components", {}).get("securitySchemes", {})
        
        if not security_schemes:
            return "none"
        
        # Get first security scheme
        scheme = list(security_schemes.values())[0]
        scheme_type = scheme.get("type", "").lower()
        
        if scheme_type == "http":
            return scheme.get("scheme", "bearer")
        elif scheme_type == "apikey":
            return "api_key"
        elif scheme_type == "oauth2":
            return "oauth2"
        
        return "bearer_token"
    
    def extract_entities(self) -> List[str]:
        """Extract main entity names from endpoints."""
        entities = set()
        
        for endpoint in self.get_endpoints():
            # Simple heuristic: extract resource name from path
            parts = endpoint.strip("/").split("/")
            if parts:
                # Take the first path segment as entity name
                entity = parts[0].lower()
                entities.add(entity)
        
        return list(entities)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the API."""
        return {
            "title": self.spec.get("info", {}).get("title", "Unknown API"),
            "version": self.spec.get("info", {}).get("version", "1.0.0"),
            "description": self.spec.get("info", {}).get("description", ""),
            "base_url": self.get_base_url(),
            "endpoints": self.get_endpoints(),
            "entities": self.extract_entities(),
            "auth_type": self.get_auth_type()
        }

