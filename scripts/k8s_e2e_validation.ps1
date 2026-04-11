# InfraGuard Kubernetes End-to-End Validation Script
# This script deploys InfraGuard to Kubernetes and runs comprehensive validation tests

param(
    [string]$Namespace = "default",
    [switch]$CleanupFirst = $false,
    [switch]$SkipBuild = $false
)

$ErrorActionPreference = "Continue"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "InfraGuard Kubernetes End-to-End Validation" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Test counters
$totalTests = 0
$passedTests = 0
$failedTests = 0

function Test-Step {
    param(
        [string]$Name,
        [scriptblock]$Test
    )
    
    $totalTests++
    Write-Host "Test $totalTests`: $Name..." -ForegroundColor Yellow
    
    try {
        $result = & $Test
        if ($result -eq $true -or $result -eq $null) {
            Write-Host "[PASS] $Name" -ForegroundColor Green
            $script:passedTests++
            return $true
        } else {
            Write-Host "[FAIL] $Name" -ForegroundColor Red
            $script:failedTests++
            return $false
        }
    } catch {
        Write-Host "[FAIL] $Name - $_" -ForegroundColor Red
        $script:failedTests++
        return $false
    }
}

# Step 1: Check prerequisites
Write-Host "`n=== Step 1: Checking Prerequisites ===" -ForegroundColor Cyan

Test-Step "kubectl is installed" {
    $null = kubectl version --client 2>&1
    $LASTEXITCODE -eq 0
}

Test-Step "Docker is running" {
    $null = docker ps 2>&1
    $LASTEXITCODE -eq 0
}

Test-Step "Kubernetes cluster is accessible" {
    $null = kubectl cluster-info 2>&1
    $LASTEXITCODE -eq 0
}

# Step 2: Cleanup if requested
if ($CleanupFirst) {
    Write-Host "`n=== Step 2: Cleaning up existing deployment ===" -ForegroundColor Cyan
    
    Write-Host "Deleting existing InfraGuard resources..." -ForegroundColor Yellow
    kubectl delete -f k8s/ --namespace=$Namespace --ignore-not-found=true 2>&1 | Out-Null
    
    Write-Host "Waiting for cleanup to complete..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
}

# Step 3: Build Docker image
if (-not $SkipBuild) {
    Write-Host "`n=== Step 3: Building Docker Image ===" -ForegroundColor Cyan
    
    Test-Step "Build InfraGuard Docker image" {
        Write-Host "Building infraguard:latest..." -ForegroundColor Yellow
        docker build -t infraguard:latest . 2>&1 | Out-Null
        $LASTEXITCODE -eq 0
    }
} else {
    Write-Host "`n=== Step 3: Skipping Docker build ===" -ForegroundColor Cyan
}

# Step 4: Train ML model
Write-Host "`n=== Step 4: Training ML Model ===" -ForegroundColor Cyan

Test-Step "Train Isolation Forest model" {
    if (Test-Path "models/pretrained/isolation_forest.pkl") {
        Write-Host "Model already exists, skipping training" -ForegroundColor Yellow
        return $true
    }
    
    Write-Host "Training model..." -ForegroundColor Yellow
    docker-compose exec -T infraguard python scripts/train_model.py 2>&1 | Out-Null
    Test-Path "models/pretrained/isolation_forest.pkl"
}

# Step 5: Deploy to Kubernetes
Write-Host "`n=== Step 5: Deploying to Kubernetes ===" -ForegroundColor Cyan

Test-Step "Create PersistentVolumeClaim" {
    kubectl apply -f k8s/pvc.yaml --namespace=$Namespace 2>&1 | Out-Null
    $LASTEXITCODE -eq 0
}

Test-Step "Create ConfigMap" {
    kubectl apply -f k8s/configmap.yaml --namespace=$Namespace 2>&1 | Out-Null
    $LASTEXITCODE -eq 0
}

