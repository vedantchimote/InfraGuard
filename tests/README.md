# InfraGuard Test Suite

This directory contains comprehensive tests for the InfraGuard AIOps platform, including unit tests, integration tests, and property-based tests.

## Test Structure

```
tests/
├── __init__.py                          # Test package initialization
├── test_prometheus_collector.py        # Unit tests for Prometheus collector
├── test_data_formatter.py               # Unit tests for data formatter
├── test_isolation_forest_detector.py    # Unit tests for ML detector
├── test_properties.py                   # Property-based tests (Hypothesis)
├── test_integration.py                  # Integration tests
└── README.md                            # This file
```

## Test Categories

### Unit Tests

Unit tests validate individual components in isolation using mocks and fixtures.

**Files**:
- `test_prometheus_collector.py`: Tests Prometheus API interaction, query execution, error handling
- `test_data_formatter.py`: Tests data transformation, timestamp normalization, feature engineering
- `test_isolation_forest_detector.py`: Tests model training, anomaly detection, persistence

**Run unit tests**:
```bash
# All unit tests
pytest tests/test_*.py -v

# Specific component
pytest tests/test_prometheus_collector.py -v
```

### Integration Tests

Integration tests validate interactions between multiple components and end-to-end workflows.

**File**: `test_integration.py`

**Test Scenarios**:
- Collector + Formatter integration
- ML training and detection pipeline
- Model persistence workflow
- Alerting component integration
- Health endpoint functionality
- Configuration management
- Complete end-to-end workflow

**Run integration tests**:
```bash
pytest tests/test_integration.py -v
```

### Property-Based Tests

Property-based tests use Hypothesis to validate universal properties that should hold for all valid inputs.

**File**: `test_properties.py`

**Properties Tested**:
1. **Property 1**: Prometheus Response Transformation Preserves Data
2. **Property 2**: Timestamp Precision Preservation
3. **Property 4**: Anomaly Score Computation Completeness
4. **Property 5**: Confidence Percentage Validity
5. **Property 6**: Threshold-Based Alert Triggering
6. **Property 16**: Runbook Resolution with Fallback
7. **Property 17**: Configuration Validation Completeness

**Run property tests**:
```bash
pytest tests/test_properties.py -v
```

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install -r requirements.txt
```

Required packages:
- pytest
- pytest-cov
- hypothesis
- pytest-mock

### Run All Tests

```bash
# Using pytest directly
pytest tests/ -v

# Using test runner script (Linux/Mac)
chmod +x scripts/run_tests.sh
./scripts/run_tests.sh all

# Using test runner script (Windows)
powershell -ExecutionPolicy Bypass -File scripts/run_tests.ps1 all
```

### Run Specific Test Categories

**Unit tests only**:
```bash
./scripts/run_tests.sh unit
```

**Integration tests only**:
```bash
./scripts/run_tests.sh integration
```

**Property-based tests only**:
```bash
./scripts/run_tests.sh property
```

### Run with Coverage

```bash
# Generate coverage report
./scripts/run_tests.sh coverage

# View HTML coverage report
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Run Specific Tests

```bash
# Run single test file
pytest tests/test_prometheus_collector.py -v

# Run single test class
pytest tests/test_prometheus_collector.py::TestPrometheusCollector -v

# Run single test method
pytest tests/test_prometheus_collector.py::TestPrometheusCollector::test_initialization -v

# Run tests matching pattern
pytest tests/ -k "test_collect" -v
```

## Test Configuration

### pytest.ini

Configuration file for pytest with settings for:
- Test discovery patterns
- Output formatting
- Coverage reporting
- Hypothesis statistics
- Test markers

### Markers

Tests can be marked with custom markers:

```python
@pytest.mark.unit
def test_something():
    pass

@pytest.mark.integration
def test_integration():
    pass

@pytest.mark.property
def test_property():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass
```

Run tests by marker:
```bash
pytest -m unit  # Run only unit tests
pytest -m "not slow"  # Skip slow tests
```

## Writing Tests

### Unit Test Example

```python
import pytest
from unittest.mock import Mock, patch

class TestMyComponent:
    @pytest.fixture
    def component(self):
        return MyComponent(config={})
    
    def test_something(self, component):
        result = component.do_something()
        assert result == expected_value
    
    @patch('module.external_call')
    def test_with_mock(self, mock_call, component):
        mock_call.return_value = "mocked"
        result = component.use_external()
        assert result == "mocked"
```

### Property-Based Test Example

```python
from hypothesis import given, strategies as st

class TestProperties:
    @given(
        value=st.integers(min_value=0, max_value=100),
        threshold=st.integers(min_value=0, max_value=100)
    )
    def test_property(self, value, threshold):
        result = check_threshold(value, threshold)
        # Property: result should be boolean
        assert isinstance(result, bool)
```

### Integration Test Example

```python
class TestIntegration:
    def test_workflow(self):
        # Setup components
        collector = Collector(config)
        processor = Processor()
        
        # Execute workflow
        data = collector.collect()
        result = processor.process(data)
        
        # Verify end-to-end behavior
        assert result.is_valid()
```

## Test Coverage

### Current Coverage

Run coverage report to see current test coverage:
```bash
pytest --cov=src --cov-report=term-missing
```

### Coverage Goals

- **Overall**: > 80%
- **Critical paths**: > 90%
- **Unit tests**: Cover all public methods
- **Integration tests**: Cover main workflows
- **Property tests**: Cover universal properties

### Viewing Coverage

**Terminal report**:
```bash
pytest --cov=src --cov-report=term-missing
```

**HTML report**:
```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

**XML report** (for CI/CD):
```bash
pytest --cov=src --cov-report=xml
```

## Continuous Integration

Tests are automatically run in CI/CD pipeline on:
- Every push to main branch
- Every pull request
- Scheduled nightly builds

### CI Configuration

See `.github/workflows/ci.yml` for CI configuration.

**CI Jobs**:
1. Linting (Flake8)
2. Unit tests
3. Integration tests
4. Property-based tests
5. Coverage reporting

## Troubleshooting

### Tests Failing Locally

1. **Check dependencies**:
```bash
pip install -r requirements.txt
```

2. **Clear pytest cache**:
```bash
pytest --cache-clear
```

3. **Run with verbose output**:
```bash
pytest -vv
```

4. **Check for import errors**:
```bash
python -c "import src.collector.prometheus_collector"
```

### Hypothesis Tests Timing Out

Reduce number of examples:
```python
@given(value=st.integers())
@settings(max_examples=10)  # Reduce from default 100
def test_property(value):
    pass
```

### Mock Not Working

Ensure correct import path:
```python
# If module imports: from requests import get
@patch('module.get')  # Patch where it's used

# If module imports: import requests
@patch('requests.get')  # Patch at source
```

## Best Practices

1. **Test Naming**: Use descriptive names that explain what is being tested
2. **Fixtures**: Use fixtures for common setup/teardown
3. **Mocking**: Mock external dependencies (HTTP, database, filesystem)
4. **Assertions**: Use specific assertions with clear error messages
5. **Coverage**: Aim for high coverage but focus on critical paths
6. **Speed**: Keep unit tests fast (< 1s each)
7. **Independence**: Tests should not depend on each other
8. **Documentation**: Add docstrings explaining complex test scenarios

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain or improve coverage
4. Add integration tests for new workflows
5. Consider property-based tests for universal properties
6. Update this README if adding new test categories

## Support

For issues or questions about tests:
- Check test output for error messages
- Review test documentation above
- Check CI logs for failures
- Open an issue on GitHub
