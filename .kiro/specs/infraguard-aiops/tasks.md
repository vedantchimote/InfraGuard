# Implementation Plan: InfraGuard AIOps

## Overview

This implementation plan breaks down the InfraGuard AIOps project into actionable coding tasks following a 4-week milestone structure:
- Week 1: Collector & Local Testing Sandbox
- Week 2: ML Engine (Isolation Forest)
- Week 3: Integrations & Notifications
- Week 4: Packaging & CI/CD

Each task builds incrementally on previous work, with checkpoints to validate progress. Property-based tests are included as optional sub-tasks to validate correctness properties from the design document.

## Tasks

### Week 1: Collector & Local Testing Sandbox

- [x] 1. Set up project structure and dependencies
  - Create Python project structure with src/, tests/, models/, logs/, config/ directories
  - Create requirements.txt with dependencies: pandas, numpy, scikit-learn, prophet, requests, pyyaml, pytest, hypothesis
  - Create setup.py or pyproject.toml for package configuration
  - Initialize logging configuration
  - _Requirements: 8.1, 8.2, 11.6_

- [x] 2. Implement Prometheus metrics collector
  - [x] 2.1 Create PrometheusCollector class with HTTP client
    - Implement __init__ to load Prometheus URL, queries, and timeout from config
    - Implement execute_query method to send PromQL queries via HTTP GET
    - Implement collect_metrics method to execute all configured queries
    - Handle connection errors and timeouts with appropriate exceptions
    - _Requirements: 1.1, 1.2, 1.5_

  - [ ]* 2.2 Write property test for query execution completeness
    - **Property 3: Query Execution Completeness**
    - **Validates: Requirements 1.2**

  - [x] 2.3 Create DataFormatter class for response transformation
    - Implement format_prometheus_response to convert JSON to Pandas DataFrame
    - Implement normalize_timestamps to ensure second-level precision
    - Implement add_feature_columns to compute rolling statistics and time features
    - _Requirements: 1.3, 1.6_

  - [ ]* 2.4 Write property tests for data transformation
    - **Property 1: Prometheus Response Transformation Preserves Data**
    - **Validates: Requirements 1.3**
    - **Property 2: Timestamp Precision Preservation**
    - **Validates: Requirements 1.6**

- [x] 3. Create local development environment with Docker Compose
  - [x] 3.1 Create docker-compose.yml with Prometheus, dummy app, and InfraGuard services
    - Configure Prometheus service with port 9090
    - Configure dummy metrics-generating application with port 8080
    - Configure volume mounts for prometheus.yml and settings.yaml
    - _Requirements: 10.1, 10.4_

  - [x] 3.2 Implement dummy metrics application
    - Create simple Flask/FastAPI app that exposes /metrics endpoint
    - Generate realistic CPU, memory, and HTTP error rate patterns
    - Include periodic spikes and anomalies for testing
    - _Requirements: 10.2, 10.3_

  - [x] 3.3 Create Prometheus configuration file
    - Configure scrape targets for dummy application
    - Set scrape interval to 15 seconds
    - _Requirements: 10.4_

  - [x] 3.4 Create InfraGuard settings.yaml configuration file
    - Configure Prometheus connection settings
    - Configure PromQL queries for CPU, memory, HTTP error rates
    - Configure collection interval (60 seconds)
    - _Requirements: 8.2, 10.5_

- [ ] 4. Checkpoint - Verify metrics collection works locally
  - Run docker-compose up and verify Prometheus scrapes dummy app
  - Run collector manually and verify it retrieves metrics from Prometheus
  - Verify DataFrame output contains expected columns and data
  - Ensure all tests pass, ask the user if questions arise.

### Week 2: ML Engine (Isolation Forest)

- [x] 5. Implement configuration management
  - [x] 5.1 Create ConfigurationManager class
    - Implement _load_config to read YAML file
    - Implement _validate_config to check required fields
    - Implement get method with dot-notation support
    - Implement helper methods for section-specific configs
    - _Requirements: 8.1, 8.3, 8.4, 8.5_

  - [ ]* 5.2 Write property test for configuration validation
    - **Property 17: Configuration Validation Completeness**
    - **Validates: Requirements 8.5**