Test-Step "Create Secret" {
    kubectl apply -f k8s/secret.yaml --namespace=$Namespace 2>&1 | Out-Null
    $LASTEXITCODE -eq 0
}

Test-Step "Create Deployment and Service" {
    kubectl apply -f k8s/deployment.yaml --namespace=$Namespace 2>&1 | Out-Null
    $LASTEXITCODE -eq 0
}

# Step 6: Wait for deployment
Write-Host "`n=== Step 6: Waiting for Deployment ===" -ForegroundColor Cyan

Test-Step "Wait for pod to be ready" {
    Write-Host "Waiting for InfraGuard pod to be ready (timeout: 120s)..." -ForegroundColor Yellow
    
    $timeout = 120
    $elapsed = 0
    $interval = 5
    
    while ($elapsed -lt $timeout) {
        $podStatus = kubectl get pods -l app=infraguard --namespace=$Namespace -o jsonpath='{.items[0].status.phase}' 2>&1
        
        if ($podStatus -eq "Running") {
            $ready = kubectl get pods -l app=infraguard --namespace=$Namespace -o jsonpath='{.items[0].status.conditions[?(@.type=="Ready")].status}' 2>&1
            if ($ready -eq "True") {
                Write-Host "Pod is ready!" -ForegroundColor Green
                return $true
            }
        }
        
        Write-Host "Pod status: $podStatus (waiting...)" -ForegroundColor Yellow
        Start-Sleep -Seconds $interval
        $elapsed += $interval
    }
    
    Write-Host "Timeout waiting for pod to be ready" -ForegroundColor Red
    kubectl describe pod -l app=infraguard --namespace=$Namespace
    return $false
}

# Step 7: Verify deployment
Write-Host "`n=== Step 7: Verifying Deployment ===" -ForegroundColor Cyan

Test-Step "Pod is running" {
    $podStatus = kubectl get pods -l app=infraguard --namespace=$Namespace -o jsonpath='{.items[0].status.phase}' 2>&1
    $podStatus -eq "Running"
}

Test-Step "Service is created" {
    $service = kubectl get service infraguard --namespace=$Namespace -o jsonpath='{.metadata.name}' 2>&1
    $service -eq "infraguard"
}

Test-Step "ConfigMap is mounted" {
    $podName = kubectl get pods -l app=infraguard --namespace=$Namespace -o jsonpath='{.items[0].metadata.name}' 2>&1
    $configExists = kubectl exec $podName --namespace=$Namespace -- test -f /app/config/settings.yaml 2>&1
    $LASTEXITCODE -eq 0
}

# Step 8: Health check
Write-Host "`n=== Step 8: Health Check ===" -ForegroundColor Cyan

Test-Step "Health endpoint responds" {
    $podName = kubectl get pods -l app=infraguard --namespace=$Namespace -o jsonpath='{.items[0].metadata.name}' 2>&1
    $health = kubectl exec $podName --namespace=$Namespace -- curl -s http://localhost:8000/health 2>&1
    $health -match '"status":\s*"healthy"'
}

Test-Step "Model is loaded" {
    $podName = kubectl get pods -l app=infraguard --namespace=$Namespace -o jsonpath='{.items[0].metadata.name}' 2>&1
    $health = kubectl exec $podName --namespace=$Namespace -- curl -s http://localhost:8000/health 2>&1
    $health -match '"model_loaded":\s*true'
}

# Step 9: Check logs
Write-Host "`n=== Step 9: Checking Application Logs ===" -ForegroundColor Cyan

Test-Step "Application is collecting metrics" {
    $podName = kubectl get pods -l app=infraguard --namespace=$Namespace -o jsonpath='{.items[0].metadata.name}' 2>&1
    $logs = kubectl logs $podName --namespace=$Namespace --tail=50 2>&1
    $logs -match "Starting collection cycle" -or $logs -match "Collection cycle completed"
}

