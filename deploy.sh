#!/bin/bash

set -e

echo "🚀 Deploying 5tran to Google Cloud Run"

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: PROJECT_ID environment variable is not set"
    echo "Usage: PROJECT_ID=your-gcp-project-id ./deploy.sh"
    exit 1
fi

if [ -z "$ACCESS_PASSWORD" ]; then
    echo "❌ Error: ACCESS_PASSWORD environment variable is not set"
    exit 1
fi

if [ -z "$FIVETRAN_API_SECRET_BASE64" ]; then
    echo "❌ Error: FIVETRAN_API_SECRET_BASE64 environment variable is not set"
    exit 1
fi

if [ -z "$FIRECRAWL_API_KEY" ]; then
    echo "❌ Error: FIRECRAWL_API_KEY environment variable is not set"
    exit 1
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Error: GEMINI_API_KEY environment variable is not set"
    exit 1
fi

REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-5tran}"

echo "📦 Building Docker image..."
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:latest .

echo "📤 Pushing image to Google Container Registry..."
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

echo "🌐 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --max-instances 10 \
    --set-env-vars "ACCESS_PASSWORD=$ACCESS_PASSWORD,FIVETRAN_API_SECRET_BASE64=$FIVETRAN_API_SECRET_BASE64,FIRECRAWL_API_KEY=$FIRECRAWL_API_KEY,GEMINI_API_KEY=$GEMINI_API_KEY" \
    --project $PROJECT_ID

echo "✅ Deployment complete!"
echo "🔗 Service URL:"
gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)'

