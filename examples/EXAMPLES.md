# 5tran Examples

This directory contains example OpenAPI specifications to help you get started with 5tran.

## Available Examples

### 1. GitHub API (`github_api.yaml`)

Simplified GitHub API specification for syncing repository data.

**Entities:**
- Repositories
- Issues
- Pull Requests

**Usage:**
```bash
5tran generate pipeline \
  "GitHub API to BigQuery" \
  --spec examples/github_api.yaml \
  --output ./github-pipeline \
  --project my-gcp-project \
  --dataset github_data
```

**Use Cases:**
- Track repository metrics
- Analyze issue resolution times
- Monitor pull request activity
- Build engineering dashboards

---

### 2. E-commerce API (`ecommerce_api.json`)

Sample e-commerce REST API specification.

**Entities:**
- Orders
- Customers
- Products
- Payments

**Usage:**
```bash
5tran generate pipeline \
  "E-commerce API to BigQuery" \
  --spec examples/ecommerce_api.json \
  --output ./ecommerce-pipeline \
  --project my-gcp-project \
  --dataset ecommerce_data
```

**Use Cases:**
- Revenue analytics
- Customer lifetime value
- Product performance tracking
- Inventory management

---

### 3. SaaS Metrics API (`saas_metrics_api.yaml`)

SaaS application metrics API.

**Entities:**
- Users
- Subscriptions
- Usage Events
- Billing

**Usage:**
```bash
5tran generate pipeline \
  "SaaS Metrics to BigQuery" \
  --spec examples/saas_metrics_api.yaml \
  --output ./saas-pipeline \
  --project my-gcp-project \
  --dataset saas_metrics
```

**Use Cases:**
- MRR/ARR tracking
- Churn analysis
- Usage-based billing
- Customer health scores

---

## Creating Your Own Spec

To use 5tran with your own API:

1. **Get or create an OpenAPI spec** (3.0+)
   - Export from your API framework (FastAPI, Flask-RESTX, etc.)
   - Use tools like Swagger Editor
   - Convert Postman collections

2. **Ensure it includes:**
   - Base URL (`servers` section)
   - Authentication scheme (`securitySchemes`)
   - Endpoint definitions with response schemas
   - Data models with proper types

3. **Validate the spec:**
   ```bash
   # Using swagger-cli
   npx @apidevtools/swagger-cli validate your-api.yaml
   
   # Using redocly
   npx @redocly/cli lint your-api.yaml
   ```

4. **Generate pipeline:**
   ```bash
   5tran generate pipeline "Your API to BigQuery" --spec your-api.yaml
   ```

---

## Testing Examples

### Test with GitHub API

```bash
# Generate
5tran generate pipeline \
  "GitHub to BQ" \
  --spec examples/github_api.yaml \
  --output ./test-github

# Inspect generated files
ls -la test-github/
cat test-github/connector/connector.py
cat test-github/.5tran.yml

# Test connector locally (requires GitHub token)
cd test-github/connector
# Edit configuration.json to add your token
python test_connector.py
```

### Customize and Deploy

```bash
# 1. Review and customize
vim test-github/connector/connector.py
vim test-github/dbt/models/staging/stg_issues.sql

# 2. Deploy
cd test-github
export FIVETRAN_API_KEY="your_key"
export FIVETRAN_API_SECRET="your_secret"
5tran deploy pipeline

# 3. Monitor
5tran status check
```

---

## Example dbt Models Generated

### Staging Model
```sql
-- dbt/models/staging/stg_github_issues.sql

{{ config(materialized='view') }}

with source as (
    select * from {{ source('github', 'issues') }}
),

renamed as (
    select
        id,
        number,
        title,
        state,
        created_at,
        updated_at,
        closed_at,
        current_timestamp() as _loaded_at
    from source
)

select * from renamed
```

### Mart Model
```sql
-- dbt/models/marts/mart_github_metrics.sql

{{ config(materialized='table') }}

with issues as (
    select * from {{ ref('stg_github_issues') }}
),

metrics as (
    select
        count(*) as total_issues,
        count(distinct case when state = 'open' then id end) as open_issues,
        count(distinct case when state = 'closed' then id end) as closed_issues,
        avg(timestamp_diff(closed_at, created_at, day)) as avg_resolution_days
    from issues
)

select * from metrics
```

---

## Tips

1. **Start Simple** - Begin with a few endpoints, expand later
2. **Test Locally** - Use `test_connector.py` before deploying
3. **Customize** - Generated code is a starting point
4. **Iterate** - Update specs and regenerate as your API evolves
5. **Monitor** - Use `5tran status` to track sync health

---

## Need Help?

- Review [CLI_USAGE.md](../CLI_USAGE.md) for detailed commands
- Check [README.md](../README.md) for architecture details
- Validate your OpenAPI spec before generating
- Test connectors locally before deploying

