# InfraGuard Grafana Dashboard

This directory contains the Grafana dashboard configuration for visualizing InfraGuard metrics and anomaly detection results.

## Dashboard Overview

The InfraGuard AIOps Dashboard provides comprehensive visualization of:

- **Real-time Metrics**: CPU, Memory, HTTP Error Rate, Request Latency
- **Gauge Panels**: Current values with threshold indicators
- **Time-Series Graphs**: Historical trends with configurable time ranges
- **Service Status**: Monitored service health indicators

## Features

### Panels

1. **CPU Usage** (Time Series)
   - Displays CPU utilization percentage over time
   - Thresholds: Yellow (70%), Red (85%)
   - Shows mean, current, and max values

2. **Memory Usage** (Time Series)
   - Displays memory utilization percentage over time
   - Thresholds: Yellow (70%), Red (85%)
   - Shows mean, current, and max values

3. **HTTP Error Rate** (Time Series)
   - Displays HTTP error rate percentage over time
   - Thresholds: Yellow (5%), Red (10%)
   - Shows mean, current, and max values

4. **Request Latency** (Time Series)
   - Displays request latency in milliseconds over time
   - Thresholds: Yellow (100ms), Red (200ms)
   - Shows mean, current, and max values

5. **Monitored Services** (Stat)
   - Shows status of monitored services
   - Indicates if services are up or down

6. **Current CPU** (Gauge)
   - Real-time CPU usage gauge
   - Color-coded thresholds

7. **Current Memory** (Gauge)
   - Real-time memory usage gauge
   - Color-coded thresholds

8. **Current Error Rate** (Gauge)
   - Real-time HTTP error rate gauge
   - Color-coded thresholds

### Variables

- **Data Source**: Select Prometheus data source
- **Metric Type**: Filter by metric type (CPU, Memory, Error Rate, Latency)

### Settings

- **Auto-refresh**: 30 seconds
- **Default time range**: Last 6 hours
- **Timezone**: Browser default
- **Theme**: Dark mode

## Installation

### Prerequisites

- Grafana 9.0+ installed
- Prometheus data source configured in Grafana
- InfraGuard collecting metrics to Prometheus

### Method 1: Import via UI

1. Open Grafana in your browser
2. Navigate to **Dashboards** → **Import**
3. Click **Upload JSON file**
4. Select `infraguard-dashboard.json`
5. Select your Prometheus data source
6. Click **Import**

### Method 2: Import via API

```bash
# Set your Grafana URL and API key
GRAFANA_URL="http://localhost:3000"
GRAFANA_API_KEY="your-api-key"

# Import dashboard
curl -X POST \
  -H "Authorization: Bearer ${GRAFANA_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @infraguard-dashboard.json \
  "${GRAFANA_URL}/api/dashboards/db"
```

### Method 3: Provisioning (Recommended for Production)

1. Copy the dashboard JSON to Grafana provisioning directory:

```bash
# For Docker
cp infraguard-dashboard.json /etc/grafana/provisioning/dashboards/

# For Kubernetes
kubectl create configmap grafana-dashboard-infraguard \
  --from-file=infraguard-dashboard.json \
  -n monitoring
```

2. Create a provisioning configuration file:

```yaml
# /etc/grafana/provisioning/dashboards/infraguard.yaml
apiVersion: 1

providers:
  - name: 'InfraGuard'
    orgId: 1
    folder: 'AIOps'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
      foldersFromFilesStructure: true
```

3. Restart Grafana:

```bash
# Docker
docker-compose restart grafana

# Kubernetes
kubectl rollout restart deployment/grafana -n monitoring

# Systemd
sudo systemctl restart grafana-server
```

## Configuration

### Prometheus Data Source

Ensure your Prometheus data source is configured in Grafana:

1. Navigate to **Configuration** → **Data Sources**
2. Click **Add data source**
3. Select **Prometheus**
4. Configure:
   - **Name**: Prometheus
   - **URL**: http://prometheus:9090 (or your Prometheus URL)
   - **Access**: Server (default)
5. Click **Save & Test**

### Dashboard Variables

The dashboard includes two variables:

#### DS_PROMETHEUS
- **Type**: Data source
- **Query**: prometheus
- **Purpose**: Select Prometheus data source

#### metric_type
- **Type**: Custom
- **Options**: All, CPU, Memory, Error Rate, Latency
- **Purpose**: Filter panels by metric type

### Customizing Thresholds

To adjust alert thresholds:

1. Click on a panel title → **Edit**
2. Navigate to **Field** tab
3. Scroll to **Thresholds**
4. Modify values:
   - Green: Normal range
   - Yellow: Warning threshold
   - Red: Critical threshold
5. Click **Apply**

## Usage

### Viewing Metrics

1. Open the InfraGuard dashboard in Grafana
2. Use the time range picker (top right) to select time window
3. Use the refresh dropdown to set auto-refresh interval
4. Use the **Metric Type** variable to filter by specific metrics

### Analyzing Anomalies

When InfraGuard detects anomalies:

1. Check the time-series graphs for unusual patterns
2. Look for threshold breaches (yellow/red zones)
3. Correlate across multiple metrics
4. Use the time range picker to zoom into specific periods

### Correlating with Alerts

1. Note the timestamp of anomalies in the dashboard
2. Check InfraGuard logs for corresponding alerts
3. Verify Slack/Jira notifications were sent
4. Use Prometheus queries to investigate further

## Docker Compose Integration

To add Grafana to your InfraGuard Docker Compose setup:

