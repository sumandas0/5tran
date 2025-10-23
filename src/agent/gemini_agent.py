"""Gemini API integration for pipeline automation."""

import json
import google.generativeai as genai
from typing import Dict, Any, Optional
from src.config import GEMINI_API_KEY, GEMINI_MODEL_FAST, GEMINI_TEMPERATURE


class GeminiAgent:
    """Agent for interacting with Gemini API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini agent."""
        self.api_key = api_key or GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("Gemini API key not found. Set GEMINI_API_KEY in .env")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(GEMINI_MODEL_FAST)
    
    def analyze_requirements(self, user_description: str, openapi_spec: Optional[str] = None) -> Dict[str, Any]:
        """Analyze user requirements and extract pipeline details."""
        openapi_section = ""
        if openapi_spec:
            openapi_section = f"OpenAPI Specification:\n{openapi_spec[:2000]}..."
        
        prompt = f"""You are a data pipeline architect. Analyze the following requirements and extract structured information.

User Requirements:
{user_description}

{openapi_section}

Extract and return a JSON object with:
1. source_type: Type of data source (e.g., "rest_api", "database", "saas")
2. source_name: Name of the source system (e.g., "Stripe", "Shopify", "Custom API")
3. endpoints: List of API endpoints to sync (if applicable)
4. entities: Main data entities to track (e.g., ["orders", "customers", "products"])
5. business_metrics: Key metrics to calculate (e.g., ["revenue", "customer_count", "avg_order_value"])
6. transformations: Suggested transformations needed
7. use_case: Brief description of the use case

Return ONLY valid JSON, no additional text."""

        response = self.model.generate_content(
            prompt,
            generation_config={
                "temperature": GEMINI_TEMPERATURE,
                "response_mime_type": "application/json"
            }
        )
        
        return json.loads(response.text)
    
    def generate_sql_from_nl(self, natural_language_query: str, schema_context: str) -> str:
        """Generate SQL from natural language query."""
        prompt = f"""You are a SQL expert. Convert the natural language query to valid BigQuery SQL.

Available Tables and Schema:
{schema_context}

Natural Language Query:
{natural_language_query}

Generate a valid BigQuery SQL query. Return ONLY the SQL query, no explanations or markdown."""

        response = self.model.generate_content(
            prompt,
            generation_config={
                "temperature": GEMINI_TEMPERATURE
            }
        )
        
        sql = response.text.strip()
        # Clean up markdown code blocks if present
        if sql.startswith("```"):
            sql = sql.split("```")[1]
            if sql.startswith("sql"):
                sql = sql[3:]
            sql = sql.strip()
        
        return sql
    
    def suggest_dbt_models(self, entities: list, business_metrics: list) -> Dict[str, Any]:
        """Suggest dbt model structure based on entities and metrics."""
        prompt = f"""You are a dbt expert. Suggest a dbt model structure for the following:

Entities: {', '.join(entities)}
Business Metrics: {', '.join(business_metrics)}

Return a JSON object with:
1. staging_models: List of staging model names (one per entity)
2. intermediate_models: List of intermediate models for joining/transforming
3. mart_models: List of final mart models for business metrics
4. model_descriptions: Brief description for each model

Return ONLY valid JSON."""

        response = self.model.generate_content(
            prompt,
            generation_config={
                "temperature": GEMINI_TEMPERATURE,
                "response_mime_type": "application/json"
            }
        )
        
        return json.loads(response.text)
    
    def extract_schema_from_openapi(self, openapi_spec: str, endpoint: str) -> Dict[str, Any]:
        """Extract schema information from OpenAPI spec for a specific endpoint."""
        prompt = f"""Extract the response schema for the following endpoint from this OpenAPI specification.

OpenAPI Spec:
{openapi_spec[:3000]}

Endpoint: {endpoint}

Return a JSON object with:
1. fields: List of field objects with "name", "type", and "description"
2. nested_objects: Any nested objects that should be flattened or structured
3. suggested_table_name: Suggested BigQuery table name

Return ONLY valid JSON."""

        response = self.model.generate_content(
            prompt,
            generation_config={
                "temperature": GEMINI_TEMPERATURE,
                "response_mime_type": "application/json"
            }
        )
        
        return json.loads(response.text)

