#!/bin/bash
# Test runner script for InfraGuard

set -e

echo "============================================================"
echo "InfraGuard Test Suite"
echo "============================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
TEST_TYPE="${1:-all}"

case "$TEST_TYPE" in
    unit)
        echo -e "${YELLOW}Running unit tests...${NC}"
        pytest tests/test_prometheus_collector.py tests/test_data_formatter.py tests/test_isolation_forest_detector.py -v
        ;;
    integration)
        echo -e "${YELLOW}Running integration tests...${NC}"
        pytest tests/test_integration.py -v
        ;;
    property)
        echo -e "${YELLOW}Running property-based tests...${NC}"
        pytest tests/test_properties.py -v
        ;;
    coverage)
        echo -e "${YELLOW}Running tests with coverage...${NC}"
        pytest --cov=src --cov-report=term-missing --cov-report=html
        echo ""
        echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
        ;;
    all)
        echo -e "${YELLOW}Running all tests...${NC}"
        pytest tests/ -v
        ;;
    *)
        echo "Usage: $0 {unit|integration|property|coverage|all}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Tests completed!${NC}"
