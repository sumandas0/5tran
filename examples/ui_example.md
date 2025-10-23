# Complete UI Example: E-Commerce Pipeline

This guide shows exactly how to use the 5Tran UI to create and deploy a complete data pipeline.

## Step-by-Step Guide

### 1. Start the UI

```bash
cd /Users/suman/projects/5tran
python src/ui/app.py
```

The UI will open at: http://localhost:7860

### 2. Prepare Your Credentials

Before starting, gather:

1. **Fivetran Group ID**
   ```bash
   # Run this in a terminal
   python scripts/list_fivetran_groups.py
   ```
   Copy the Group ID (looks like: `abc123_def456`)

2. **Source API Credentials**
   - API Base URL (e.g., `https://api.yourcompany.com/v1`)
   - API Key or Bearer Token
   - Authentication type (usually `bearer`)

### 3. Navigate to Pipeline Creator Tab

In the UI, click on the **"🔧 Pipeline Creator"** tab.

### 4. Enter Requirements

In the **Requirements** text box, paste:

```
I want to sync data from our e-commerce platform including:
- Orders: Complete order history with line items
- Customers: Customer profiles with contact info and spending
- Products: Product catalog with inventory and pricing

Calculate these business metrics:
- Monthly revenue and growth rate
- Customer lifetime value (CLV)
- Top 10 products by revenue
- Average order value
- Customer retention and churn rates
```

### 5. Upload OpenAPI Spec (Optional)

Click **"OpenAPI Specification"** file upload:
- Upload: `examples/ecommerce_api.json`
- This helps extract exact API structure

### 6. Configure Auto-Deploy

✅ Check **"Auto-deploy to Fivetran"**

Fill in the fields that appear:

**Fivetran Group ID:**
```
your_group_id_here  (from step 2)
```

**API Base URL:**
```
https://api.ecommerce-example.com/v1
```

**API Key / Token:**
```
your_api_key_here
```

**Auth Type:**
```
bearer  (select from dropdown)
```

### 7. Create & Deploy

Click the big **"Create & Deploy Pipeline"** button.

You'll see progress indicators:
1. ⏳ Analyzing requirements...
2. ⏳ Parsing specifications...
3. ⏳ Creating pipeline...
4. ⏳ Generating artifacts...
5. ✅ Pipeline created!

### 8. Review Results

The UI will display:

```
✅ Pipeline Created Successfully!

Source: E-Commerce API
Type: rest_api

📊 Entities
orders, customers, products

📈 Business Metrics
monthly_revenue, customer_lifetime_value, avg_order_value, retention_rate

🔧 Created Components

Fivetran Connector:
- Name: e_commerce_api_connector
- Directory: configs/fivetran/connectors/e_commerce_api
- ✅ DEPLOYED to Fivetran
- Connector ID: connector_abc123
- Status: Syncing data to your warehouse!

dbt Models:
- Staging: stg_ecommerce_orders, stg_ecommerce_customers, stg_ecommerce_products
- Marts: mart_ecommerce_metrics

BigQuery:
- Dataset: dev_pipeline_test
- Tables: 3 tables created

📁 Files Created
7 files generated in project directory
```

### 9. Monitor Sync Progress