Test-Step "No critical errors in logs" {
    $podName = kubectl get pods -l app=infraguard --namespace=$Namespace -o jsonpath='{.items[0].metadata.name}' 2>&1
    $logs = kubectl logs $podName --namespace=$Namespace --tail=100 2>&1
    -not ($logs -match "CRITICAL" -or $logs -match "FATAL")
}

# Step 10: Resource usage
Write-Host "`n=== Step 10: Checking Resource Usage ===" -ForegroundColor Cyan

Test-Step "Pod memory usage is within limits" {
    $podName = kubectl get pods -l app=infraguard --namespace=$Namespace -o jsonpath='{.items[0].metadata.name}' 2>&1
    $metrics = kubectl top pod $podName --namespace=$Namespace 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Metrics server not available, skipping" -ForegroundColor Yellow
        return $true
    }
    
    # Extract memory usage (e.g., "512Mi")
    if ($metrics -match '(\d+)Mi') {
        $memoryMi = [int]$matches[1]
        Write-Host "Memory usage: ${memoryMi}Mi" -ForegroundColor Yellow
        $memoryMi -lt 2048  # Less than 2Gi limit
    } else {
        return $true
    }
}

# Step 11: Port forwarding test
Write-Host "`n=== Step 11: Testing Port Forwarding ===" -ForegroundColor Cyan

Test-Step "Port forward and access health endpoint" {
    $podName = kubectl get pods -l app=infraguard --namespace=$Namespace -o jsonpath='{.items[0].metadata.name}' 2>&1
    
    # Start port-forward in background
    $portForwardJob = Start-Job -ScriptBlock {
        param($pod, $ns)
        kubectl port-forward $pod 8000:8000 --namespace=$ns 2>&1 | Out-Null
    } -ArgumentList $podName, $Namespace
    
    Start-Sleep -Seconds 5
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 10
        $success = $response.status -eq "healthy"
    } catch {
        $success = $false
    } finally {
        Stop-Job -Job $portForwardJob
        Remove-Job -Job $portForwardJob
    }
    
    $success
}

# Step 12: Configuration validation
Write-Host "`n=== Step 12: Validating Configuration ===" -ForegroundColor Cyan

Test-Step "Prometheus URL is configured" {
    $podName = kubectl get pods -l app=infraguard --namespace=$Namespace -o jsonpath='{.items[0].metadata.name}' 2>&1
    $config = kubectl exec $podName --namespace=$Namespace -- cat /app/config/settings.yaml 2>&1
    $config -match "prometheus:"
}

Test-Step "ML thresholds are configured" {
    $podName = kubectl get pods -l app=infraguard --namespace=$Namespace -o jsonpath='{.items[0].metadata.name}' 2>&1
    $config = kubectl exec $podName --namespace=$Namespace -- cat /app/config/settings.yaml 2>&1
    $config -match "thresholds:"
}

# Summary
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "Validation Summary" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Total Tests: $totalTests" -ForegroundColor White
Write-Host "Passed: $passedTests" -ForegroundColor Green
Write-Host "Failed: $failedTests" -ForegroundColor Red
Write-Host ""

if ($failedTests -eq 0) {
    Write-Host "SUCCESS: All validation tests passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "InfraGuard is successfully deployed to Kubernetes!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. View logs: kubectl logs -f deployment/infraguard --namespace=$Namespace" -ForegroundColor White
    Write-Host "  2. Check health: kubectl port-forward deployment/infraguard 8000:8000 --namespace=$Namespace" -ForegroundColor White
    Write-Host "  3. Access health endpoint: curl http://localhost:8000/health" -ForegroundColor White
    Write-Host ""
    exit 0
} else {
    Write-Host "FAILURE: $failedTests test(s) failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Check pod status: kubectl get pods -l app=infraguard --namespace=$Namespace" -ForegroundColor White
    Write-Host "  2. View logs: kubectl logs deployment/infraguard --namespace=$Namespace" -ForegroundColor White
    Write-Host "  3. Describe pod: kubectl describe pod -l app=infraguard --namespace=$Namespace" -ForegroundColor White
    Write-Host ""
    exit 1
}
