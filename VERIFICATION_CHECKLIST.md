# Deployment Verification Checklist

Use this checklist to verify your containerized 5tran deployment.

## Pre-Deployment Checklist

### Local Environment
- [ ] Docker installed and running
- [ ] gcloud CLI installed (`gcloud --version`)
- [ ] Authenticated with Google Cloud (`gcloud auth list`)
- [ ] Project ID set (`gcloud config get-value project`)

### Required Files Present
- [ ] `Dockerfile` exists and is valid
- [ ] `.dockerignore` exists
- [ ] `.gcloudignore` exists
- [ ] `deploy.sh` exists and is executable
- [ ] `cloudbuild.yaml` exists
- [ ] `pyproject.toml` exists
- [ ] `uv.lock` exists
- [ ] `app.py` exists
- [ ] `src/` directory exists

### Environment Variables Set
- [ ] `ACCESS_PASSWORD` set and valid
- [ ] `FIVETRAN_API_SECRET_BASE64` set and valid
- [ ] `FIRECRAWL_API_KEY` set and valid
- [ ] `GEMINI_API_KEY` set and valid
- [ ] `PROJECT_ID` set (for deployment)

### Google Cloud Project Setup
- [ ] GCP project created
- [ ] Billing enabled on project
- [ ] Cloud Run API enabled
- [ ] Container Registry API enabled
- [ ] Cloud Build API enabled
- [ ] Appropriate IAM permissions

## Local Testing Checklist

### Build the Image
```bash
docker build -t 5tran:test .
```
- [ ] Build completes without errors
- [ ] No missing dependencies
- [ ] Image size is reasonable (<2GB)

### Run Locally
```bash
docker run -p 8080:8080 \
  -e PORT=8080 \
  -e ACCESS_PASSWORD="your_password" \
  -e FIVETRAN_API_SECRET_BASE64="your_key" \
  -e FIRECRAWL_API_KEY="your_key" \
  -e GEMINI_API_KEY="your_key" \
  5tran:test
```
- [ ] Container starts without errors
- [ ] No import errors
- [ ] Application logs show successful startup
- [ ] Can access http://localhost:8080
- [ ] Gradio UI loads correctly
- [ ] All form fields visible
- [ ] Can submit test request (optional)

### Container Health Checks
- [ ] Container doesn't crash on startup
- [ ] Memory usage is acceptable
- [ ] No permission errors
- [ ] All environment variables loaded

## Deployment Checklist

### Pre-Deployment
- [ ] All local tests passed
- [ ] Environment variables verified
- [ ] Project ID is correct
- [ ] Target region selected (default: us-central1)

### Deploy Using Script
```bash
./deploy.sh
```
- [ ] Script validates all environment variables
- [ ] Docker build completes successfully
- [ ] Image pushed to GCR successfully
- [ ] Cloud Run deployment completes
- [ ] Service URL displayed

### Verify Deployment
```bash
# Get service URL
gcloud run services describe 5tran \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
```
- [ ] Service URL is accessible
- [ ] HTTPS works
- [ ] Application loads
- [ ] Gradio interface renders correctly

### Test Deployed Application
- [ ] Visit the service URL
- [ ] Gradio UI loads without errors
- [ ] All form fields are present (including Access Password)
- [ ] Can fill in test data
- [ ] Test with wrong password - should show error
- [ ] Test with correct password - should proceed
- [ ] Submit button works
- [ ] Progress indicators display
- [ ] Results are shown correctly

## Post-Deployment Verification

### Cloud Run Service Status
```bash
gcloud run services describe 5tran --region us-central1
```
- [ ] Service status is "Ready"
- [ ] Revision is serving traffic
- [ ] All 4 environment variables are set (ACCESS_PASSWORD, FIVETRAN_API_SECRET_BASE64, FIRECRAWL_API_KEY, GEMINI_API_KEY)
- [ ] Memory allocation is correct (2Gi)
- [ ] CPU allocation is correct (2 vCPU)
- [ ] Timeout is set (3600s)

### Check Logs
```bash
gcloud run services logs read 5tran --region us-central1 --limit 50
```
- [ ] No startup errors
- [ ] Application initialized successfully
- [ ] Gradio server started
- [ ] No import errors
- [ ] No missing environment variables