- [x] 6. Implement Isolation Forest anomaly detector
  - [x] 6.1 Create IsolationForestDetector class
    - Implement __init__ to initialize sklearn IsolationForest with config parameters
    - Implement _validate_input to check DataFrame has required feature columns
    - Implement _extract_features to convert DataFrame to numpy array
    - _Requirements: 2.1, 2.6_

  - [x] 6.2 Implement model training and persistence
    - Implement train method to fit model on historical data
    - Implement save_model to serialize model to pickle file
    - Implement load_model to deserialize model from disk
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [ ]* 6.3 Write property test for model serialization
    - **Property 7: Model Serialization Round-Trip**
    - **Validates: Requirements 3.2**

  - [x] 6.4 Implement anomaly detection logic
    - Implement detect_anomalies method to predict anomaly scores
    - Implement compute_confidence to convert scores to percentage
    - Create AnomalyResult dataclass to encapsulate results
    - _Requirements: 2.2, 2.3, 2.4_

  - [ ]* 6.5 Write property tests for anomaly detection
    - **Property 4: Anomaly Score Computation Completeness**
    - **Validates: Requirements 2.2**
    - **Property 5: Confidence Percentage Validity**
    - **Validates: Requirements 2.3**
    - **Property 6: Threshold-Based Alert Triggering**
    - **Validates: Requirements 2.4**

- [x] 7. Create model training script
  - [x] 7.1 Implement training script to generate baseline model
    - Query historical data from Prometheus (last 7 days)
    - Format and add feature columns
    - Train Isolation Forest model
    - Save trained model to models/pretrained/isolation_forest.pkl
    - _Requirements: 3.1, 3.5_

  - [ ]* 7.2 Write unit tests for training script
    - Test training with synthetic data
    - Test model file creation
    - _Requirements: 3.1_

- [x] 8. Implement optional time-series forecaster
  - [x] 8.1 Create TimeSeriesForecaster class with Prophet
    - Implement __init__ to initialize Prophet with config parameters
    - Implement _prepare_prophet_data to convert DataFrame to Prophet format
    - Implement _fit_model to train Prophet on historical data
    - _Requirements: 4.1_

  - [x] 8.2 Implement forecasting logic
    - Implement forecast method to generate predictions for prediction window
    - Implement predict_threshold_breach to check for threshold violations
    - Create ForecastResult dataclass to encapsulate predictions
    - _Requirements: 4.2, 4.3, 4.4_

  - [ ]* 8.3 Write property tests for forecasting
    - **Property 8: Forecast Prediction Window Coverage**
    - **Validates: Requirements 4.2**
    - **Property 9: Forecast Threshold Breach Detection**
    - **Validates: Requirements 4.3**
    - **Property 10: Forecast Confidence Intervals Presence**
    - **Validates: Requirements 4.4**

- [ ] 9. Checkpoint - Verify ML detection works end-to-end
  - Train model on historical data from local Prometheus
  - Run detector on live metrics and verify anomaly scores are computed
  - Inject anomalies in dummy app and verify detector identifies them
  - Ensure all tests pass, ask the user if questions arise.

### Week 3: Integrations & Notifications

- [x] 10. Implement runbook mapper
  - [x] 10.1 Create RunbookMapper class
    - Implement __init__ to load runbook mappings from config
    - Implement get_runbook to retrieve URL for metric and anomaly type
    - Implement fallback logic to return default URL when no mapping exists
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [ ]* 10.2 Write property test for runbook resolution
    - **Property 16: Runbook Resolution with Fallback**
    - **Validates: Requirements 7.2, 7.4**

