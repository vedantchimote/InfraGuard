# InfraGuard Kubernetes Deployment

This directory contains Kubernetes manifests for deploying InfraGuard AIOps.

## Files

- `deployment.yaml` - Deployment and Service definitions
- `configmap.yaml` - Configuration settings
- `secret.yaml` - Sensitive credentials (Slack, Jira)
- `pvc.yaml` - Persistent volume claim for ML models

## Prerequisites

- Kubernetes cluster (1.20+)
- kubectl configured
- Docker image built and available
- Prometheus running in cluster

## Quick Start

### 1. Create Namespace (Optional)

```bash
kubectl create namespace infraguard
kubectl config set-context --current --namespace=infraguard
```

### 2. Create Secrets

```bash
kubectl create secret generic infraguard-secrets \
  --from-literal=SLACK_WEBHOOK_URL='https://hooks.slack.com/services/YOUR/WEBHOOK/URL' \
  --from-literal=JIRA_URL='https://your-domain.atlassian.net' \
  --from-literal=JIRA_PROJECT_KEY='INFRA' \
  --from-literal=JIRA_USERNAME='user@example.com' \
  --from-literal=JIRA_API_TOKEN='your-api-token'
```

### 3. Apply Manifests

```bash
# Apply in order
kubectl apply -f pvc.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f deployment.yaml
```

Or apply all at once:

```bash
kubectl apply -f k8s/
```

### 4. Verify Deployment

```bash
# Check pod status
kubectl get pods -l app=infraguard

# Check logs
kubectl logs -f deployment/infraguard

# Check health endpoint
kubectl port-forward deployment/infraguard 8000:8000
curl http://localhost:8000/health
```

## Configuration

### Environment Variables

Override configuration via environment variables in `deployment.yaml`:

```yaml
env:
- name: PROMETHEUS_URL
  value: "http://prometheus:9090"
- name: LOG_LEVEL
  value: "DEBUG"
```

### ConfigMap

Edit `configmap.yaml` to customize:
- Prometheus queries
- ML model parameters
- Alert thresholds
- Collection intervals

### Secrets

Update secrets:

```bash
kubectl edit secret infraguard-secrets
```

Or recreate:

```bash
kubectl delete secret infraguard-secrets
kubectl create secret generic infraguard-secrets --from-literal=...
```

## Scaling

InfraGuard is designed to run as a single instance. To scale:

```bash
kubectl scale deployment infraguard --replicas=1
```

Note: Multiple replicas may cause duplicate alerts. Consider using leader election for HA.

## Updating

### Update Configuration

```bash
kubectl apply -f configmap.yaml
kubectl rollout restart deployment/infraguard
```

### Update Image

```bash
kubectl set image deployment/infraguard infraguard=infraguard:v0.2.0
```

### Update Model

Copy trained model to PVC:

```bash
# Get pod name
POD=$(kubectl get pod -l app=infraguard -o jsonpath='{.items[0].metadata.name}')

# Copy model
kubectl cp models/pretrained/isolation_forest.pkl $POD:/app/models/pretrained/

# Restart to load new model
kubectl rollout restart deployment/infraguard
```

## Monitoring

### Health Checks

```bash
kubectl port-forward deployment/infraguard 8000:8000
curl http://localhost:8000/health
```

### Logs

```bash
# Follow logs
kubectl logs -f deployment/infraguard

# Last 100 lines
kubectl logs --tail=100 deployment/infraguard

# Logs from previous container (if crashed)
kubectl logs --previous deployment/infraguard
```

### Metrics

InfraGuard exposes health status via `/health` endpoint. Configure Prometheus to scrape:

```yaml
- job_name: 'infraguard'
  kubernetes_sd_configs:
    - role: pod
  relabel_configs:
    - source_labels: [__meta_kubernetes_pod_label_app]
      action: keep
      regex: infraguard
```

## Troubleshooting

### Pod Not Starting

```bash
kubectl describe pod -l app=infraguard
kubectl logs deployment/infraguard
```

Common issues:
- Missing secrets
- Invalid configuration
- Model file not found
- Prometheus not accessible

### Health Check Failing

```bash
kubectl exec -it deployment/infraguard -- curl localhost:8000/health
```

### Configuration Issues

```bash
kubectl get configmap infraguard-config -o yaml
kubectl exec -it deployment/infraguard -- cat /app/config/settings.yaml
```

## Cleanup

```bash
kubectl delete -f k8s/
```

Or:

```bash
kubectl delete deployment infraguard
kubectl delete service infraguard
kubectl delete configmap infraguard-config
kubectl delete secret infraguard-secrets
kubectl delete pvc infraguard-models
```
