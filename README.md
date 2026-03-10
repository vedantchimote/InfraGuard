# InfraGuard

AI-Powered AIOps tool for intelligent infrastructure monitoring and anomaly detection.

[![CI/CD](https://github.com/your-org/infraguard/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/your-org/infraguard/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## Overview

InfraGuard is an AI-powered monitoring solution that uses machine learning to detect anomalies in infrastructure metrics, providing intelligent alerts and actionable insights.

### Key Features

- **Anomaly Detection**: Isolation Forest ML algorithm for detecting unusual behavior in metrics
- **Intelligent Alerting**: Multi-channel alerts (Slack, Jira) with runbook integration
- **Prometheus Integration**: Seamless metric collection from Prometheus
- **Docker & Kubernetes**: Production-ready containerized deployment
- **Health Monitoring**: Built-in health check endpoint for orchestration
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

# Start all services (Prometheus, dummy app, InfraGuard)
docker-compose up -d

# Check health
curl http://localhost:8000/health

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
2. **Intelligence Layer**: Detects anomalies using Isolation Forest ML
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
│   ├── ml/                    # ML models (Isolation Forest)
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
├── k8s/                       # Kubernetes manifests
│   ├── deployment.yaml        # Deployment and Service
│   ├── configmap.yaml         # Configuration
│   ├── secret.yaml            # Secrets template
│   └── pvc.yaml               # Persistent volume
├── scripts/                    # Utility scripts
│   └── train_model.py         # Model training script
├── tests/                      # Test suite
├── models/                     # ML models directory
├── logs/                       # Application logs
├── documentation/              # Mintlify documentation
├── .github/workflows/          # CI/CD pipelines
├── docker-compose.yml          # Docker Compose config
├── Dockerfile                  # Main Dockerfile
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Package configuration
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

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test types
pytest tests/unit/              # Unit tests
pytest tests/integration/       # Integration tests
pytest -m property              # Property-based tests
```

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

InfraGuard exposes a health endpoint for monitoring:

```bash
# Health check
curl http://localhost:8000/health

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
- [Flask](https://flask.palletsprojects.com/) - HTTP server
- [Docker](https://www.docker.com/) - Containerization
- [Kubernetes](https://kubernetes.io/) - Orchestration
- [Mintlify](https://mintlify.com/) - Documentation

## Roadmap

- [x] Anomaly detection with Isolation Forest
- [x] Slack and Jira integrations
- [x] Docker and Kubernetes deployment
- [x] Health check endpoint
- [ ] Time-series forecasting with Prophet
- [ ] Grafana dashboard
- [ ] Auto-remediation capabilities
- [ ] Additional ML algorithms (LSTM, Autoencoders)
- [ ] Custom alerting rules engine

---

Made with ❤️ by the InfraGuard team
