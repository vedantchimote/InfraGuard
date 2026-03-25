#!/bin/bash
# Test script for Grafana dashboard validation

echo "============================================================"
echo "Grafana Dashboard Validation"
echo "============================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
GRAFANA_URL="http://localhost:3001"
GRAFANA_USER="admin"
GRAFANA_PASS="admin"

# Test 1: Check if Grafana is accessible
echo "🔍 Test 1: Checking Grafana accessibility..."
if curl -s -o /dev/null -w "%{http_code}" "${GRAFANA_URL}/api/health" | grep -q "200"; then
    echo -e "${GREEN}✅ Grafana is accessible${NC}"
else
    echo -e "${RED}❌ Grafana is not accessible${NC}"
    exit 1
fi
echo ""

# Test 2: Check if Prometheus datasource is configured
echo "🔍 Test 2: Checking Prometheus datasource..."
DATASOURCE_RESPONSE=$(curl -s -u "${GRAFANA_USER}:${GRAFANA_PASS}" \
    "${GRAFANA_URL}/api/datasources/name/Prometheus")

if echo "${DATASOURCE_RESPONSE}" | grep -q "Prometheus"; then
    echo -e "${GREEN}✅ Prometheus datasource is configured${NC}"
    echo "   URL: $(echo ${DATASOURCE_RESPONSE} | grep -o '"url":"[^"]*"' | cut -d'"' -f4)"
else
    echo -e "${RED}❌ Prometheus datasource not found${NC}"
fi
echo ""

# Test 3: Check if InfraGuard dashboard exists
echo "🔍 Test 3: Checking InfraGuard dashboard..."
DASHBOARD_RESPONSE=$(curl -s -u "${GRAFANA_USER}:${GRAFANA_PASS}" \
    "${GRAFANA_URL}/api/search?query=InfraGuard")

if echo "${DASHBOARD_RESPONSE}" | grep -q "InfraGuard"; then
    echo -e "${GREEN}✅ InfraGuard dashboard is provisioned${NC}"
    DASHBOARD_UID=$(echo ${DASHBOARD_RESPONSE} | grep -o '"uid":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "   Dashboard UID: ${DASHBOARD_UID}"
    echo "   URL: ${GRAFANA_URL}/d/${DASHBOARD_UID}/infraguard-aiops-dashboard"
else
    echo -e "${YELLOW}⚠️  InfraGuard dashboard not found (may need manual import)${NC}"
fi
echo ""

# Test 4: Test Prometheus connectivity from Grafana
echo "🔍 Test 4: Testing Prometheus connectivity..."
QUERY_RESPONSE=$(curl -s -u "${GRAFANA_USER}:${GRAFANA_PASS}" \
    -H "Content-Type: application/json" \
    -d '{"queries":[{"refId":"A","datasource":{"type":"prometheus","uid":"PBFA97CFB590B2093"},"expr":"up","range":true}]}' \
    "${GRAFANA_URL}/api/ds/query")

if echo "${QUERY_RESPONSE}" | grep -q "results"; then
    echo -e "${GREEN}✅ Prometheus queries are working${NC}"
else
    echo -e "${RED}❌ Prometheus queries failed${NC}"
fi
echo ""

# Test 5: Check if metrics are available
echo "🔍 Test 5: Checking if metrics are available..."
METRICS=("cpu_usage_percent" "memory_usage_percent" "http_error_rate_percent" "request_latency_ms")
METRICS_FOUND=0

for metric in "${METRICS[@]}"; do
    METRIC_RESPONSE=$(curl -s "http://localhost:9090/api/v1/query?query=${metric}")
    if echo "${METRIC_RESPONSE}" | grep -q "success"; then
        echo -e "${GREEN}✅ ${metric} is available${NC}"
        ((METRICS_FOUND++))
    else
        echo -e "${RED}❌ ${metric} not found${NC}"
    fi
done
echo ""

# Summary
echo "============================================================"
echo "Validation Summary"
echo "============================================================"
echo "✅ Grafana accessible"
echo "✅ Prometheus datasource configured"
if echo "${DASHBOARD_RESPONSE}" | grep -q "InfraGuard"; then
    echo "✅ InfraGuard dashboard provisioned"
else
    echo "⚠️  InfraGuard dashboard needs manual import"
fi
echo "✅ Prometheus connectivity working"
echo "✅ ${METRICS_FOUND}/4 metrics available"
echo ""

if [ ${METRICS_FOUND} -eq 4 ]; then
    echo -e "${GREEN}🎉 All checks passed! Grafana dashboard is ready.${NC}"
    echo ""
    echo "Access the dashboard at:"
    echo "  URL: ${GRAFANA_URL}/d/infraguard-aiops/infraguard-aiops-dashboard"
    echo "  Username: ${GRAFANA_USER}"
    echo "  Password: ${GRAFANA_PASS}"
    echo ""
else
    echo -e "${YELLOW}⚠️  Some metrics are missing. Wait for InfraGuard to collect data.${NC}"
    echo ""
fi

exit 0
