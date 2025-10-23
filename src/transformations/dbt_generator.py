"""dbt model generator for pipeline transformations."""

from pathlib import Path
from typing import Dict, Any, List
from src.config import DBT_PROJECT_DIR


class DBTGenerator:
    """Generates dbt models and project structure."""
    
    def __init__(self, project_name: str = "fivetran_pipeline"):
        """Initialize dbt generator."""
        self.project_name = project_name
        self.project_dir = DBT_PROJECT_DIR
        self.models_dir = self.project_dir / "models"
        
        # Create directory structure
        self._setup_project_structure()
    
    def _setup_project_structure(self):
        """Create dbt project directory structure."""
        # Create base directories
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        (self.models_dir / "staging").mkdir(exist_ok=True)
        (self.models_dir / "marts").mkdir(exist_ok=True)
        (self.project_dir / "macros").mkdir(exist_ok=True)
        (self.project_dir / "tests").mkdir(exist_ok=True)
    
    def initialize_project(self, project_id: str, dataset: str):
        """Initialize dbt_project.yml file."""
        dbt_project_yml = f"""name: '{self.project_name}'
version: '1.0.0'
config-version: 2

profile: '{self.project_name}'

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

target-path: "target"
clean-targets:
  - "target"
  - "dbt_packages"

models:
  {self.project_name}:
    staging:
      +materialized: view
      +schema: staging
    marts:
      +materialized: table
      +schema: marts
"""
        
        dbt_project_file = self.project_dir / "dbt_project.yml"
        with open(dbt_project_file, 'w') as f:
            f.write(dbt_project_yml)
        
        # Create profiles.yml
        profiles_yml = f"""
{self.project_name}:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: oauth
      project: {project_id}
      dataset: {dataset}
      threads: 4
      timeout_seconds: 300
      location: US
      priority: interactive
"""
        
        profiles_file = self.project_dir / "profiles.yml"
        with open(profiles_file, 'w') as f:
            f.write(profiles_yml)
        
        print(f"✓ Initialized dbt project at {self.project_dir}")
    
    def create_staging_model(
        self,
        source_name: str,
        table_name: str,
        columns: List[Dict[str, str]]
    ) -> Path:
        """Create a staging model for a source table."""
        
        model_name = f"stg_{source_name}_{table_name}"
        
        # Generate column list
        column_list = []
        for col in columns:
            col_name = col.get("name", col.get("field", "unknown"))
            column_list.append(f"        {col_name}")
        
        columns_sql = ',\n'.join(column_list)
        
        sql = f"""{{{{
    config(
        materialized='view'
    )
}}}}

with source as (
    select * from {{{{ source('{source_name}', '{table_name}') }}}}
),

renamed as (
    select
{columns_sql},
        current_timestamp() as _loaded_at
    from source
)

select * from renamed
"""
        
        # Write model file
        model_file = self.models_dir / "staging" / f"{model_name}.sql"
        with open(model_file, 'w') as f:
            f.write(sql)
        
        print(f"✓ Created staging model: {model_name}")
        return model_file
    
    def create_mart_model(
        self,
        mart_name: str,
        entities: List[str],
        metrics: List[str]
    ) -> Path:
        """Create a mart model with business metrics."""
        
        model_name = f"mart_{mart_name}"
        
        # Generate basic aggregation SQL
        sql = f"""{{{{
    config(
        materialized='table'
    )
}}}}

-- Business metrics mart for {mart_name}

with base as (
    select *
    from {{{{ ref('stg_{entities[0] if entities else "unknown"}') }}}}
),

metrics as (
    select
        count(*) as total_count,
        count(distinct id) as unique_records
    from base
)

select * from metrics
"""
        
        # Write model file
        model_file = self.models_dir / "marts" / f"{model_name}.sql"
        with open(model_file, 'w') as f:
            f.write(sql)
        
        print(f"✓ Created mart model: {model_name}")
        return model_file
    
    def create_sources_yml(
        self,
        source_name: str,
        tables: List[Dict[str, Any]]
    ):
        """Create sources.yml for dbt."""
        
        tables_yml = []
        for table in tables:
            table_name = table.get("name", "unknown")
            description = table.get("description", f"{table_name} from {source_name}")
            
            table_entry = f"""    - name: {table_name}
      description: {description}
      columns:
"""
            
            # Add columns if available
            columns = table.get("columns", [])
            for col in columns:
                col_name = col.get("name", col.get("field", "unknown"))
                col_desc = col.get("description", "")
                table_entry += f"""        - name: {col_name}
          description: {col_desc}
"""
            
            tables_yml.append(table_entry)
        
        sources_yml = f"""version: 2

sources:
  - name: {source_name}
    description: Data from {source_name}
    database: "{{{{ target.project }}}}"
    schema: "{{{{ target.dataset }}}}"
    tables:
{chr(10).join(tables_yml)}
"""
        
        # Write sources file
        sources_file = self.models_dir / "staging" / "sources.yml"
        with open(sources_file, 'w') as f:
            f.write(sources_yml)
        
        print(f"✓ Created sources.yml for {source_name}")
    
    def create_schema_yml(self, models: List[str]):
        """Create schema.yml for model documentation."""
        
        models_yml = []
        for model in models:
            models_yml.append(f"""  - name: {model}
    description: "Model: {model}"
""")
        
        schema_yml = f"""version: 2

models:
{chr(10).join(models_yml)}
"""
        
        schema_file = self.models_dir / "marts" / "schema.yml"
        with open(schema_file, 'w') as f:
            f.write(schema_yml)
        
        print(f"✓ Created schema.yml")
    
    def list_models(self) -> Dict[str, List[str]]:
        """List all generated dbt models."""
        models = {
            "staging": [],
            "marts": []
        }
        
        # List staging models
        staging_dir = self.models_dir / "staging"
        if staging_dir.exists():
            for model_file in staging_dir.glob("*.sql"):
                models["staging"].append(model_file.stem)
        
        # List mart models
        marts_dir = self.models_dir / "marts"
        if marts_dir.exists():
            for model_file in marts_dir.glob("*.sql"):
                models["marts"].append(model_file.stem)
        
        return models

