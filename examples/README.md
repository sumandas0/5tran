# Example OpenAPI Specifications

This directory contains example OpenAPI specifications for testing 5Tran pipeline automation.

## Available Examples

### 1. E-Commerce API (`ecommerce_api.json`)
A typical e-commerce platform with:
- **Orders**: Order history with items and totals
- **Customers**: Customer profiles and spending data
- **Products**: Product catalog with inventory

**Use Case**: Track sales metrics, customer lifetime value, inventory levels

**Sample Requirements**:
```
I want to sync data from our e-commerce platform including orders, customers, 
and products. Calculate monthly revenue, customer lifetime value, and 
best-selling products.
```

### 2. SaaS Metrics API (`saas_metrics_api.yaml`)
A SaaS application tracking:
- **Users**: User accounts and status
- **Subscriptions**: Subscription plans and MRR
- **Usage**: Product usage events

**Use Case**: Track MRR, churn rate, user engagement

**Sample Requirements**:
```
I want to sync our SaaS application data including users, subscriptions, and 
usage events. Calculate monthly recurring revenue (MRR), churn rate, and 
active users by plan.
```

### 3. GitHub API (`github_api.json`) 🆕
Real GitHub API integration example:
- **Repositories**: Your repos with stats
- **Issues**: Track issues across repos
- **Pull Requests**: Monitor PR activity
- **Commits**: Track commit history

**Use Case**: Developer productivity, code review metrics

**Sample Requirements**:
```
I want to sync GitHub data for my repositories including repos, issues, 
pull requests, and commits. Calculate repository activity, issue resolution 
time, PR merge time, and contributor metrics.
```

**Authentication**: GitHub Personal Access Token (Bearer)

**Run Example**:
```bash
python examples/github_example.py
```

This example demonstrates:
- Custom authentication configuration (Bearer token)
- Real API with actual GitHub token
- Complete end-to-end workflow

## How to Use

### Option 1: Complete Programmatic Example

Run the full end-to-end example:
```bash
python examples/complete_example.py
```

This demonstrates:
- Listing Fivetran groups
- Creating pipeline with auto-deployment
- Checking connector status
- Example natural language queries

### Option 2: UI Example

See `examples/ui_example.md` for complete step-by-step UI guide with screenshots and troubleshooting.

### Option 3: Quick UI Test

1. Open the 5Tran Gradio interface: `python src/ui/app.py`
2. Navigate to the "Pipeline Creator" tab
3. Paste your requirements in the text area
4. Upload one of these OpenAPI specs
5. Enable "Auto-deploy to Fivetran"
6. Enter credentials and click "Create & Deploy Pipeline"

## Creating Your Own

To create your own OpenAPI specification:

1. Use the OpenAPI 3.0 format
2. Define your endpoints under `paths`
3. Include response schemas in `components/schemas`
4. Specify authentication method in `security` and `securitySchemes`

For more information, see: https://swagger.io/specification/