```yaml
# Add to docker-compose.yml
services:
  grafana:
    image: grafana/grafana:latest
    container_name: infraguard-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/infraguard-dashboard.json:/etc/grafana/provisioning/dashboards/infraguard-dashboard.json
      - ./grafana/provisioning.yaml:/etc/grafana/provisioning/dashboards/provisioning.yaml
    networks:
      - infraguard-network
    depends_on:
      - prometheus

volumes:
  grafana-data:
```

Create `grafana/provisioning.yaml`:

```yaml
apiVersion: 1

providers:
  - name: 'InfraGuard'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
```

Start Grafana:

```bash
docker-compose up -d grafana
```

Access Grafana:
- URL: http://localhost:3000
- Username: admin
- Password: admin (change on first login)

## Kubernetes Deployment

### Using Helm

```bash
# Add Grafana Helm repository
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install Grafana with dashboard
helm install grafana grafana/grafana \
  --namespace monitoring \
  --set persistence.enabled=true \
  --set persistence.size=10Gi \
  --set adminPassword=admin \
  --set datasources."datasources\.yaml".apiVersion=1 \
  --set datasources."datasources\.yaml".datasources[0].name=Prometheus \
  --set datasources."datasources\.yaml".datasources[0].type=prometheus \
  --set datasources."datasources\.yaml".datasources[0].url=http://prometheus:9090 \
  --set datasources."datasources\.yaml".datasources[0].access=proxy \
  --set datasources."datasources\.yaml".datasources[0].isDefault=true

# Create ConfigMap for dashboard
kubectl create configmap grafana-dashboard-infraguard \
  --from-file=infraguard-dashboard.json \
  -n monitoring

# Label ConfigMap for auto-discovery
kubectl label configmap grafana-dashboard-infraguard \
  grafana_dashboard=1 \
  -n monitoring
```

### Manual Deployment

```yaml
# grafana-deployment.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboard-infraguard
  namespace: monitoring
  labels:
    grafana_dashboard: "1"
data:
  infraguard-dashboard.json: |
    # Paste dashboard JSON here

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:latest
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          value: "admin"
        volumeMounts:
        - name: grafana-storage
          mountPath: /var/lib/grafana
        - name: grafana-dashboards
          mountPath: /etc/grafana/provisioning/dashboards
      volumes:
      - name: grafana-storage
        persistentVolumeClaim:
          claimName: grafana-pvc
      - name: grafana-dashboards
        configMap:
          name: grafana-dashboard-infraguard

---
apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: monitoring
spec:
  type: LoadBalancer
  ports:
  - port: 3000
    targetPort: 3000
  selector:
    app: grafana
```

Apply:

```bash
kubectl apply -f grafana-deployment.yaml
```

## Troubleshooting

### Dashboard Not Showing Data

**Check Prometheus data source**:
```bash
# Test Prometheus connectivity
curl http://prometheus:9090/api/v1/query?query=up

# Check if metrics exist
curl http://prometheus:9090/api/v1/query?query=cpu_usage_percent
```

**Verify InfraGuard is collecting metrics**:
```bash
# Check InfraGuard logs
docker-compose logs infraguard | grep "Collection cycle completed"

# Check Prometheus targets
curl http://prometheus:9090/api/v1/targets
```

### Panels Show "No Data"

1. Check time range - ensure it covers period when metrics were collected
2. Verify metric names match Prometheus queries
3. Check Prometheus data source is selected in dashboard variables
4. Ensure Prometheus is scraping the dummy app

### Dashboard Import Fails

1. Verify JSON syntax is valid
2. Check Grafana version compatibility (requires 9.0+)
3. Ensure Prometheus data source exists before importing
4. Try importing via API instead of UI

### Thresholds Not Working

1. Verify threshold values in panel configuration
2. Check unit settings match metric units
3. Ensure threshold mode is set to "absolute"
4. Verify color scheme is configured correctly

## Customization

### Adding New Panels

1. Click **Add panel** (top right)
2. Select **Add a new panel**
3. Configure query:
   - Data source: Prometheus
   - Query: Your PromQL expression
4. Configure visualization:
   - Type: Time series, Gauge, Stat, etc.
   - Thresholds: Set warning/critical levels
5. Click **Apply**

### Modifying Queries

Example PromQL queries:

```promql
# Average CPU over 5 minutes
avg_over_time(cpu_usage_percent[5m])

# Maximum memory in last hour
max_over_time(memory_usage_percent[1h])

# Error rate increase
rate(http_error_rate_percent[5m])

# 95th percentile latency
histogram_quantile(0.95, request_latency_ms)
```

### Creating Alerts

1. Edit a panel
2. Navigate to **Alert** tab
3. Click **Create alert rule from this panel**
4. Configure:
   - Condition: Threshold value
   - Evaluation: Frequency and duration
   - Notification: Contact point
5. Click **Save**

## Best Practices

1. **Use Variables**: Leverage dashboard variables for flexibility
2. **Set Appropriate Time Ranges**: Balance detail vs. overview
3. **Configure Auto-Refresh**: 30s for real-time, 5m for historical
4. **Organize Panels**: Group related metrics together
5. **Document Changes**: Add panel descriptions
6. **Version Control**: Keep dashboard JSON in git
7. **Test Queries**: Verify PromQL queries in Prometheus first
8. **Monitor Performance**: Avoid too many panels or complex queries

## Support

For issues or questions:

- **Documentation**: https://docs.infraguard.io
- **GitHub Issues**: https://github.com/your-org/infraguard/issues
- **Grafana Docs**: https://grafana.com/docs/

## License

This dashboard configuration is part of the InfraGuard project and follows the same license.