- [x] 11. Implement Slack notifier
  - [x] 11.1 Create SlackNotifier class
    - Implement __init__ to load webhook URL and channel from config
    - Implement send_message to POST formatted messages to Slack webhook
    - Implement _retry_send for retry logic with 10-second delay
    - _Requirements: 6.1, 6.5_

  - [x] 11.2 Implement Slack message formatting
    - Implement _format_anomaly_message with blocks formatting
    - Implement _format_prediction_message for forecast alerts
    - Include severity emojis, confidence, metric details, Jira ticket ID, runbook URL
    - _Requirements: 6.2, 6.3, 6.4, 6.6_

  - [ ]* 11.3 Write property tests for Slack formatting
    - **Property 11: Alert Payload Completeness**
    - **Validates: Requirements 6.2**
    - **Property 13: Contextual Links in Alerts**
    - **Validates: Requirements 6.3**
    - **Property 14: Severity-Based Message Formatting**
    - **Validates: Requirements 6.4**
    - **Property 15: Prediction Window in Forecast Alerts**
    - **Validates: Requirements 6.6**

- [x] 12. Implement Jira notifier
  - [x] 12.1 Create JiraNotifier class
    - Implement __init__ to load API URL, project key, credentials from config
    - Implement create_ticket to POST issue creation via Jira REST API v3
    - Implement HTTP Basic Auth with username and API token
    - _Requirements: 5.1, 5.5_

  - [x] 12.2 Implement Jira ticket formatting
    - Implement _format_anomaly_ticket with priority mapping
    - Implement _format_prediction_ticket for forecast alerts
    - Include metric details, confidence, runbook URL, Prometheus graph links
    - _Requirements: 5.2, 5.3, 5.4, 5.6_

  - [ ]* 12.3 Write property tests for Jira formatting
    - **Property 11: Alert Payload Completeness**
    - **Validates: Requirements 5.3**
    - **Property 12: Priority Mapping Consistency**
    - **Validates: Requirements 5.2**
    - **Property 13: Contextual Links in Alerts**
    - **Validates: Requirements 5.6**

- [x] 13. Implement alert manager orchestration
  - [x] 13.1 Create AlertManager class
    - Implement __init__ to initialize SlackNotifier, JiraNotifier, RunbookMapper
    - Implement _build_alert_payload to create standardized payload structure
    - Implement _log_alert_delivery to record delivery status
    - _Requirements: 11.2_

  - [x] 13.2 Implement alert routing logic
    - Implement send_alert for anomaly-based alerts
    - Implement send_forecast_alert for prediction-based alerts
    - Create AlertStatus dataclass to track delivery results
    - Send to Jira first to get ticket ID, then include in Slack message
    - Handle errors gracefully and continue with other channels
    - _Requirements: 5.1, 6.1, 11.2_

  - [ ]* 13.3 Write property test for alert delivery logging
    - **Property 19: Alert Delivery Status Logging**
    - **Validates: Requirements 11.2**

- [ ] 14. Checkpoint - Verify integrations work end-to-end
  - Configure Slack webhook and Jira credentials in settings.yaml
  - Trigger test anomaly and verify Jira ticket is created
  - Verify Slack message is sent with correct formatting and ticket ID
  - Verify runbook URLs are included in both notifications
  - Ensure all tests pass, ask the user if questions arise.

### Week 4: Packaging & CI/CD

- [x] 15. Implement main application orchestrator
  - [x] 15.1 Create InfraGuard main class
    - Implement __init__ to initialize all components (collector, detector, forecaster, alert manager)
    - Implement _setup_logging to configure logging from config
    - Implement _signal_handler for graceful shutdown on SIGTERM/SIGINT
    - Load pre-trained model at startup
    - _Requirements: 9.5, 11.6_

  - [x] 15.2 Implement main collection loop
    - Implement run method with collection interval timing
    - Implement _execute_collection_cycle to orchestrate metrics collection, detection, alerting
    - Implement _execute_forecasting for optional time-series predictions
    - Handle errors gracefully with logging and continue operation
    - _Requirements: 1.4, 2.4, 11.3, 11.4_

  - [ ]* 15.3 Write property test for anomaly detection logging
    - **Property 18: Anomaly Detection Logging Completeness**
    - **Validates: Requirements 11.1**

  - [x] 15.3 Create main.py entry point
    - Implement main function to instantiate InfraGuard and call run
    - Handle ConfigurationError and exit with non-zero status
    - Handle KeyboardInterrupt for clean shutdown
    - _Requirements: 8.3, 8.4_

