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

## How to Use

1. Open the 5Tran Gradio interface
2. Navigate to the "Pipeline Creator" tab
3. Paste your requirements in the text area
4. Upload one of these OpenAPI specs
5. Click "Create Pipeline"

## Creating Your Own

To create your own OpenAPI specification:

1. Use the OpenAPI 3.0 format
2. Define your endpoints under `paths`
3. Include response schemas in `components/schemas`
4. Specify authentication method in `security` and `securitySchemes`

For more information, see: https://swagger.io/specification/

