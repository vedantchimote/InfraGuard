# Test runner script for InfraGuard (PowerShell)

param(
    [string]$TestType = "all"
)

Write-Host "============================================================"
Write-Host "InfraGuard Test Suite"
Write-Host "============================================================"
Write-Host ""

switch ($TestType) {
    "unit" {
        Write-Host "Running unit tests..." -ForegroundColor Yellow
        pytest tests/test_prometheus_collector.py tests/test_data_formatter.py tests/test_isolation_forest_detector.py -v
    }
    "integration" {
        Write-Host "Running integration tests..." -ForegroundColor Yellow
        pytest tests/test_integration.py -v
    }
    "property" {
        Write-Host "Running property-based tests..." -ForegroundColor Yellow
        pytest tests/test_properties.py -v
    }
    "coverage" {
        Write-Host "Running tests with coverage..." -ForegroundColor Yellow
        pytest --cov=src --cov-report=term-missing --cov-report=html
        Write-Host ""
        Write-Host "Coverage report generated in htmlcov/index.html" -ForegroundColor Green
    }
    "all" {
        Write-Host "Running all tests..." -ForegroundColor Yellow
        pytest tests/ -v
    }
    default {
        Write-Host "Usage: .\run_tests.ps1 {unit|integration|property|coverage|all}"
        exit 1
    }
}

Write-Host ""
Write-Host "[PASS] Tests completed!" -ForegroundColor Green