Go to your [Fivetran Dashboard](https://fivetran.com/dashboard) to see the connector syncing.

### 10. Query Your Data

Switch to the **"💬 SQL Chat"** tab in the UI.

Try these natural language queries:

**Query 1:** "What is our total revenue this month?"

Expected Output:
```sql
SELECT 
  SUM(total_amount) as total_revenue
FROM `dev_pipeline_test.raw_ecommerce_orders`
WHERE DATE_TRUNC(created_at, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```

**Query 2:** "Show me the top 10 customers by lifetime value"

Expected Output:
```sql
SELECT 
  customer_id,
  name,
  email,
  total_spent as lifetime_value
FROM `dev_pipeline_test.raw_ecommerce_customers`
ORDER BY total_spent DESC
LIMIT 10
```

**Query 3:** "What are our best-selling products?"

Expected Output:
```sql
SELECT 
  p.name,
  COUNT(DISTINCT o.id) as order_count,
  SUM(oi.quantity) as units_sold,
  SUM(oi.price * oi.quantity) as total_revenue
FROM `dev_pipeline_test.raw_ecommerce_orders` o,
  UNNEST(o.items) as oi
JOIN `dev_pipeline_test.raw_ecommerce_products` p ON p.id = oi.product_id
GROUP BY p.name
ORDER BY total_revenue DESC
LIMIT 10
```

Click **"Generate & Execute"** to run the query and see results.

### 11. View Pipeline Status

Switch to the **"📊 Pipeline Status"** tab.

Click **"Refresh Status"** to see:
- Active connectors and sync status
- Generated dbt models
- Created BigQuery tables

## What Happened Behind the Scenes?

1. **Gemini AI Analysis**
   - Analyzed your requirements
   - Extracted entities, metrics, transformations

2. **OpenAPI Parsing**
   - Parsed API endpoints
   - Extracted schema definitions
   - Identified authentication

3. **Connector Generation**
   - Created `connector.py` with Fivetran SDK
   - Implemented pagination, auth, error handling
   - Generated `requirements.txt`

4. **Automatic Deployment**
   - Created `configuration.json` with API credentials
   - Deployed to Fivetran using SDK CLI
   - Started initial sync

5. **BigQuery Setup**
   - Created dataset
   - Generated table schemas
   - Prepared for incoming data

6. **dbt Models**
   - Created staging models (one per table)
   - Created mart model with business metrics
   - Generated documentation

## Troubleshooting

### "Auto-deploy enabled but missing required fields"

✅ **Fix:** Make sure all fields are filled:
- Fivetran Group ID
- API Base URL
- API Key

### "Deployment Failed: Invalid API credentials"

✅ **Fix:** Check your Fivetran API key and secret in `.env`:
```bash
FIVETRAN_API_KEY=your_key
FIVETRAN_API_SECRET=your_secret
```

### "Source API connection failed"

✅ **Fix:** 
- Verify source API URL is correct
- Test API key works: `curl -H "Authorization: Bearer YOUR_KEY" YOUR_API_URL/orders`
- Check firewall/IP restrictions

### "No groups found"

✅ **Fix:** Create a Fivetran group:
```bash
python scripts/create_fivetran_group.py --name "Production DW"
```

## Generated File Structure

After creation, you'll have:

```
configs/fivetran/connectors/e_commerce_api/
├── connector.py              # Your deployed connector
├── requirements.txt          # Python dependencies
├── configuration.json        # API credentials (gitignored)
└── README.md                 # Connector docs

dbt_project/models/
├── staging/
│   ├── stg_ecommerce_orders.sql
│   ├── stg_ecommerce_customers.sql
│   └── stg_ecommerce_products.sql
├── marts/
│   └── mart_ecommerce_metrics.sql
└── sources.yml
```

## Next Steps

1. **Monitor Data Sync**
   - Check Fivetran dashboard for sync progress
   - Verify data arrives in BigQuery

2. **Run dbt Transformations**
   ```bash
   cd dbt_project
   dbt run
   ```

3. **Build Dashboards**
   - Connect Looker/Tableau/Metabase to BigQuery
   - Use mart tables for visualizations

4. **Add More Sources**
   - Repeat the process for other APIs
   - Use different group IDs for different projects

## Advanced: Programmatic Usage

If you prefer Python over UI:

```python
from src.orchestrator import PipelineOrchestrator

orchestrator = PipelineOrchestrator()

result = orchestrator.create_pipeline(
    requirements="Your requirements here...",
    openapi_spec=open('spec.json').read(),
    auto_deploy=True,
    fivetran_group_id="your_group_id",
    source_api_credentials={
        "api_url": "https://api.example.com",
        "api_key": "your_key",
        "auth_type": "bearer"
    }
)

print(f"Deployed! Connector ID: {result['fivetran']['connector_id']}")
```

## Resources

- [Fivetran Dashboard](https://fivetran.com/dashboard)
- [Fivetran Connector SDK Docs](https://fivetran.com/docs/connector-sdk)
- [BigQuery Console](https://console.cloud.google.com/bigquery)
- [dbt Documentation](https://docs.getdbt.com/)

