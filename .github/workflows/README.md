# GitHub Actions Workflows

This directory contains GitHub Actions workflows for CI/CD of the Snake Game application.

## Workflows

### 1. `deploy.yml` - Application Deployment

Deploys the frontend and backend applications to Google Kubernetes Engine (GKE).

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main`
- Manual workflow dispatch

**Jobs:**
1. **test** - Runs backend and frontend tests
2. **build-and-push** - Builds Docker images and pushes to GCP Artifact Registry
3. **deploy** - Deploys to GKE cluster

**Required Secrets:**
- `GCP_SA_KEY` - Google Cloud Service Account JSON key with permissions for:
  - Artifact Registry (read/write)
  - GKE (cluster access)
  - Container Registry

### 2. `terraform.yml` - Infrastructure Deployment

Manages Terraform infrastructure deployments.

**Triggers:**
- Push to `main` branch (when Terraform files change)
- Pull requests to `main` (when Terraform files change)
- Manual workflow dispatch

**Jobs:**
1. **terraform-validate** - Validates Terraform configuration
2. **terraform-plan** - Creates Terraform plan for PRs
3. **terraform-apply** - Applies Terraform changes to production





## Workflow Details

### Image Tagging

- **Main branch:** `YYYYMMDDHHMMSS` (e.g., `20240115143022`)
- **Other branches:** `YYYYMMDDHHMMSS-branch-name` (e.g., `20240115143022-develop`)

### Deployment Process

1. **Test Phase:**
   - Runs backend unit tests
   - Runs frontend unit tests
   - Must pass before building images

2. **Build Phase:**
   - Builds backend Docker image
   - Builds frontend Docker image (with API URL configured)
   - Pushes images to Artifact Registry
   - Uses Docker layer caching for faster builds

3. **Deploy Phase:**
   - Authenticates to GKE
   - Creates/updates namespace
   - Applies Kubernetes manifests
   - Waits for rollout completion
   - Verifies deployment status

### Rollback

If a deployment fails, you can rollback using:

```bash
kubectl rollout undo deployment/snake-game-backend -n snake-game
kubectl rollout undo deployment/snake-game-frontend -n snake-game
```

Or manually deploy a previous image tag by updating the deployment manifest.

## Troubleshooting

### Build Failures

- Check Docker build logs in GitHub Actions
- Verify Dockerfile syntax
- Ensure all dependencies are in requirements.txt/package.json

### Deployment Failures

- Check Kubernetes events: `kubectl get events -n snake-game`
- Verify service account permissions
- Check pod logs: `kubectl logs -n snake-game -l app=snake-game,component=backend`

### Authentication Issues

- Verify `GCP_SA_KEY` secret is correctly set
- Check service account has necessary permissions
- Ensure service account key hasn't expired

## Manual Deployment

To manually trigger a deployment:

1. Go to **Actions** tab in GitHub
2. Select the workflow
3. Click **Run workflow**
4. Choose branch and click **Run workflow**

