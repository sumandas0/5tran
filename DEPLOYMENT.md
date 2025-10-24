# 5tran Cloud Run Deployment Guide

This guide covers deploying the 5tran Gradio application to Google Cloud Run.

## Prerequisites

1. **Google Cloud Project** with billing enabled
2. **gcloud CLI** installed and configured
3. **Docker** installed locally
4. **Required API Keys**:
   - `FIVETRAN_API_SECRET_BASE64`
   - `FIRECRAWL_API_KEY`
   - `GEMINI_API_KEY`

## Initial Setup

### 1. Install gcloud CLI

```bash
# macOS
brew install google-cloud-sdk

# Linux/Windows - follow: https://cloud.google.com/sdk/docs/install
```

### 2. Authenticate and Set Project

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud auth configure-docker
```

### 3. Enable Required APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

## Deployment Methods

### Method 1: Quick Deploy Script (Recommended)

```bash
# Set environment variables
export PROJECT_ID="your-gcp-project-id"
export FIVETRAN_API_SECRET_BASE64="your_base64_key"
export FIRECRAWL_API_KEY="your_firecrawl_key"
export GEMINI_API_KEY="your_gemini_key"

# Optional: customize region and service name
export REGION="us-central1"
export SERVICE_NAME="5tran"

# Make script executable and run
chmod +x deploy.sh
./deploy.sh
```

### Method 2: Manual Deployment

```bash
# 1. Build the Docker image
docker build -t gcr.io/YOUR_PROJECT_ID/5tran:latest .

# 2. Push to Google Container Registry
docker push gcr.io/YOUR_PROJECT_ID/5tran:latest

# 3. Deploy to Cloud Run
gcloud run deploy 5tran \
    --image gcr.io/YOUR_PROJECT_ID/5tran:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --max-instances 10 \
    --set-env-vars "FIVETRAN_API_SECRET_BASE64=YOUR_KEY,FIRECRAWL_API_KEY=YOUR_KEY,GEMINI_API_KEY=YOUR_KEY"
```

### Method 3: Cloud Build (CI/CD)

```bash
# Submit build to Cloud Build (uses cloudbuild.yaml)
gcloud builds submit --config cloudbuild.yaml

# Or connect to GitHub for automatic deployments
gcloud builds triggers create github \
    --repo-name=5tran \
    --repo-owner=YOUR_GITHUB_USERNAME \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml
```

## Configuration

### Environment Variables

The application requires three environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `FIVETRAN_API_SECRET_BASE64` | Base64-encoded Fivetran API credentials | Yes |
| `FIRECRAWL_API_KEY` | Firecrawl API key for web scraping | Yes |
| `GEMINI_API_KEY` | Google Gemini API key for AI generation | Yes |
| `PORT` | Server port (auto-set by Cloud Run) | No |

### Resource Configuration

Current settings in `cloudbuild.yaml` and `deploy.sh`:

- **Memory**: 2 GiB
- **CPU**: 2 vCPU
- **Timeout**: 3600 seconds (1 hour)
- **Max Instances**: 10
- **Min Instances**: 0 (scales to zero)

Adjust these based on your needs:

```bash
gcloud run services update 5tran \
    --memory 4Gi \
    --cpu 4 \
    --max-instances 20
```

## Verification

After deployment:

```bash
# Get service URL
gcloud run services describe 5tran \
    --platform managed \
    --region us-central1 \
    --format 'value(status.url)'

# View logs
gcloud run services logs read 5tran --region us-central1

# Test the endpoint
curl https://YOUR_SERVICE_URL
```

## Security Best Practices

### 1. Use Secret Manager (Recommended)

Instead of passing env vars directly, use Google Secret Manager:

```bash
# Create secrets
echo -n "your_key" | gcloud secrets create fivetran-api-secret --data-file=-
echo -n "your_key" | gcloud secrets create firecrawl-api-key --data-file=-
echo -n "your_key" | gcloud secrets create gemini-api-key --data-file=-

# Deploy with secrets
gcloud run deploy 5tran \
    --image gcr.io/YOUR_PROJECT_ID/5tran:latest \
    --set-secrets="FIVETRAN_API_SECRET_BASE64=fivetran-api-secret:latest" \
    --set-secrets="FIRECRAWL_API_KEY=firecrawl-api-key:latest" \
    --set-secrets="GEMINI_API_KEY=gemini-api-key:latest"
```

### 2. Restrict Access

```bash
# Require authentication
gcloud run services update 5tran --no-allow-unauthenticated

# Add IAM binding for specific users
gcloud run services add-iam-policy-binding 5tran \
    --member='user:your-email@example.com' \
    --role='roles/run.invoker'
```

### 3. VPC Connector (Optional)

For private network access:

```bash
gcloud run services update 5tran \
    --vpc-connector YOUR_VPC_CONNECTOR \
    --vpc-egress all-traffic
```

## Monitoring and Logs

### View Logs

```bash
# Real-time logs
gcloud run services logs tail 5tran --region us-central1

# Recent logs
gcloud run services logs read 5tran --limit 50 --region us-central1
```

### Metrics

View in Google Cloud Console:
- Cloud Run → 5tran → Metrics
- Monitor: Request count, latency, memory usage, CPU utilization

## Troubleshooting

### Common Issues

1. **Container fails to start**
   ```bash
   # Check logs
   gcloud run services logs read 5tran --limit 100
   
   # Verify environment variables
   gcloud run services describe 5tran --format="value(spec.template.spec.containers[0].env)"
   ```

2. **Timeout errors**
   ```bash
   # Increase timeout
   gcloud run services update 5tran --timeout 3600
   ```

3. **Out of memory**
   ```bash
   # Increase memory
   gcloud run services update 5tran --memory 4Gi
   ```

4. **Build fails**
   ```bash
   # Test locally first
   docker build -t 5tran-test .
   docker run -p 8080:8080 \
       -e FIVETRAN_API_SECRET_BASE64=your_key \
       -e FIRECRAWL_API_KEY=your_key \
       -e GEMINI_API_KEY=your_key \
       5tran-test
   ```

## Cost Optimization

Cloud Run pricing is based on:
- Request count
- CPU and memory allocation
- Request duration

To optimize costs:

1. **Enable auto-scaling to zero**
   ```bash
   gcloud run services update 5tran --min-instances 0
   ```

2. **Use appropriate resources**
   ```bash
   # Start with smaller resources if possible
   gcloud run services update 5tran --memory 1Gi --cpu 1
   ```

3. **Set request concurrency**
   ```bash
   gcloud run services update 5tran --concurrency 80
   ```

## Local Testing

Test the container locally before deploying:

```bash
# Build
docker build -t 5tran-local .

# Run locally
docker run -p 8080:8080 \
    -e PORT=8080 \
    -e FIVETRAN_API_SECRET_BASE64="your_key" \
    -e FIRECRAWL_API_KEY="your_key" \
    -e GEMINI_API_KEY="your_key" \
    5tran-local

# Test
open http://localhost:8080
```

## Cleanup

To delete the service:

```bash
gcloud run services delete 5tran --region us-central1
```

To delete the container images:

```bash
gcloud container images delete gcr.io/YOUR_PROJECT_ID/5tran:latest
```

## Support

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Gradio Documentation](https://gradio.app/docs)
- [Docker Documentation](https://docs.docker.com)