### Resource Monitoring
- [ ] Check Cloud Console for service metrics
- [ ] Verify memory usage is within limits
- [ ] Check CPU utilization
- [ ] Monitor request latency
- [ ] Review error rate (should be 0%)

### Security Verification
- [ ] Service runs as non-root user
- [ ] Environment variables not exposed in logs
- [ ] HTTPS enabled by default
- [ ] Consider: Authentication required? (if needed)
- [ ] Consider: VPC connector? (if needed)

## Functional Testing

### Test Connector Generation
- [ ] Fill in all required fields
- [ ] Submit a test connector generation
- [ ] Monitor progress indicators
- [ ] Wait for completion
- [ ] Verify success or failure message
- [ ] Check generated output

### Error Handling
- [ ] Test with missing fields
- [ ] Test with invalid API keys (optional)
- [ ] Verify error messages display correctly
- [ ] Confirm application doesn't crash

## Performance Testing

### Load Testing (Optional)
- [ ] Test with concurrent requests
- [ ] Monitor auto-scaling behavior
- [ ] Check response times
- [ ] Verify no timeouts
- [ ] Monitor memory usage under load

### Scaling Verification
- [ ] Service scales to zero when idle
- [ ] Cold start time is acceptable
- [ ] Service scales up on demand
- [ ] Max instances respected

## Cost Verification

### Initial Checks
- [ ] Check Cloud Console billing page
- [ ] Verify service scales to zero
- [ ] No unexpected charges
- [ ] Resource allocation matches requirements

### Cost Optimization
- [ ] Min instances set to 0
- [ ] Max instances set appropriately (10)
- [ ] Memory not over-allocated
- [ ] CPU not over-allocated

## Rollback Plan

In case of issues:

### Quick Rollback
```bash
# List revisions
gcloud run revisions list --service 5tran --region us-central1

# Rollback to previous revision
gcloud run services update-traffic 5tran \
  --to-revisions PREVIOUS_REVISION=100 \
  --region us-central1
```
- [ ] Previous revision identified
- [ ] Rollback procedure tested
- [ ] Traffic routing works

### Complete Cleanup (if needed)
```bash
# Delete service
gcloud run services delete 5tran --region us-central1

# Delete images
gcloud container images delete gcr.io/PROJECT_ID/5tran --quiet
```
- [ ] Cleanup procedure documented
- [ ] Backup of working configuration

## Documentation Verification

- [ ] README.md updated with deployment info
- [ ] DEPLOYMENT.md is comprehensive
- [ ] QUICKSTART.md covers common tasks
- [ ] CONTAINER_SUMMARY.md describes architecture
- [ ] All commands in docs are tested and working

## Maintenance Tasks

### Regular Checks
- [ ] Monitor service health weekly
- [ ] Review logs for errors
- [ ] Check for dependency updates
- [ ] Update uv.lock when needed
- [ ] Rebuild and redeploy for security updates

### Update Procedure
1. [ ] Test changes locally
2. [ ] Update version/tag
3. [ ] Build new image
4. [ ] Deploy to staging (if exists)
5. [ ] Deploy to production
6. [ ] Monitor for issues
7. [ ] Keep previous revision ready for rollback

## Success Criteria

✅ **Deployment is successful if:**
- Container builds without errors
- Application starts and runs correctly
- Gradio UI is accessible via HTTPS
- All features work as expected
- No errors in logs
- Service scales properly
- Costs are reasonable

## Common Issues and Solutions

### Issue: Container fails to build
- Check Dockerfile syntax
- Verify all COPY paths exist
- Ensure uv.lock is up to date

### Issue: Application won't start
- Check environment variables
- Review logs for import errors
- Verify PORT is set correctly

### Issue: Timeout errors
- Increase timeout in deploy command
- Check for long-running operations
- Consider increasing CPU/memory

### Issue: Out of memory
- Increase memory allocation
- Check for memory leaks
- Review connector generation process

### Issue: Cold starts too slow
- Consider setting min-instances > 0
- Optimize container size
- Review startup time

## Support

If you encounter issues:
1. Check logs: `gcloud run services logs read 5tran --limit 100`
2. Review [DEPLOYMENT.md](DEPLOYMENT.md) troubleshooting section
3. Verify all checklist items are completed
4. Test locally to isolate issues
5. Check Cloud Console for service status

---

**Checklist Version:** 1.0  
**Last Updated:** 2024  
**Maintainer:** 5tran Team