- [x] 16. Create health check endpoint
  - [x] 16.1 Implement HTTP health check server
    - Create simple HTTP server (Flask/FastAPI) on port 8000
    - Expose /health endpoint that returns 200 OK
    - Include health status: last collection time, model loaded status
    - _Requirements: 11.5_

  - [ ]* 16.2 Write integration tests for health endpoint
    - Test endpoint returns 200 when application is healthy
    - Test endpoint includes expected status fields
    - _Requirements: 11.5_

- [x] 17. Create Docker container
  - [x] 17.1 Create Dockerfile
    - Use Python 3.11 slim base image
    - Copy source code and install dependencies
    - Create non-root user for security
    - Set CMD to run main.py
    - _Requirements: 9.1, 9.4_

  - [x] 17.2 Support configuration injection
    - Support environment variable substitution in settings.yaml
    - Support mounting settings.yaml as volume
    - Support mounting models/ directory as volume
    - _Requirements: 9.2, 9.3_

  - [x] 17.3 Test Docker image locally
    - Build image and verify it starts successfully
    - Test with docker-compose environment
    - Verify graceful shutdown on SIGTERM
    - _Requirements: 9.5_

- [x] 18. Create Kubernetes deployment manifests
  - [x] 18.1 Create Kubernetes Deployment
    - Define Deployment with InfraGuard container
    - Configure resource requests and limits
    - Configure liveness and readiness probes using /health endpoint
    - _Requirements: 9.1, 11.5_

  - [x] 18.2 Create ConfigMap and Secret
    - Create ConfigMap for settings.yaml
    - Create Secret for Jira API token and Slack webhook URL
    - Mount ConfigMap and Secret as volumes
    - _Requirements: 9.2, 9.3_

  - [x] 18.3 Create PersistentVolumeClaim for models
    - Define PVC for models/ directory
    - Mount PVC to InfraGuard pod
    - _Requirements: 9.3_

- [x] 19. Create Grafana dashboard
  - [x] 19.1 Create dashboard JSON configuration
    - Define panels for monitored metrics with time-series graphs
    - Define panel for recent anomaly detections
    - Define panel for alert delivery status
    - Support filtering by metric type and time range
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

  - [ ]* 19.2 Write integration tests for dashboard
    - Test dashboard can be imported into Grafana
    - Test panels query correct data sources
    - _Requirements: 12.1_

- [x] 20. Create CI/CD pipeline
  - [x] 20.1 Create GitHub Actions workflow
    - Configure workflow to trigger on push and pull request
    - Add job for Python linting with Flake8
    - Add job for running unit tests with Pytest
    - Add job for running property-based tests with Hypothesis
    - Add job for building Docker image
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

  - [x] 20.2 Configure test coverage reporting
    - Add pytest-cov to requirements
    - Configure coverage reporting in CI
    - Set minimum coverage threshold
    - _Requirements: 13.6_

  - [ ]* 20.3 Write integration tests for CI pipeline
    - Test linting catches common issues
    - Test unit tests execute successfully
    - Test Docker build succeeds
    - _Requirements: 13.1, 13.2, 13.3, 13.4_

- [x] 21. Create documentation
  - [x] 21.1 Create README.md
    - Document project overview and features
    - Document installation and setup instructions
    - Document configuration options
    - Document deployment instructions (Docker, Kubernetes)
    - Include architecture diagram

  - [x] 21.2 Create API documentation
    - Document all public classes and methods with docstrings
    - Generate API documentation with Sphinx or pdoc
    - Document configuration schema

  - [x] 21.3 Create runbook templates
    - Create example runbook for CPU spike remediation
    - Create example runbook for memory leak remediation
    - Create example runbook for HTTP error rate remediation

- [x] 22. Final checkpoint - End-to-end validation
  - Deploy InfraGuard to local Kubernetes cluster (kind/minikube)
  - Verify metrics collection from Prometheus
  - Inject anomalies and verify detection
  - Verify Jira tickets are created
  - Verify Slack notifications are sent
  - Verify Grafana dashboard displays data
  - Run full test suite including property-based tests
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- Integration tests validate component interactions
- The 4-week structure allows for parallel work on different components
- Configuration management is implemented early to support all other components
- Local development environment enables rapid iteration and testing
- Docker and Kubernetes deployment ensures production-ready packaging
