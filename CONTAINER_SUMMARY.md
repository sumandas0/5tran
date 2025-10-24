# Containerization Summary - 5tran

## What Was Done

The 5tran application has been fully containerized for Google Cloud Run deployment using `uv` as the package manager.

## Files Created/Modified

### New Files Created

1. **`Dockerfile`**
   - Multi-stage build using Python 3.11-slim base image
   - Installs `uv` from official Astral image
   - Uses `uv sync --frozen --no-dev` for reproducible builds
   - Runs as non-root user (appuser) for security
   - Supports Cloud Run's dynamic PORT environment variable
   - CMD: `uv run python app.py`

2. **`.dockerignore`**
   - Excludes Python cache, virtual environments, and IDE files
   - Prevents unnecessary files from being copied to the image
   - Reduces image size and build time

3. **`.gcloudignore`**
   - Similar to .dockerignore but for Cloud Build
   - Optimizes Cloud Build performance
   - Excludes generated connectors and temporary files

4. **`deploy.sh`**
   - Automated deployment script for Cloud Run
   - Validates required environment variables
   - Builds, pushes, and deploys in one command
   - Configurable region and service name
   - Displays service URL after successful deployment

5. **`cloudbuild.yaml`**
   - Google Cloud Build configuration for CI/CD
   - Automatically builds and deploys on git push
   - Configurable for GitHub integration
   - Sets up environment variables and resource limits

6. **`DEPLOYMENT.md`**
   - Comprehensive deployment guide
   - Covers all deployment methods (script, manual, Cloud Build)
   - Security best practices (Secret Manager, IAM, VPC)
   - Troubleshooting section
   - Cost optimization tips
   - Local testing instructions

7. **`QUICKSTART.md`**
   - Quick reference for common tasks
   - Local Docker testing commands
   - Cloud Run deployment options
   - Troubleshooting common issues

### Modified Files

1. **`app.py`**
   - Updated to read PORT from environment variable
   - Changed from hardcoded port 7860 to: `port = int(os.getenv("PORT", 7860))`
   - Now Cloud Run compatible (defaults to 7860 for local dev)

2. **`README.md`**
   - Added "Cloud Deployment (Google Cloud Run)" section
   - Updated environment variable documentation
   - Added quick deploy instructions
   - Reorganized Setup section into Local Development and Cloud Deployment

## Environment Variables Required

The containerized application requires these three environment variables:

1. **`FIVETRAN_API_SECRET_BASE64`** (Required)
   - Base64-encoded Fivetran API credentials
   - Format: base64(api_key:api_secret)

2. **`FIRECRAWL_API_KEY`** (Required)
   - Firecrawl API key for web scraping
   - Format: fc-xxxxxxxx

3. **`GEMINI_API_KEY`** (Required)
   - Google Gemini API key for AI schema generation
   - Format: AIzaSy...

4. **`PORT`** (Optional)
   - Server port number
   - Automatically set by Cloud Run
   - Defaults to 7860 for local development

## Container Architecture

```
┌─────────────────────────────────────────┐
│ Python 3.11-slim Base Image            │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│ Install uv Package Manager              │
│ (from ghcr.io/astral-sh/uv:latest)     │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│ Copy pyproject.toml & uv.lock           │
│ (for Docker layer caching)              │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│ Install Dependencies                    │
│ uv sync --frozen --no-dev --no-cache   │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│ Copy Application Code                   │
│ - app.py                                │
│ - src/ directory                        │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│ Create Non-Root User (appuser)          │
│ UID: 1000                               │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│ Run Gradio Application                  │
│ CMD: uv run python app.py               │
└─────────────────────────────────────────┘
```

## Deployment Methods

### 1. Quick Deploy Script (Easiest)
```bash
export PROJECT_ID="your-gcp-project-id"
export FIVETRAN_API_SECRET_BASE64="your_key"
export FIRECRAWL_API_KEY="your_key"
export GEMINI_API_KEY="your_key"
./deploy.sh
```

### 2. Manual Docker + gcloud
```bash
docker build -t gcr.io/PROJECT_ID/5tran:latest .
docker push gcr.io/PROJECT_ID/5tran:latest
gcloud run deploy 5tran --image gcr.io/PROJECT_ID/5tran:latest ...
```

### 3. Cloud Build CI/CD
```bash
gcloud builds submit --config cloudbuild.yaml
```

## Cloud Run Configuration

**Default Settings:**
- **Memory**: 2 GiB
- **CPU**: 2 vCPU
- **Timeout**: 3600 seconds (1 hour)
- **Max Instances**: 10
- **Min Instances**: 0 (scales to zero)
- **Concurrency**: 80 requests per instance
- **Port**: 8080 (or dynamic via $PORT)

**Estimated Costs:**
- Scales to zero when not in use (no cost)
- Pay only for request time
- ~$0.024 per hour of 2 vCPU usage
- ~$0.0025 per hour of 2 GiB memory

## Security Features

1. **Non-Root User**: Container runs as `appuser` (UID 1000)
2. **Environment Variables**: Sensitive data via env vars (or Secret Manager)
3. **Read-Only Filesystem**: Application doesn't require write access to system files
4. **Minimal Base Image**: python:3.11-slim reduces attack surface
5. **No Hardcoded Secrets**: All credentials via environment variables

## Testing Locally

```bash
# Build the image
docker build -t 5tran:test .

# Run with environment variables
docker run -p 8080:8080 \
  -e PORT=8080 \
  -e FIVETRAN_API_SECRET_BASE64="your_key" \
  -e FIRECRAWL_API_KEY="your_key" \
  -e GEMINI_API_KEY="your_key" \
  5tran:test

# Access at http://localhost:8080
```

## Benefits of Containerization

1. **Consistent Environment**: Same behavior in dev, staging, and production
2. **Easy Scaling**: Cloud Run automatically scales based on demand
3. **Zero Ops**: No server management required
4. **Cost Effective**: Pay only for actual usage, scales to zero
5. **Global Deployment**: Deploy to any GCP region
6. **HTTPS by Default**: Cloud Run provides SSL certificates
7. **Version Control**: Easy rollbacks and canary deployments
8. **Reproducible Builds**: `uv.lock` ensures exact dependencies

## Next Steps

1. **Test Locally**: Build and run the container locally
2. **Set Up GCP**: Create project and enable required APIs
3. **Configure Secrets**: Set up environment variables or Secret Manager
4. **Deploy**: Use `deploy.sh` or Cloud Build
5. **Monitor**: Set up logging and monitoring in Cloud Console
6. **Scale**: Adjust memory/CPU based on usage patterns

## Troubleshooting

See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- Common deployment issues
- Log analysis commands
- Resource adjustment tips
- Secret Manager integration
- VPC configuration
- Custom domain setup

## Support Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Gradio Cloud Deployment](https://gradio.app/guides/deploying-gradio-apps/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

