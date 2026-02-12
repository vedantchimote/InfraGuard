# InfraGuard

AI-Powered AIOps tool for intelligent infrastructure monitoring and anomaly detection.

## Overview

InfraGuard is an AI-powered monitoring solution that uses machine learning to detect anomalies, forecast trends, and send intelligent alerts for your infrastructure.

### Key Features

- **Anomaly Detection**: Isolation Forest ML algorithm for detecting unusual behavior
- **Time Series Forecasting**: Prophet-based predictions for capacity planning
- **Intelligent Alerting**: Multi-channel alerts with smart deduplication
- **Prometheus Integration**: Seamless metric collection from Prometheus
- **Multiple Integrations**: Slack, Jira, PagerDuty, Grafana support

## Quick Start

### Using Docker Compose

```bash
# Download docker-compose.yml
curl -O https://raw.githubusercontent.com/your-org/infraguard/main/docker-compose.yml

# Start services
docker-compose up -d

# Verify
curl http://localhost:8000/health
```

### Using Kubernetes

```bash
# Apply manifests
kubectl apply -f k8s/

# Check status
kubectl get pods -n infraguard
```

## Documentation

All documentation is located in the `documentation/` directory.

### View Interactive Documentation

```bash
cd documentation
mintlify dev
```

Then open http://localhost:3000

### Documentation Structure

- **Get Started**: Introduction, quickstart, installation
- **Core Concepts**: Architecture, anomaly detection, forecasting, alerting
- **Deployment**: Docker, Kubernetes, configuration
- **Integrations**: Prometheus, Slack, Jira, Grafana
- **API Reference**: Complete API documentation
- **Guides**: Training models, custom metrics, runbooks, troubleshooting
- **Advanced**: Property testing, performance tuning, security, monitoring

See [documentation/README.md](documentation/README.md) for complete documentation structure.

## Project Structure

```
InfraGuard/
├── .kiro/                      # Kiro specs and configuration
│   └── specs/
│       └── infraguard-aiops/   # Project specifications
├── documentation/              # All documentation (see documentation/README.md)
│   ├── concepts/              # Core concepts
│   ├── deployment/            # Deployment guides
│   ├── integrations/          # Integration guides
│   ├── api-reference/         # API documentation
│   ├── guides/                # How-to guides
│   ├── advanced/              # Advanced topics
│   ├── technical-docs/        # Technical markdown docs
│   └── logo/                  # Brand assets
└── README.md                   # This file
```

## Development

### Prerequisites

- Docker 20.10+
- Python 3.9+
- Node.js 16+ (for documentation)

### Local Development

1. Clone the repository
2. Set up environment variables
3. Start services with Docker Compose
4. Access API at http://localhost:8000

### Documentation Development

```bash
cd documentation
npm install -g mintlify
mintlify dev
```

## Configuration

Configuration is managed via `config.yaml`. See [documentation/deployment/configuration.mdx](documentation/deployment/configuration.mdx) for details.

Example:

```yaml
collector:
  prometheus:
    url: "http://prometheus:9090"
    scrape_interval: 60s

detector:
  algorithm: "isolation_forest"
  thresholds:
    anomaly_score: 0.7

alerting:
  enabled: true
  routing:
    - name: "critical_alerts"
      severity: "critical"
      channels:
        - type: "slack"
          channel: "#ops-alerts"
```

## Architecture

InfraGuard consists of four main components:

1. **Collector**: Gathers metrics from Prometheus
2. **Detector**: Detects anomalies using Isolation Forest
3. **Forecaster**: Predicts future trends using Prophet
4. **Alerter**: Routes alerts to multiple channels

See [documentation/concepts/architecture.mdx](documentation/concepts/architecture.mdx) for detailed architecture.

## API

RESTful API available at `http://localhost:8000/api`

Key endpoints:
- `/api/collector/metrics` - Metric collection
- `/api/detector/detect` - Anomaly detection
- `/api/forecaster/predict` - Time series forecasting
- `/api/alerter/alert` - Alert management

See [documentation/api-reference/](documentation/api-reference/) for complete API documentation.

## Testing

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run property-based tests
pytest tests/property/
```

See [documentation/technical-docs/TESTING.md](documentation/technical-docs/TESTING.md) for testing strategy.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Submit a pull request

## License

[Your License Here]

## Support

- **Documentation**: [documentation/](documentation/)
- **Issues**: [GitHub Issues](https://github.com/your-org/infraguard/issues)
- **Community**: [Slack](https://slack.infraguard.io)
- **Email**: support@infraguard.io

## Roadmap

- [ ] Auto-remediation capabilities
- [ ] Distributed training for ML models
- [ ] Additional ML algorithms (LSTM, Autoencoders)
- [ ] Custom alerting rules engine
- [ ] Multi-cloud support

## Acknowledgments

Built with:
- [Prometheus](https://prometheus.io/) - Metrics collection
- [scikit-learn](https://scikit-learn.org/) - Isolation Forest
- [Prophet](https://facebook.github.io/prophet/) - Time series forecasting
- [FastAPI](https://fastapi.tiangolo.com/) - API framework
- [Mintlify](https://mintlify.com/) - Documentation
