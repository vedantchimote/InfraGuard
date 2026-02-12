# InfraGuard Architecture Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Component Architecture](#component-architecture)
4. [Data Flow](#data-flow)
5. [Deployment Architecture](#deployment-architecture)

## System Overview

InfraGuard is an AI-powered AIOps tool that provides intelligent infrastructure monitoring and predictive failure detection. The system continuously collects metrics from Prometheus, applies machine learning algorithms to detect statistical anomalies, predicts infrastructure failures before user impact, and automatically creates actionable alerts with contextual runbooks.

### Key Features
- Real-time anomaly detection using Isolation Forest ML algorithm
- Predictive failure analysis with 15-minute advance warning
- Automated Jira ticket creation and Slack notifications
- Contextual runbook mapping for rapid incident response
- Containerized deployment for Kubernetes environments

## High-Level Architecture

```mermaid
flowchart TB
    subgraph External["External Systems"]
        Prom[(Prometheus<br/>Time-Series DB)]
        Slack[Slack<br/>Notifications]
        Jira[Jira<br/>Issue Tracking]
        Grafana[Grafana<br/>Dashboards]
    end
    
    subgraph InfraGuard["InfraGuard Application"]
        direction TB
        
        subgraph Collection["Collection Layer"]
            Collector[Metrics Collector]
            Formatter[Data Formatter]
        end
        
        subgraph Intelligence["Intelligence Layer"]
            MLDetector[ML Anomaly Detector<br/>Isolation Forest]
            Forecaster[Time-Series Forecaster<br/>Prophet - Optional]
        end
        
        subgraph Alerting["Alerting Layer"]
            AlertMgr[Alert Manager]
            RunbookMap[Runbook Mapper]
        end
        
        subgraph Config["Configuration"]
            Settings[Settings Manager<br/>YAML Config]
        end
        
        Collector --> Formatter
        Formatter --> MLDetector
        Formatter --> Forecaster
        MLDetector --> AlertMgr
        Forecaster --> AlertMgr
        AlertMgr --> RunbookMap
        Settings -.-> Collector
        Settings -.-> MLDetector
        Settings -.-> AlertMgr
    end
    
    Prom -->|PromQL API| Collector
    AlertMgr -->|Webhook| Slack
    AlertMgr -->|REST API| Jira
    Prom -.->|Metrics Source| Grafana
    InfraGuard -.->|Anomaly Data| Grafana
    
    style InfraGuard fill:#e1f5ff
    style Collection fill:#fff4e6
    style Intelligence fill:#f3e5f5
    style Alerting fill:#e8f5e9
    style Config fill:#fce4ec
```

### Architecture Layers

**Collection Layer**
- Queries Prometheus API using PromQL
- Transforms JSON responses to Pandas DataFrames
- Adds derived features for ML processing

**Intelligence Layer**
- Isolation Forest for unsupervised anomaly detection
- Optional Prophet-based time-series forecasting
- Confidence scoring and threshold evaluation

**Alerting Layer**
- Routes alerts to Slack and Jira
- Maps anomalies to contextual runbooks
- Handles delivery failures with retry logic

**Configuration Layer**
- YAML-based configuration management
- Environment variable support
- Runtime validation

## Component Architecture

### Metrics Collector Component

```mermaid
classDiagram
    class PrometheusCollector {
        -str prometheus_url
        -dict queries
        -int timeout_seconds
        -Session http_session
        +__init__(config: dict)
        +collect_metrics() DataFrame
        +execute_query(query: str) dict
        -_build_query_url(query: str) str
        -_handle_api_error(error: Exception) None
    }
    
    class DataFormatter {
        +format_prometheus_response(response: dict) DataFrame
        +normalize_timestamps(df: DataFrame) DataFrame
        +add_feature_columns(df: DataFrame) DataFrame
        -_extract_metric_values(response: dict) list
        -_parse_timestamp(ts: float) datetime
    }
    
    PrometheusCollector --> DataFormatter : uses
```

### ML Detection Component

```mermaid
classDiagram
    class IsolationForestDetector {
        -IsolationForest model
        -float confidence_threshold
        -str model_path
        -bool is_trained
        +__init__(config: dict)
        +load_model(path: str) None
        +train(data: DataFrame) None
        +save_model(path: str) None
        +detect_anomalies(data: DataFrame) AnomalyResult
        +compute_confidence(scores: ndarray) float
        -_validate_input(data: DataFrame) bool
        -_extract_features(data: DataFrame) ndarray
    }
    
    class AnomalyResult {
        +bool is_anomaly
        +float confidence
        +ndarray scores
        +DataFrame anomalous_points
        +dict metadata
        +to_dict() dict
    }
    
    IsolationForestDetector --> AnomalyResult : returns
```

### Alert Management Component

```mermaid
classDiagram
    class AlertManager {
        -SlackNotifier slack
        -JiraNotifier jira
        -RunbookMapper runbook_mapper
        -dict config
        +__init__(config: dict)
        +send_alert(anomaly: AnomalyResult, metric_name: str) AlertStatus
        +send_forecast_alert(forecast: ForecastResult, metric_name: str) AlertStatus
        -_build_alert_payload(data: dict) dict
        -_log_alert_delivery(status: AlertStatus) None
    }
    
    class SlackNotifier {
        -str webhook_url
        -str channel
        -int retry_count
        +__init__(config: dict)
        +send_message(payload: dict) bool
        -_format_message(payload: dict) dict
        -_retry_send(payload: dict) bool
    }
    
    class JiraNotifier {
        -str api_url
        -str project_key
        -str username
        -str api_token
        +__init__(config: dict)
        +create_ticket(payload: dict) str
        -_format_ticket(payload: dict) dict
        -_authenticate() Session
    }
    
    class RunbookMapper {
        -dict mappings
        +__init__(config: dict)
        +get_runbook(metric_name: str, anomaly_type: str) str
        +load_mappings(path: str) None
    }
    
    AlertManager --> SlackNotifier : uses
    AlertManager --> JiraNotifier : uses
    AlertManager --> RunbookMapper : uses
```

## Data Flow

### End-to-End Data Flow

```mermaid
flowchart LR
    subgraph Input["Data Input"]
        P1[Prometheus<br/>Metrics]
    end
    
    subgraph Transform["Data Transformation"]
        Q1[PromQL<br/>Queries]
        J1[JSON<br/>Response]
        DF[Pandas<br/>DataFrame]
    end
    
    subgraph Process["Processing Pipeline"]
        direction TB
        N1[Normalize<br/>Timestamps]
        N2[Feature<br/>Engineering]
        N3[Sliding<br/>Window]
    end
    
    subgraph ML["ML Pipeline"]
        direction TB
        T1[Load Pre-trained<br/>Model]
        T2[Compute<br/>Anomaly Scores]
        T3[Apply<br/>Threshold]
    end
    
    subgraph Output["Alert Output"]
        direction TB
        A1[Anomaly<br/>Metadata]
        A2[Runbook<br/>Context]
        A3[Alert<br/>Payload]
    end
    
    subgraph Delivery["Delivery Channels"]
        S1[Slack]
        J2[Jira]
    end
    
    P1 --> Q1
    Q1 --> J1
    J1 --> DF
    DF --> N1
    N1 --> N2
    N2 --> N3
    N3 --> T1
    T1 --> T2
    T2 --> T3
    T3 --> A1
    A1 --> A2
    A2 --> A3
    A3 --> S1
    A3 --> J2
    
    style Input fill:#e3f2fd
    style Transform fill:#fff3e0
    style Process fill:#f3e5f5
    style ML fill:#e8f5e9
    style Output fill:#fce4ec
    style Delivery fill:#fff9c4
```

### ML Pipeline Architecture

```mermaid
flowchart TB
    subgraph Training["Training Phase (Offline)"]
        direction TB
        H1[(Historical<br/>Metrics)]
        H2[Extract<br/>Features]
        H3[Train<br/>Isolation Forest]
        H4[Validate<br/>Model]
        H5[Serialize<br/>to .pkl]
        
        H1 --> H2
        H2 --> H3
        H3 --> H4
        H4 --> H5
    end
    
    subgraph Runtime["Runtime Phase (Online)"]
        direction TB
        R1[Load Model<br/>from Disk]
        R2[Receive<br/>Live Metrics]
        R3[Feature<br/>Extraction]
        R4[Predict<br/>Anomaly Score]
        R5{Score = -1?}
        R6[Calculate<br/>Confidence %]
        R7{Confidence ><br/>Threshold?}
        R8[Trigger Alert]
        R9[Log Normal]
        
        R1 --> R2
        R2 --> R3
        R3 --> R4
        R4 --> R5
        R5 -->|Yes| R6
        R5 -->|No| R9
        R6 --> R7
        R7 -->|Yes| R8
        R7 -->|No| R9
    end
    
    H5 -.->|Model File| R1
    
    style Training fill:#e8f5e9
    style Runtime fill:#e3f2fd
```

### Alert Routing Flow

```mermaid
flowchart TD
    Start([Anomaly Detected])
    
    Start --> GetMetric[Get Metric Type<br/>& Confidence]
    GetMetric --> CheckConf{Confidence ><br/>Threshold?}
    
    CheckConf -->|No| LogOnly[Log Detection<br/>No Alert]
    CheckConf -->|Yes| GetRunbook[Lookup Runbook<br/>from Config]
    
    GetRunbook --> BuildPayload[Build Alert Payload:<br/>- Metric details<br/>- Confidence %<br/>- Timestamp<br/>- Runbook URL]
    
    BuildPayload --> ParallelSend{Send to Channels}
    
    ParallelSend -->|Channel 1| Jira[Create Jira Ticket]
    ParallelSend -->|Channel 2| Slack[Send Slack Message]
    
    Jira --> JiraCheck{Success?}
    JiraCheck -->|Yes| JiraLog[Log Ticket ID]
    JiraCheck -->|No| JiraRetry{Retry?}
    JiraRetry -->|No| JiraError[Log Error]
    JiraRetry -->|Yes| Jira
    
    Slack --> SlackCheck{Success?}
    SlackCheck -->|Yes| SlackLog[Log Success]
    SlackCheck -->|No| SlackRetry{Retry Once?}
    SlackRetry -->|No| SlackError[Log Error]
    SlackRetry -->|Yes| Slack
    
    JiraLog --> Complete([Complete])
    JiraError --> Complete
    SlackLog --> Complete
    SlackError --> Complete
    LogOnly --> Complete
    
    style Start fill:#f44336,color:#fff
    style Complete fill:#4caf50,color:#fff
    style CheckConf fill:#ff9800
    style ParallelSend fill:#2196f3,color:#fff
```

## Deployment Architecture

### Kubernetes Deployment

```mermaid
flowchart TB
    subgraph K8s["Kubernetes Cluster"]
        direction TB
        
        subgraph Monitoring["Monitoring Namespace"]
            PromPod[Prometheus Pod<br/>:9090]
            GrafanaPod[Grafana Pod<br/>:3000]
        end
        
        subgraph InfraGuardNS["InfraGuard Namespace"]
            IGPod[InfraGuard Pod]
            ConfigMap[ConfigMap<br/>settings.yaml]
            Secret[Secret<br/>API Credentials]
            PVC[PersistentVolumeClaim<br/>ML Models]
        end
        
        subgraph Apps["Application Namespace"]
            App1[App Pod 1]
            App2[App Pod 2]
            App3[App Pod 3]
        end
        
        ConfigMap -.->|Mount| IGPod
        Secret -.->|Mount| IGPod
        PVC -.->|Mount| IGPod
        
        App1 -->|Expose Metrics| PromPod
        App2 -->|Expose Metrics| PromPod
        App3 -->|Expose Metrics| PromPod
        
        IGPod -->|Query| PromPod
        GrafanaPod -->|Query| PromPod
    end
    
    subgraph External["External Services"]
        SlackAPI[Slack API]
        JiraAPI[Jira API]
    end
    
    IGPod -->|HTTPS| SlackAPI
    IGPod -->|HTTPS| JiraAPI
    
    style K8s fill:#e3f2fd
    style Monitoring fill:#fff3e0
    style InfraGuardNS fill:#e8f5e9
    style Apps fill:#f3e5f5
    style External fill:#fce4ec
```

### Local Development Environment

```mermaid
flowchart TB
    subgraph Docker["Docker Compose Environment"]
        direction TB
        
        subgraph Services["Services"]
            PromContainer[Prometheus Container<br/>Port: 9090]
            DummyApp[Dummy App Container<br/>Port: 8080<br/>Generates Metrics]
            IGContainer[InfraGuard Container<br/>Port: 8000]
            GrafanaContainer[Grafana Container<br/>Port: 3000]
        end
        
        subgraph Volumes["Volumes"]
            PromConfig[prometheus.yml]
            IGConfig[settings.yaml]
            Models[models/]
        end
        
        PromConfig -.->|Mount| PromContainer
        IGConfig -.->|Mount| IGContainer
        Models -.->|Mount| IGContainer
        
        DummyApp -->|Scrape /metrics| PromContainer
        IGContainer -->|Query API| PromContainer
        GrafanaContainer -->|Query API| PromContainer
    end
    
    Developer[Developer<br/>Laptop]
    Developer -->|docker-compose up| Docker
    Developer -->|View Dashboards| GrafanaContainer
    Developer -->|View Alerts| IGContainer
    
    style Docker fill:#e3f2fd
    style Services fill:#fff3e0
    style Volumes fill:#f3e5f5
```

### Component Interaction Sequence

```mermaid
sequenceDiagram
    participant Scheduler as Scheduler<br/>(1-min interval)
    participant Collector as Metrics Collector
    participant Prom as Prometheus API
    participant Formatter as Data Formatter
    participant ML as ML Detector<br/>(Isolation Forest)
    participant Forecaster as Time-Series<br/>Forecaster
    participant AlertMgr as Alert Manager
    participant Runbook as Runbook Mapper
    participant Jira as Jira API
    participant Slack as Slack Webhook
    
    loop Every 1 Minute
        Scheduler->>Collector: Trigger collection cycle
        
        Collector->>Prom: Execute PromQL queries<br/>(CPU, Memory, Error Rates)
        Prom-->>Collector: Return JSON time-series data
        
        Collector->>Formatter: Transform raw metrics
        Formatter-->>Collector: Pandas DataFrame
        
        par Anomaly Detection
            Collector->>ML: Evaluate metrics
            ML->>ML: Compute anomaly scores
            alt Normal Behavior
                ML-->>Collector: Score: 1 (Normal)
            else Anomaly Detected
                ML-->>AlertMgr: Score: -1, Confidence: 94%
            end
        and Predictive Analysis (Optional)
            Collector->>Forecaster: Historical trends
            Forecaster->>Forecaster: Generate 15-min forecast
            alt Within Normal Range
                Forecaster-->>Collector: Prediction: Normal
            else Threshold Breach Predicted
                Forecaster-->>AlertMgr: Predicted failure in 15 min
            end
        end
        
        alt Alert Triggered
            AlertMgr->>Runbook: Get runbook for metric type
            Runbook-->>AlertMgr: Runbook URL
            
            par Parallel Notifications
                AlertMgr->>Jira: Create incident ticket<br/>(Priority: High)
                Jira-->>AlertMgr: Ticket ID: INC-1045
            and
                AlertMgr->>Slack: Send formatted alert<br/>(with runbook & ticket)
                Slack-->>AlertMgr: 200 OK
            end
            
            AlertMgr->>Scheduler: Log alert delivery status
        end
    end
```

## Data Models

### Entity Relationship Diagram

```mermaid
erDiagram
    METRIC_POINT {
        datetime timestamp
        string metric_name
        float value
        string instance
        dict labels
        float rolling_mean_5m
        float rolling_std_5m
        float rate_of_change
        int hour_of_day
        int day_of_week
    }
    
    ANOMALY_RESULT {
        bool is_anomaly
        float confidence
        array scores
        int anomalous_count
        dict metadata
    }
    
    FORECAST_RESULT {
        datetime breach_time
        float breach_value
        float confidence_lower
        float confidence_upper
        array predictions
    }
    
    ALERT_PAYLOAD {
        string type
        string metric_name
        datetime timestamp
        float confidence
        string runbook_url
        string jira_ticket_id
    }
    
    METRIC_POINT ||--o{ ANOMALY_RESULT : "analyzed_by"
    METRIC_POINT ||--o{ FORECAST_RESULT : "forecasted_from"
    ANOMALY_RESULT ||--|| ALERT_PAYLOAD : "triggers"
    FORECAST_RESULT ||--|| ALERT_PAYLOAD : "triggers"
```

## Technology Stack

### Core Technologies
- **Language**: Python 3.9+
- **ML Framework**: scikit-learn (Isolation Forest)
- **Forecasting**: Facebook Prophet (optional)
- **Data Processing**: Pandas, NumPy
- **API Client**: requests, prometheus-api-client

### Infrastructure
- **Container Runtime**: Docker
- **Orchestration**: Kubernetes
- **Monitoring**: Prometheus, Grafana
- **Configuration**: YAML, environment variables

### External Integrations
- **Alerting**: Slack (webhooks), Jira (REST API)
- **Storage**: Persistent volumes for ML models

## Performance Characteristics

### Scalability
- **Single Instance**: Handles up to 100 metrics at 1-minute intervals
- **CPU**: 250m-500m (0.25-0.5 cores)
- **Memory**: 512Mi-1Gi
- **Storage**: 1-5Gi for models and logs

### Latency
- **Collection Cycle**: < 5 seconds
- **ML Inference**: < 1 second per metric
- **Alert Delivery**: < 3 seconds (parallel)

## Security Considerations

### Authentication & Authorization
- Kubernetes RBAC for pod access
- Secret management for API tokens
- Non-root container execution

### Network Security
- TLS for all external API calls
- Network policies for pod isolation
- Service mesh (optional) for mTLS

### Data Protection
- No PII in logs or metrics
- Encrypted secrets at rest
- Audit logging for alert delivery

## Operational Considerations

### Monitoring
- Self-monitoring via Prometheus metrics
- Health check endpoints
- Structured logging (JSON)

### Maintenance
- Model retraining procedures
- Configuration updates via ConfigMap
- Rolling updates for zero downtime

### Disaster Recovery
- Model backups to persistent storage
- Configuration version control
- Alert delivery retry mechanisms

---

**Document Version**: 1.0  
**Last Updated**: 2026-04-06  
**Maintained By**: InfraGuard Team
