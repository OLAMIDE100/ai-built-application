# Kubernetes Workloads

This directory contains Kubernetes manifests for deploying the Snake Game application.

## Files

- `backend-deployment.yaml` - Backend API deployment
- `backend-service.yaml` - Backend API service (ClusterIP)
- `frontend-deployment.yaml` - Frontend deployment (Nginx)
- `frontend-service.yaml` - Frontend service (LoadBalancer or ClusterIP)
- `configmap.yaml` - Non-sensitive configuration
- `secrets.yaml.example` - Template for sensitive data (copy to `secrets.yaml` and update)
- `ingress.yaml` - Ingress configuration for external access

## Prerequisites

1. **Kubernetes cluster** (minikube, GKE, EKS, AKS, etc.)
2. **kubectl** configured to access your cluster
3. **Container images** built and pushed to a registry
4. **PostgreSQL database** (can be deployed separately or use managed service)

## Setup Instructions

### 1. Build and Push Images

```bash
# Build backend image
cd backend
docker build -t your-registry/snake-game-backend:latest .
docker push your-registry/snake-game-backend:latest

# Build frontend image
cd ../frontend
docker build -t your-registry/snake-game-frontend:latest .
docker push your-registry/snake-game-frontend:latest
```

### 2. Update Image References

Update the `image` field in:
- `backend-deployment.yaml`
- `frontend-deployment.yaml`

Replace `snake-game-backend:latest` and `snake-game-frontend:latest` with your actual image registry paths.

### 3. Create Secrets

```bash
# Option 1: Copy and edit the example
cp secrets.yaml.example secrets.yaml
# Edit secrets.yaml with your actual values
kubectl apply -f secrets.yaml

# Option 2: Use kubectl create secret
kubectl create secret generic snake-game-secrets \
  --from-literal=database-url='postgresql://user:pass@host:5432/db' \
  --from-literal=secret-key='your-secret-key' \
  --from-literal=postgres-user='snakegame' \
  --from-literal=postgres-password='snakegame123' \
  --from-literal=postgres-db='snake_game'
```

### 4. Apply ConfigMap

```bash
kubectl apply -f configmap.yaml
```

### 5. Deploy Backend

```bash
kubectl apply -f backend-deployment.yaml
kubectl apply -f backend-service.yaml
```

### 6. Deploy Frontend

```bash
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml
```

### 7. (Optional) Deploy Ingress

If you have an ingress controller installed:

```bash
# Update ingress.yaml with your domain
kubectl apply -f ingress.yaml
```

## Deployment Order

1. ConfigMap
2. Secrets
3. Backend Deployment
4. Backend Service
5. Frontend Deployment
6. Frontend Service
7. Ingress (optional)

## Quick Deploy Script

```bash
#!/bin/bash
# Deploy all resources
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml  # Make sure this exists first
kubectl apply -f backend-deployment.yaml
kubectl apply -f backend-service.yaml
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml
kubectl apply -f ingress.yaml  # Optional
```

## Database Setup

The manifests assume a PostgreSQL database is available. You can:

1. **Use a managed database service** (RDS, Cloud SQL, etc.)
   - Update the `database-url` in secrets to point to your managed database

2. **Deploy PostgreSQL in Kubernetes**
   - Use a PostgreSQL StatefulSet or Helm chart
   - Update the database URL to use the service name

3. **External database**
   - Update the database URL to point to your external database host

## Verification

```bash
# Check deployments
kubectl get deployments

# Check services
kubectl get services

# Check pods
kubectl get pods -l app=snake-game

# View logs
kubectl logs -l component=backend
kubectl logs -l component=frontend

# Check ingress
kubectl get ingress
```

## Scaling

```bash
# Scale backend
kubectl scale deployment snake-game-backend --replicas=3

# Scale frontend
kubectl scale deployment snake-game-frontend --replicas=3
```

## Updating

```bash
# Update image
kubectl set image deployment/snake-game-backend backend=your-registry/snake-game-backend:v1.1.0

# Rollout status
kubectl rollout status deployment/snake-game-backend

# Rollback if needed
kubectl rollout undo deployment/snake-game-backend
```

## Troubleshooting

### Backend not starting
```bash
# Check pod status
kubectl describe pod -l component=backend

# Check logs
kubectl logs -l component=backend

# Verify secrets
kubectl get secret snake-game-secrets -o yaml
```

### Frontend not accessible
```bash
# Check service
kubectl get svc snake-game-frontend

# Check ingress (if using)
kubectl describe ingress snake-game-ingress

# Port forward for testing
kubectl port-forward svc/snake-game-frontend 8080:80
```

### Database connection issues
- Verify the database URL in secrets
- Check if database service is accessible from pods
- Verify network policies allow database access

## Security Notes

- **Never commit `secrets.yaml` to version control**
- Use Kubernetes secrets management (Sealed Secrets, External Secrets Operator, etc.)
- Consider using service accounts with minimal permissions
- Enable network policies for pod-to-pod communication
- Use TLS/SSL for ingress (cert-manager recommended)

