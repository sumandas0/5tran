# Quick Start Guide - 5tran Containerized

## Local Testing

### 1. Build the Docker image
```bash
docker build -t 5tran:local .
```

### 2. Run locally with environment variables
```bash
docker run -p 8080:8080 \
  -e PORT=8080 \
  -e FIVETRAN_API_SECRET_BASE64="your_key_here" \
  -e FIRECRAWL_API_KEY="your_key_here" \
  -e GEMINI_API_KEY="your_key_here" \
  5tran:local
```

### 3. Access the app
Open your browser to: http://localhost:8080

## Deploy to Google Cloud Run

### Option 1: Quick Deploy Script
```bash
export PROJECT_ID="your-gcp-project-id"
export FIVETRAN_API_SECRET_BASE64="your_key"
export FIRECRAWL_API_KEY="your_key"
export GEMINI_API_KEY="your_key"

chmod +x deploy.sh
./deploy.sh
```

### Option 2: Manual Deployment
```bash
# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Build and push
docker build -t gcr.io/YOUR_PROJECT_ID/5tran:latest .
docker push gcr.io/YOUR_PROJECT_ID/5tran:latest

# Deploy
gcloud run deploy 5tran \
  --image gcr.io/YOUR_PROJECT_ID/5tran:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --set-env-vars "FIVETRAN_API_SECRET_BASE64=xxx,FIRECRAWL_API_KEY=xxx,GEMINI_API_KEY=xxx"
```

### Option 3: Cloud Build (CI/CD)
```bash
gcloud builds submit --config cloudbuild.yaml
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FIVETRAN_API_SECRET_BASE64` | Yes | Base64-encoded Fivetran API key:secret |
| `FIRECRAWL_API_KEY` | Yes | Firecrawl API key for web scraping |
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `PORT` | No | Server port (auto-set by Cloud Run) |

## Verify Deployment

```bash
# Get service URL
gcloud run services describe 5tran \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'

# View logs
gcloud run services logs read 5tran --region us-central1 --limit 100
```

## Troubleshooting

### Container fails to start
```bash
# Check logs
docker logs CONTAINER_ID

# Run interactively
docker run -it --entrypoint /bin/bash 5tran:local
```

### Cloud Run deployment fails
```bash
# Check Cloud Run logs
gcloud run services logs read 5tran --limit 100

# Verify environment variables
gcloud run services describe 5tran \
  --format="value(spec.template.spec.containers[0].env)"
```

### Out of memory
```bash
# Increase memory allocation
gcloud run services update 5tran --memory 4Gi
```

## Clean Up

```bash
# Delete Cloud Run service
gcloud run services delete 5tran --region us-central1

# Delete container images
gcloud container images delete gcr.io/YOUR_PROJECT_ID/5tran:latest
```

## More Information

- Full deployment guide: [DEPLOYMENT.md](DEPLOYMENT.md)
- Project README: [README.md](README.md)

