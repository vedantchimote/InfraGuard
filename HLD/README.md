# InfraGuard - High-Level Design (HLD) Documentation

This directory contains comprehensive PlantUML-based High-Level Design diagrams for the InfraGuard AIOps platform.

## 📋 Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Component Interaction Sequence](#2-component-interaction-sequence)
3. [Data Flow Architecture](#3-data-flow-architecture)
4. [ML Pipeline Architecture](#4-ml-pipeline-architecture)
5. [Alert Routing Flow](#5-alert-routing-flow)
6. [Deployment Architecture - Kubernetes](#6-deployment-architecture---kubernetes)
7. [Deployment Architecture - Docker Compose](#7-deployment-architecture---docker-compose)
8. [Class Diagram - Core Components](#8-class-diagram---core-components)
9. [Forecasting Pipeline](#9-forecasting-pipeline)
10. [Monitoring and Observability](#10-monitoring-and-observability)
11. [Security Architecture](#11-security-architecture)
12. [Error Handling and Resilience](#12-error-handling-and-resilience)

---

## Diagram Descriptions

### 1. System Architecture
**File**: `01-system-architecture.puml`

**Purpose**: Provides a high-level overview of the InfraGuard system, showing all major components and their interactions.

**Key Elements**:
- External systems (Prometheus, Slack, Jira, Grafana)
- Collection Layer (Metrics Collector, Data Formatter)
- Intelligence Layer (ML Detector, Forecaster)
- Alerting Layer (Alert Manager, Runbook Mapper)
- Configuration Layer (Settings Manager)

**Use Case**: Understanding the overall system architecture and component relationships.

---

### 2. Component Interaction Sequence
**File**: `02-component-interaction-sequence.puml`

**Purpose**: Illustrates the sequence of interactions between components during a typical 1-minute collection cycle.

**Key Elements**:
- Scheduler triggering collection
- Prometheus query execution
- Data transformation pipeline
- Parallel anomaly detection and forecasting
- Alert routing to Slack and Jira

**Use Case**: Understanding the runtime behavior and data flow during normal operations.

---

### 3. Data Flow Architecture
**File**: `03-data-flow-architecture.puml`

**Purpose**: Shows how data flows through the system from input to output.

**Key Elements**:
- Data Input: Prometheus metrics
- Data Transformation: PromQL → JSON → DataFrame
- Processing Pipeline: Normalization, feature engineering, sliding window
- ML Pipeline: Model loading, scoring, thresholding
- Alert Output: Metadata, runbook context, payload
- Delivery Channels: Slack, Jira

**Use Case**: Understanding data transformations and processing stages.

---

### 4. ML Pipeline Architecture
**File**: `04-ml-pipeline-architecture.puml`

**Purpose**: Details the machine learning pipeline for anomaly detection.

**Key Elements**:
- Training Phase: Historical data → Feature extraction → Model training → Validation → Serialization
- Runtime Phase: Model loading → Live metrics → Feature extraction → Prediction → Confidence calculation → Alert triggering

**Use Case**: Understanding how the Isolation Forest algorithm is trained and used for anomaly detection.

---

### 5. Alert Routing Flow
**File**: `05-alert-routing-flow.puml`

**Purpose**: Flowchart showing the decision logic for alert routing.

**Key Elements**:
- Confidence threshold checking
- Runbook lookup
- Alert payload building
- Parallel delivery to Slack and Jira
- Retry logic
- Error handling

**Use Case**: Understanding alert routing decisions and retry mechanisms.

---

### 6. Deployment Architecture - Kubernetes
**File**: `06-deployment-architecture-kubernetes.puml`

**Purpose**: Shows how InfraGuard is deployed in a Kubernetes cluster.

**Key Elements**:
- Monitoring Namespace: Prometheus, Grafana
- InfraGuard Namespace: Application pod, ConfigMap, Secret, PVC
- Application Namespace: Monitored application pods
- External Services: Slack API, Jira API

**Use Case**: Understanding production deployment architecture and resource organization.

---

### 7. Deployment Architecture - Docker Compose
**File**: `07-deployment-architecture-docker-compose.puml`

**Purpose**: Shows the local development environment using Docker Compose.

**Key Elements**:
- Services: Prometheus, Dummy App, InfraGuard, Grafana
- Volumes: Configuration files, ML models
- Port mappings
- Developer interactions

**Use Case**: Setting up local development environment and testing.

---

### 8. Class Diagram - Core Components
**File**: `08-class-diagram-core-components.puml`

**Purpose**: UML class diagram showing the structure of core components.

**Key Elements**:
- Collection Layer: PrometheusCollector, DataFormatter
- Intelligence Layer: IsolationForestDetector, TimeSeriesForecaster, AnomalyResult, ForecastResult
- Alerting Layer: AlertManager, SlackNotifier, JiraNotifier, RunbookMapper, AlertStatus
- Configuration: ConfigurationManager

**Use Case**: Understanding class structure, methods, and relationships for development.

---

### 9. Forecasting Pipeline
**File**: `09-forecasting-pipeline.puml`

**Purpose**: Flowchart showing the time-series forecasting pipeline (optional feature).

**Key Elements**:
- Data preparation for Prophet
- Model fitting with seasonality
- 15-minute forecast generation
- Threshold breach detection
- Predictive alert generation

**Use Case**: Understanding how predictive alerting works.

---

### 10. Monitoring and Observability
**File**: `10-monitoring-and-observability.puml`

**Purpose**: Shows how InfraGuard itself is monitored and observed.

**Key Elements**:
- Application Layer: Health server, logging, metrics exporter
- Observability Stack: Prometheus, Grafana, log files
- Monitored Metrics: Application, system, and business metrics
- Dashboard Panels: CPU, memory, error rate, latency, anomaly detection, alert success rate

**Use Case**: Understanding operational monitoring and troubleshooting.

---

### 11. Security Architecture
**File**: `11-security-architecture.puml`

**Purpose**: Details the security mechanisms and best practices.

**Key Elements**:
- External Communication: HTTPS/TLS encryption
- Security Layer: TLS/SSL, API token management, secrets manager, input validation
- Configuration: Kubernetes Secrets, ConfigMap
- Best Practices: Secret rotation, RBAC, external secret managers

**Use Case**: Understanding security controls and compliance requirements.

---

### 12. Error Handling and Resilience
**File**: `12-error-handling-and-resilience.puml`

**Purpose**: Shows resilience patterns and error handling strategies.

**Key Elements**:
- Resilience Patterns: Retry logic, circuit breaker, timeout management
- Fallback Mechanisms: Graceful degradation, default values, cache fallback
- Error Recovery: Health checks, auto-restart, state recovery
- Error Scenarios: Prometheus unavailable, model load failure, API failures, invalid data, memory exhaustion

**Use Case**: Understanding system resilience and failure recovery.

---

## How to Use These Diagrams

### Viewing PlantUML Diagrams

#### Option 1: Online Viewer
1. Visit [PlantUML Online Editor](http://www.plantuml.com/plantuml/uml/)
2. Copy the content of any `.puml` file
3. Paste into the editor
4. View the rendered diagram

#### Option 2: VS Code Extension
1. Install the "PlantUML" extension in VS Code
2. Open any `.puml` file
3. Press `Alt+D` to preview the diagram

#### Option 3: Command Line
```bash
# Install PlantUML
brew install plantuml  # macOS
apt-get install plantuml  # Ubuntu

# Generate PNG images
plantuml HLD/*.puml

# Generate SVG images
plantuml -tsvg HLD/*.puml
```

#### Option 4: Docker
```bash
# Generate all diagrams as PNG
docker run --rm -v $(pwd)/HLD:/data plantuml/plantuml:latest -tpng /data/*.puml

# Generate all diagrams as SVG
docker run --rm -v $(pwd)/HLD:/data plantuml/plantuml:latest -tsvg /data/*.puml
```

### Generating Images

To generate PNG images for all diagrams:

```bash
# Using PlantUML CLI
cd HLD
plantuml *.puml

# Using Docker
docker run --rm -v $(pwd):/data plantuml/plantuml:latest -tpng /data/*.puml
```

This will create PNG files alongside each `.puml` file.

---

## Diagram Relationships

```
System Architecture (01)
    ├── Component Interaction Sequence (02)
    ├── Data Flow Architecture (03)
    │   ├── ML Pipeline Architecture (04)
    │   └── Forecasting Pipeline (09)
    ├── Alert Routing Flow (05)
    ├── Deployment Architecture - K8s (06)
    ├── Deployment Architecture - Docker (07)
    ├── Class Diagram (08)
    ├── Monitoring and Observability (10)
    ├── Security Architecture (11)
    └── Error Handling and Resilience (12)
```

---

## Key Design Decisions

### 1. Isolation Forest for Anomaly Detection
- **Why**: Unsupervised learning, efficient O(n log n) complexity, no labeled data required
- **Trade-off**: May have false positives, requires tuning contamination parameter

### 2. Prophet for Time-Series Forecasting
- **Why**: Handles seasonality well, robust to missing data, easy to use
- **Trade-off**: Requires minimum 2 days of data, slower than simple models

### 3. 1-Minute Collection Interval
- **Why**: Balance between real-time detection and system load
- **Trade-off**: May miss very short-lived anomalies

### 4. Parallel Alert Delivery
- **Why**: Faster notification, independent failure handling
- **Trade-off**: More complex error handling

### 5. Pre-trained Model Approach
- **Why**: Faster startup, consistent behavior, easier deployment
- **Trade-off**: Requires periodic retraining with new data

---

## Architecture Principles

1. **Modularity**: Each component has a single responsibility
2. **Scalability**: Stateless design allows horizontal scaling
3. **Resilience**: Graceful degradation, retry logic, circuit breakers
4. **Observability**: Comprehensive logging, metrics, and health checks
5. **Security**: TLS encryption, secret management, input validation
6. **Simplicity**: Single containerized service, minimal dependencies

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Data Collection | Prometheus | Metrics storage and querying |
| Data Processing | Pandas | Data transformation and feature engineering |
| ML Framework | scikit-learn | Isolation Forest implementation |
| Forecasting | Prophet | Time-series forecasting |
| Alerting | Slack, Jira | Notification delivery |
| Visualization | Grafana | Dashboard and monitoring |
| Orchestration | Kubernetes | Container orchestration |
| Configuration | YAML | Settings management |
| Logging | Python logging | Application logs |

---

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Collection Interval | 1 minute | Configurable |
| Anomaly Detection Latency | < 5 seconds | Per cycle |
| Forecasting Latency | < 10 seconds | Optional, per cycle |
| Alert Delivery Time | < 3 seconds | To Slack/Jira |
| Memory Usage | ~500 MB | With pre-trained model |
| CPU Usage | ~0.5 cores | Average during collection |
| Throughput | 60 metrics/minute | Per instance |

---

## Scalability Considerations

### Horizontal Scaling
- Deploy multiple InfraGuard instances
- Each instance monitors different metric sets
- Load balance using Kubernetes services

### Vertical Scaling
- Increase memory for larger models
- Increase CPU for faster processing
- Adjust resource limits in Kubernetes

### Data Volume Scaling
- Implement metric sampling for high-cardinality data
- Use time-based aggregation
- Archive old anomaly data

---

## Future Enhancements

1. **Multi-Model Support**: Support for additional ML algorithms (LSTM, Autoencoders)
2. **Adaptive Thresholds**: Dynamic threshold adjustment based on historical patterns
3. **Root Cause Analysis**: Automated correlation analysis to identify root causes
4. **Feedback Loop**: Incorporate user feedback to improve model accuracy
5. **Multi-Tenancy**: Support for multiple teams/projects in single deployment
6. **Advanced Forecasting**: Support for multivariate forecasting
7. **Custom Metrics**: User-defined metric collection and processing

---

## Related Documentation

- [Design Document](../documentation/Infraguard-design.md)
- [API Reference](../documentation/api-reference/)
- [Deployment Guide](../documentation/deployment/)
- [Architecture Overview](../documentation/concepts/architecture.mdx)
- [README](../README.md)

---

## Contributing

When adding new diagrams:

1. Follow the naming convention: `##-descriptive-name.puml`
2. Include a title in the diagram
3. Add comments for complex sections
4. Update this README with diagram description
5. Generate PNG/SVG for easy viewing
6. Test rendering in PlantUML viewer

---

## License

These diagrams are part of the InfraGuard project and follow the same license.

---

**Last Updated**: April 12, 2026  
**Version**: 1.0  
**Maintainer**: InfraGuard Team
