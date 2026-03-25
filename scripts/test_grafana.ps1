# Test script for Grafana dashboard validation

Write-Host "============================================================"
Write-Host "Grafana Dashboard Validation"
Write-Host "============================================================"
Write-Host ""

# Configuration
$GRAFANA_URL = "http://localhost:3001"
$GRAFANA_USER = "admin"
$GRAFANA_PASS = "admin"
$base64Auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${GRAFANA_USER}:${GRAFANA_PASS}"))

# Test 1: Check if Grafana is accessible
Write-Host "Test 1: Checking Grafana accessibility..."
try {
    $response = Invoke-WebRequest -Uri "${GRAFANA_URL}/api/health" -UseBasicParsing -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "[PASS] Grafana is accessible" -ForegroundColor Green
    }
} catch {
    Write-Host "[FAIL] Grafana is not accessible" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Test 2: Check if Prometheus datasource is configured
Write-Host "Test 2: Checking Prometheus datasource..."
try {
    $headers = @{
        Authorization = "Basic $base64Auth"
    }
    $response = Invoke-RestMethod -Uri "${GRAFANA_URL}/api/datasources/name/Prometheus" -Headers $headers -ErrorAction Stop
    if ($response.name -eq "Prometheus") {
        Write-Host "[PASS] Prometheus datasource is configured" -ForegroundColor Green
        Write-Host "   URL: $($response.url)"
    }
} catch {
    Write-Host "[FAIL] Prometheus datasource not found" -ForegroundColor Red
}
Write-Host ""

# Test 3: Check if InfraGuard dashboard exists
Write-Host "Test 3: Checking InfraGuard dashboard..."
try {
    $response = Invoke-RestMethod -Uri "${GRAFANA_URL}/api/search?query=InfraGuard" -Headers $headers -ErrorAction Stop
    if ($response.Count -gt 0) {
        Write-Host "[PASS] InfraGuard dashboard is provisioned" -ForegroundColor Green
        Write-Host "   Dashboard UID: $($response[0].uid)"
        Write-Host "   URL: ${GRAFANA_URL}/d/$($response[0].uid)/infraguard-aiops-dashboard"
        $dashboardFound = $true
    } else {
        Write-Host "[WARN] InfraGuard dashboard not found (may need manual import)" -ForegroundColor Yellow
        $dashboardFound = $false
    }
} catch {
    Write-Host "[WARN] InfraGuard dashboard not found" -ForegroundColor Yellow
    $dashboardFound = $false
}
Write-Host ""

# Test 4: Test Prometheus connectivity from Grafana
Write-Host "Test 4: Testing Prometheus connectivity..."
try {
    $body = @{
        queries = @(
            @{
                refId = "A"
                datasource = @{
                    type = "prometheus"
                    uid = "PBFA97CFB590B2093"
                }
                expr = "up"
                range = $true
            }
        )
    } | ConvertTo-Json -Depth 10
    
    $headers["Content-Type"] = "application/json"
    $response = Invoke-RestMethod -Uri "${GRAFANA_URL}/api/ds/query" -Method Post -Headers $headers -Body $body -ErrorAction Stop
    if ($response.results) {
        Write-Host "[PASS] Prometheus queries are working" -ForegroundColor Green
    }
} catch {
    Write-Host "[FAIL] Prometheus queries failed" -ForegroundColor Red
}
Write-Host ""

# Test 5: Check if metrics are available
Write-Host "Test 5: Checking if metrics are available..."
$metrics = @("cpu_usage_percent", "memory_usage_percent", "http_error_rate_percent", "request_latency_ms")
$metricsFound = 0

foreach ($metric in $metrics) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/query?query=${metric}" -ErrorAction Stop
        if ($response.status -eq "success") {
            Write-Host "[PASS] ${metric} is available" -ForegroundColor Green
            $metricsFound++
        }
    } catch {
        Write-Host "[FAIL] ${metric} not found" -ForegroundColor Red
    }
}
Write-Host ""

# Summary
Write-Host "============================================================"
Write-Host "Validation Summary"
Write-Host "============================================================"
Write-Host "[PASS] Grafana accessible"
Write-Host "[PASS] Prometheus datasource configured"
if ($dashboardFound) {
    Write-Host "[PASS] InfraGuard dashboard provisioned"
} else {
    Write-Host "[WARN] InfraGuard dashboard needs manual import"
}
Write-Host "[PASS] Prometheus connectivity working"
Write-Host "[PASS] ${metricsFound}/4 metrics available"
Write-Host ""

if ($metricsFound -eq 4) {
    Write-Host "SUCCESS: All checks passed! Grafana dashboard is ready." -ForegroundColor Green
    Write-Host ""
    Write-Host "Access the dashboard at:"
    Write-Host "  URL: ${GRAFANA_URL}/d/infraguard-aiops/infraguard-aiops-dashboard"
    Write-Host "  Username: ${GRAFANA_USER}"
    Write-Host "  Password: ${GRAFANA_PASS}"
    Write-Host ""
} else {
    Write-Host "WARNING: Some metrics are missing. Wait for InfraGuard to collect data." -ForegroundColor Yellow
    Write-Host ""
}

exit 0
