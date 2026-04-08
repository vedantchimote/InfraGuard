# InfraGuard

AI-Powered AIOps tool for intelligent infrastructure monitoring and anomaly detection.

[![CI/CD](https://github.com/your-org/infraguard/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/your-org/infraguard/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## Overview

InfraGuard is an AI-powered monitoring solution that uses machine learning to detect anomalies in infrastructure metrics, providing intelligent alerts and actionable insights.

### Quick Links

- **Dashboard**: http://localhost:3001 (Grafana - admin/admin)
- **Health Check**: http://localhost:8000/health
- **Prometheus**: http://localhost:9090
- **Documentation**: [documentation/](documentation/)
- **Implementation Summaries**:
  - [Forecasting Feature](FORECASTING_IMPLEMENTATION.md)
  - [Grafana Dashboard](GRAFANA_IMPLEMENTATION.md)
  - [Test Suite](TESTING_IMPLEMENTATION.md)
  - [System Validation](VALIDATION_REPORT.md)

### Key Features

- **Anomaly Detection**: Isolation Forest ML algorithm for detecting unusual behavior in metrics
- **Time-Series Forecasting**: Prophet-based predictive failure analysis with configurable prediction windows
- **Intelligent Alerting**: Multi-channel alerts (Slack, Jira) with runbook integration
- **Prometheus Integration**: Seamless metric collection from Prometheus
- **Grafana Dashboard**: Real-time visualization with 8 panels for metrics and anomalies
- **Docker & Kubernetes**: Production-ready containerized deployment
- **Health Monitoring**: Built-in health check endpoint for orchestration
- **Comprehensive Testing**: Unit, integration, and property-based tests with Hypothesis
- **Configurable**: YAML-based configuration with environment variable support

## Quick Start

### Prerequisites

- Docker 20.10+ and Docker Compose
- Python 3.11+ (for local development)
- Prometheus instance (or use included dummy app)

### Using Docker Compose

```bash
# Clone the repository
git clone https://github.com/your-org/infraguard.git
cd infraguard

# Start all services (Prometheus, Grafana, dummy app, InfraGuard)
docker-compose up -d

# Check health
curl http://localhost:8000/health

# Access Grafana dashboard
# Open http://localhost:3001 (admin/admin)

# View logs
docker-compose logs -f infraguard
```

### Using Kubernetes

```bash
# Apply manifests
kubectl apply -f k8s/

# Check status
kubectl get pods -l app=infraguard

# View logs
kubectl logs -f deployment/infraguard
```

## Installation

### Local Development

```bash
# Clone repository
git clone https://github.com/your-org/infraguard.git
cd infraguard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure settings
cp config/settings.yaml.example config/settings.yaml
# Edit config/settings.yaml with your settings

# Train initial model
python scripts/train_model.py

# Run application
python main.py
```

## Configuration

Configuration is managed via `config/settings.yaml`:

```yaml
# Prometheus connection
prometheus:
  url: "http://prometheus:9090"
  timeout: 30
  queries:
    - name: "cpu_usage"
      query: "cpu_usage_percent"
      metric_type: "cpu"

# ML settings
ml:
  isolation_forest:
    n_estimators: 100
    contamination: 0.1
  model_path: "models/pretrained/isolation_forest.pkl"
  thresholds:
    cpu:
      confidence: 80
      severity_high: 95

# Alerting
alerting:
  slack:
    enabled: true
    webhook_url: "${SLACK_WEBHOOK_URL}"
  jira:
    enabled: true
    url: "${JIRA_URL}"
    project_key: "${JIRA_PROJECT_KEY}"
```

See [config/settings.yaml](config/settings.yaml) for complete configuration options.

## Architecture

InfraGuard consists of four main layers:

1. **Collection Layer**: Gathers metrics from Prometheus
2. **Intelligence Layer**: Detects anomalies using Isolation Forest ML and forecasts with Prophet
3. **Alerting Layer**: Routes alerts to Slack, Jira with runbook links
4. **Configuration Layer**: Manages settings and credentials

```
┌─────────────────────────────────────────────────────────┐
│                     InfraGuard                          │
├─────────────────────────────────────────────────────────┤
│  Collection    │  Intelligence  │  Alerting            │
│  - Prometheus  │  - Isolation   │  - Slack             │
│  - Metrics     │    Forest      │  - Jira              │
│  - Features    │  - Anomaly     │  - Runbooks          │
│                │    Detection   │                      │
│                │  - Prophet     │  Visualization       │
│                │  - Forecasting │  - Grafana           │
└─────────────────────────────────────────────────────────┘
```

## Usage

### Training a Model

```bash
# Train on last 7 days of data
python scripts/train_model.py

# Train with custom config
python scripts/train_model.py --config config/settings.yaml --days 14

# Specify output path
python scripts/train_model.py --output models/custom_model.pkl
```

### Running the Application

```bash
# Run with default config
python main.py

# Run with custom config
python main.py --config /path/to/settings.yaml

# Run with debug logging
python main.py --log-level DEBUG
```

### Health Check

```bash
# Check application health
curl http://localhost:8000/health

# Response:
{
  "status": "healthy",
  "service": "InfraGuard AIOps",
  "running": true,
  "last_collection_time": "2024-01-01T12:00:00",
  "collection_interval": 60,
  "model_loaded": true,
  "slack_enabled": true,
  "jira_enabled": true
}
```

## Project Structure

```
InfraGuard/
├── src/                        # Source code
│   ├── collector/             # Prometheus metrics collection
│   ├── ml/                    # ML models (Isolation Forest, Prophet)
│   ├── alerter/               # Alert routing (Slack, Jira)
│   ├── config/                # Configuration management
│   ├── utils/                 # Utilities (logging)
│   ├── infraguard.py          # Main application orchestrator
│   └── health_server.py       # Health check HTTP server
├── config/                     # Configuration files
│   ├── settings.yaml          # Main configuration
│   └── prometheus.yml         # Prometheus config
├── docker/                     # Docker files
│   ├── Dockerfile.dummy-app   # Dummy metrics app
│   └── dummy_app.py           # Dummy app source
├── grafana/                    # Grafana dashboard
│   ├── infraguard-dashboard.json  # Dashboard configuration
│   ├── provisioning.yaml      # Auto-provisioning config
│   ├── datasources.yaml       # Prometheus datasource
│   └── README.md              # Dashboard documentation
├── k8s/                       # Kubernetes manifests
│   ├── deployment.yaml        # Deployment and Service
│   ├── configmap.yaml         # Configuration
│   ├── secret.yaml            # Secrets template
│   └── pvc.yaml               # Persistent volume
├── scripts/                    # Utility scripts
│   ├── train_model.py         # Model training script
│   ├── test_forecasting.py    # Forecasting validation
│   ├── test_grafana.ps1       # Grafana validation (Windows)
│   ├── test_grafana.sh        # Grafana validation (Linux)
│   ├── run_tests.ps1          # Test runner (Windows)
│   ├── run_tests.sh           # Test runner (Linux)
│   └── validate_system.py     # System validation
├── tests/                      # Test suite
│   ├── test_prometheus_collector.py  # Unit tests
│   ├── test_data_formatter.py        # Unit tests
│   ├── test_isolation_forest_detector.py  # Unit tests
│   ├── test_properties.py     # Property-based tests
│   ├── test_integration.py    # Integration tests
│   └── README.md              # Test documentation
├── models/                     # ML models directory
├── logs/                       # Application logs
├── documentation/              # Mintlify documentation
├── .github/workflows/          # CI/CD pipelines
├── docker-compose.yml          # Docker Compose config
├── Dockerfile                  # Main Dockerfile
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── pytest.ini                 # Pytest configuration
├── pyproject.toml             # Package configuration
├── FORECASTING_IMPLEMENTATION.md  # Forecasting feature summary
├── GRAFANA_IMPLEMENTATION.md      # Grafana feature summary
├── TESTING_IMPLEMENTATION.md      # Testing feature summary
├── VALIDATION_REPORT.md           # System validation report
└── README.md                   # This file
```

## Documentation

Comprehensive documentation is available in the `documentation/` directory using Mintlify.

### View Interactive Documentation

```bash
cd documentation
mintlify dev
```

Then open http://localhost:3000

### Documentation Sections

- **Get Started**: Introduction, quickstart, installation
- **Core Concepts**: Architecture, anomaly detection, alerting
- **Deployment**: Docker, Kubernetes, configuration
- **Integrations**: Prometheus, Slack, Jira, Grafana
- **API Reference**: Complete API documentation
- **Guides**: Training models, custom metrics, runbooks, troubleshooting
- **Advanced**: Property testing, performance tuning, security

See [documentation/README.md](documentation/README.md) for complete structure.

## Features in Detail

### Time-Series Forecasting

InfraGuard includes optional predictive failure analysis using Facebook Prophet:

- **Proactive Alerting**: Predict threshold breaches before they occur
- **Configurable Windows**: 15 minutes to 2 hours prediction windows
- **Confidence Intervals**: Prediction reliability with upper/lower bounds
- **Seamless Integration**: Works with existing Slack/Jira alerting

Enable forecasting in `config/settings.yaml`:

```yaml
forecasting:
  enabled: true
  prediction_window: 3600  # 1 hour
  forecast_interval: 300   # Every 5 minutes
```

See [FORECASTING_IMPLEMENTATION.md](FORECASTING_IMPLEMENTATION.md) and [documentation/guides/forecasting-setup.mdx](documentation/guides/forecasting-setup.mdx) for complete details.

### Grafana Dashboard

Real-time visualization with comprehensive monitoring:

- **Time-Series Graphs**: CPU, Memory, HTTP Error Rate, Request Latency
- **Gauges**: Current values with color-coded thresholds
- **Auto-Refresh**: 30-second updates for real-time monitoring
- **Variables**: Filter by metric type and customize time ranges

Access at http://localhost:3001/d/infraguard-aiops/infraguard-aiops-dashboard

Validate dashboard:
```bash
# Windows
powershell -ExecutionPolicy Bypass -File scripts/test_grafana.ps1

# Linux/Mac
./scripts/test_grafana.sh
```

See [GRAFANA_IMPLEMENTATION.md](GRAFANA_IMPLEMENTATION.md) for complete details.

### Comprehensive Testing

Production-ready test suite with multiple testing strategies:

- **29 Tests**: Unit tests for all core components
- **8 Properties**: Universal correctness properties with Hypothesis
- **8 Integration Tests**: End-to-end workflow validation
- **Coverage Tracking**: HTML and XML reports with pytest-cov

Run tests:
```bash
# All tests
pytest tests/ -v

# With coverage
pytest --cov=src --cov-report=html

# Specific categories
./scripts/run_tests.sh unit         # Unit tests only
./scripts/run_tests.sh property     # Property-based tests
./scripts/run_tests.sh integration  # Integration tests
```

See [TESTING_IMPLEMENTATION.md](TESTING_IMPLEMENTATION.md) for complete details.

## Testing

InfraGuard includes a comprehensive test suite with 29 tests across three categories:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test types
pytest tests/test_prometheus_collector.py  # Unit tests
pytest tests/test_integration.py           # Integration tests
pytest tests/test_properties.py            # Property-based tests

# Run using test runner scripts
./scripts/run_tests.sh all        # Linux/Mac
.\scripts\run_tests.ps1 all       # Windows
```

### Test Categories

- **Unit Tests** (29 tests): PrometheusCollector, DataFormatter, IsolationForestDetector
- **Property-Based Tests** (8 properties): Universal correctness properties using Hypothesis
- **Integration Tests** (8 scenarios): End-to-end component interactions

### Test Coverage

- PrometheusCollector: 85%
- DataFormatter: 80%
- IsolationForestDetector: 86%

See [tests/README.md](tests/README.md) and [TESTING_IMPLEMENTATION.md](TESTING_IMPLEMENTATION.md) for details.

## System Validation

InfraGuard has been fully validated and is operational:

```bash
# Run comprehensive system validation
python scripts/validate_system.py
```

**Validation Results**: 7/7 checks passed (100%)

- ✅ Prometheus healthy and accessible
- ✅ Dummy metrics app generating test data
- ✅ Prometheus scraping metrics successfully
- ✅ InfraGuard health endpoint responding
- ✅ All 4 metrics available (CPU, Memory, Error Rate, Latency)
- ✅ ML model trained and loaded
- ✅ Anomaly detection active

See [VALIDATION_REPORT.md](VALIDATION_REPORT.md) for complete validation details.

## Deployment

### Docker

```bash
# Build image
docker build -t infraguard:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/models:/app/models \
  -e PROMETHEUS_URL=http://prometheus:9090 \
  infraguard:latest
```

### Kubernetes

See [k8s/README.md](k8s/README.md) for detailed Kubernetes deployment instructions.

```bash
# Quick deploy
kubectl apply -f k8s/

# Configure secrets
kubectl create secret generic infraguard-secrets \
  --from-literal=SLACK_WEBHOOK_URL='...' \
  --from-literal=JIRA_API_TOKEN='...'
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Install pre-commit hooks
pre-commit install

# Run linting
flake8 src/

# Run tests
pytest
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Update documentation
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## CI/CD

GitHub Actions workflow runs on every push and pull request:

- **Lint**: Flake8 code quality checks
- **Test**: Unit and property-based tests with coverage
- **Build**: Docker image build and test
- **Security**: Trivy vulnerability scanning

See [.github/workflows/ci.yml](.github/workflows/ci.yml) for pipeline details.

## Monitoring

InfraGuard exposes a health endpoint and integrates with Grafana for visualization:

### Health Endpoint

```bash
# Health check
curl http://localhost:8000/health

# Response includes:
{
  "status": "healthy",
  "service": "InfraGuard AIOps",
  "running": true,
  "last_collection_time": "2026-04-11T12:00:00",
  "collection_interval": 60,
  "model_loaded": true,
  "forecasting_enabled": false,
  "slack_enabled": true,
  "jira_enabled": true
}
```

### Grafana Dashboard

Access the InfraGuard dashboard at http://localhost:3001 (admin/admin):

- **8 Panels**: 4 time-series graphs, 3 gauges, 1 stat panel
- **Metrics**: CPU, Memory, HTTP Error Rate, Request Latency
- **Features**: Auto-refresh (30s), color-coded thresholds, time range filtering
- **Auto-provisioned**: Dashboard loads automatically on Grafana startup

See [grafana/README.md](grafana/README.md) and [GRAFANA_IMPLEMENTATION.md](GRAFANA_IMPLEMENTATION.md) for details.

### Prometheus Scraping

```bash
# Prometheus scrape config
- job_name: 'infraguard'
  static_configs:
    - targets: ['infraguard:8000']
  metrics_path: '/health'
```

## Troubleshooting

### Common Issues

**Model not found**
```bash
# Train a model first
python scripts/train_model.py
```

**Prometheus connection failed**
```bash
# Check Prometheus URL in config
# Verify Prometheus is accessible
curl http://prometheus:9090/api/v1/query?query=up
```

**Alerts not sending**
```bash
# Check Slack/Jira configuration
# Verify credentials in config/settings.yaml
# Check logs for error messages
docker-compose logs infraguard
```

See [documentation/guides/troubleshooting.mdx](documentation/guides/troubleshooting.mdx) for more help.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [documentation/](documentation/)
- **Issues**: [GitHub Issues](https://github.com/your-org/infraguard/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/infraguard/discussions)
- **Email**: support@infraguard.io

## Acknowledgments

Built with:
- [Prometheus](https://prometheus.io/) - Metrics collection
- [scikit-learn](https://scikit-learn.org/) - Isolation Forest ML
- [Prophet](https://facebook.github.io/prophet/) - Time-series forecasting
- [Hypothesis](https://hypothesis.readthedocs.io/) - Property-based testing
- [Grafana](https://grafana.com/) - Metrics visualization
- [Flask](https://flask.palletsprojects.com/) - HTTP server
- [Docker](https://www.docker.com/) - Containerization
- [Kubernetes](https://kubernetes.io/) - Orchestration
- [Mintlify](https://mintlify.com/) - Documentation
- [Pytest](https://pytest.org/) - Testing framework

## Roadmap

- [x] Anomaly detection with Isolation Forest
- [x] Slack and Jira integrations
- [x] Docker and Kubernetes deployment
- [x] Health check endpoint
- [x] Time-series forecasting with Prophet
- [x] Grafana dashboard with 8 visualization panels
- [x] Comprehensive test suite (unit, integration, property-based)
- [x] CI/CD pipeline with GitHub Actions
- [x] Complete Mintlify documentation
- [ ] Auto-remediation capabilities
- [ ] Additional ML algorithms (LSTM, Autoencoders)
- [ ] Custom alerting rules engine
- [ ] Multi-region deployment support
- [ ] Advanced anomaly explanations

---

Made with ❤️ by the InfraGuard team
