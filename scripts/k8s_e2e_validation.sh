#!/bin/bash
# InfraGuard Kubernetes End-to-End Validation Script
# This script deploys InfraGuard to Kubernetes and runs comprehensive validation tests

set +e  # Don't exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
NAMESPACE="default"
CLEANUP_FIRST=false
SKIP_BUILD=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        --cleanup)
            CLEANUP_FIRST=true
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}InfraGuard Kubernetes End-to-End Validation${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""

test_step() {
    local name="$1"
    local command="$2"
    
    ((TOTAL_TESTS++))
    echo -e "${YELLOW}Test $TOTAL_TESTS: $name...${NC}"
    
    if eval "$command"; then
        echo -e "${GREEN}[PASS] $name${NC}"
        ((PASSED_TESTS++))
        return 0
    else
        echo -e "${RED}[FAIL] $name${NC}"
        ((FAILED_TESTS++))
        return 1
    fi
}

# Step 1: Check prerequisites
echo -e "\n${CYAN}=== Step 1: Checking Prerequisites ===${NC}"

test_step "kubectl is installed" "kubectl version --client &>/dev/null"
test_step "Docker is running" "docker ps &>/dev/null"
test_step "Kubernetes cluster is accessible" "kubectl cluster-info &>/dev/null"

# Step 2: Cleanup if requested
if [ "$CLEANUP_FIRST" = true ]; then
    echo -e "\n${CYAN}=== Step 2: Cleaning up existing deployment ===${NC}"
    
    echo -e "${YELLOW}Deleting existing InfraGuard resources...${NC}"
    kubectl delete -f k8s/ --namespace=$NAMESPACE --ignore-not-found=true &>/dev/null
    
    echo -e "${YELLOW}Waiting for cleanup to complete...${NC}"
    sleep 10
fi

# Step 3: Build Docker image
if [ "$SKIP_BUILD" = false ]; then
    echo -e "\n${CYAN}=== Step 3: Building Docker Image ===${NC}"
    
    test_step "Build InfraGuard Docker image" "docker build -t infraguard:latest . &>/dev/null"
else
    echo -e "\n${CYAN}=== Step 3: Skipping Docker build ===${NC}"
fi

# Step 4: Train ML model
echo -e "\n${CYAN}=== Step 4: Training ML Model ===${NC}"

test_step "Train Isolation Forest model" "
    if [ -f 'models/pretrained/isolation_forest.pkl' ]; then
        echo 'Model already exists, skipping training'
        exit 0
    fi
    
    echo 'Training model...'
    docker-compose exec -T infraguard python scripts/train_model.py &>/dev/null
    [ -f 'models/pretrained/isolation_forest.pkl' ]
"

# Step 5: Deploy to Kubernetes
echo -e "\n${CYAN}=== Step 5: Deploying to Kubernetes ===${NC}"

test_step "Create PersistentVolumeClaim" "kubectl apply -f k8s/pvc.yaml --namespace=$NAMESPACE &>/dev/null"
test_step "Create ConfigMap" "kubectl apply -f k8s/configmap.yaml --namespace=$NAMESPACE &>/dev/null"
test_step "Create Secret" "kubectl apply -f k8s/secret.yaml --namespace=$NAMESPACE &>/dev/null"
test_step "Create Deployment and Service" "kubectl apply -f k8s/deployment.yaml --namespace=$NAMESPACE &>/dev/null"

# Step 6: Wait for deployment
echo -e "\n${CYAN}=== Step 6: Waiting for Deployment ===${NC}"

test_step "Wait for pod to be ready" "
    echo 'Waiting for InfraGuard pod to be ready (timeout: 120s)...'
    
    timeout=120
    elapsed=0
    interval=5
    
    while [ \$elapsed -lt \$timeout ]; do
        pod_status=\$(kubectl get pods -l app=infraguard --namespace=$NAMESPACE -o jsonpath='{.items[0].status.phase}' 2>/dev/null)
        
        if [ \"\$pod_status\" = \"Running\" ]; then
            ready=\$(kubectl get pods -l app=infraguard --namespace=$NAMESPACE -o jsonpath='{.items[0].status.conditions[?(@.type==\"Ready\")].status}' 2>/dev/null)
            if [ \"\$ready\" = \"True\" ]; then
                echo 'Pod is ready!'
                exit 0
            fi
        fi
        
        echo \"Pod status: \$pod_status (waiting...)\"
        sleep \$interval
        elapsed=\$((elapsed + interval))
    done
    
    echo 'Timeout waiting for pod to be ready'
    kubectl describe pod -l app=infraguard --namespace=$NAMESPACE
    exit 1
"

# Step 7: Verify deployment
echo -e "\n${CYAN}=== Step 7: Verifying Deployment ===${NC}"

test_step "Pod is running" "
    pod_status=\$(kubectl get pods -l app=infraguard --namespace=$NAMESPACE -o jsonpath='{.items[0].status.phase}' 2>/dev/null)
    [ \"\$pod_status\" = \"Running\" ]
"

test_step "Service is created" "
    service=\$(kubectl get service infraguard --namespace=$NAMESPACE -o jsonpath='{.metadata.name}' 2>/dev/null)
    [ \"\$service\" = \"infraguard\" ]
"

test_step "ConfigMap is mounted" "
    pod_name=\$(kubectl get pods -l app=infraguard --namespace=$NAMESPACE -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    kubectl exec \$pod_name --namespace=$NAMESPACE -- test -f /app/config/settings.yaml &>/dev/null
"

# Step 8: Health check
echo -e "\n${CYAN}=== Step 8: Health Check ===${NC}"

test_step "Health endpoint responds" "
    pod_name=\$(kubectl get pods -l app=infraguard --namespace=$NAMESPACE -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    health=\$(kubectl exec \$pod_name --namespace=$NAMESPACE -- curl -s http://localhost:8000/health 2>/dev/null)
    echo \"\$health\" | grep -q '\"status\".*\"healthy\"'
"

test_step "Model is loaded" "
    pod_name=\$(kubectl get pods -l app=infraguard --namespace=$NAMESPACE -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    health=\$(kubectl exec \$pod_name --namespace=$NAMESPACE -- curl -s http://localhost:8000/health 2>/dev/null)
    echo \"\$health\" | grep -q '\"model_loaded\".*true'
"

# Step 9: Check logs
echo -e "\n${CYAN}=== Step 9: Checking Application Logs ===${NC}"

test_step "Application is collecting metrics" "
    pod_name=\$(kubectl get pods -l app=infraguard --namespace=$NAMESPACE -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    logs=\$(kubectl logs \$pod_name --namespace=$NAMESPACE --tail=50 2>/dev/null)
    echo \"\$logs\" | grep -qE '(Starting collection cycle|Collection cycle completed)'
"

test_step "No critical errors in logs" "
    pod_name=\$(kubectl get pods -l app=infraguard --namespace=$NAMESPACE -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    logs=\$(kubectl logs \$pod_name --namespace=$NAMESPACE --tail=100 2>/dev/null)
    ! echo \"\$logs\" | grep -qE '(CRITICAL|FATAL)'
"

# Step 10: Resource usage
echo -e "\n${CYAN}=== Step 10: Checking Resource Usage ===${NC}"

test_step "Pod memory usage is within limits" "
    pod_name=\$(kubectl get pods -l app=infraguard --namespace=$NAMESPACE -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    metrics=\$(kubectl top pod \$pod_name --namespace=$NAMESPACE 2>/dev/null)
    
    if [ \$? -ne 0 ]; then
        echo 'Metrics server not available, skipping'
        exit 0
    fi
    
    # Extract memory usage (e.g., '512Mi')
    if echo \"\$metrics\" | grep -qE '[0-9]+Mi'; then
        memory_mi=\$(echo \"\$metrics\" | grep -oE '[0-9]+Mi' | grep -oE '[0-9]+')
        echo \"Memory usage: \${memory_mi}Mi\"
        [ \$memory_mi -lt 2048 ]  # Less than 2Gi limit
    else
        exit 0
    fi
"

# Step 11: Port forwarding test
echo -e "\n${CYAN}=== Step 11: Testing Port Forwarding ===${NC}"

test_step "Port forward and access health endpoint" "
    pod_name=\$(kubectl get pods -l app=infraguard --namespace=$NAMESPACE -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    
    # Start port-forward in background
    kubectl port-forward \$pod_name 8000:8000 --namespace=$NAMESPACE &>/dev/null &
    pf_pid=\$!
    
    sleep 5
    
    # Test health endpoint
    response=\$(curl -s http://localhost:8000/health 2>/dev/null)
    success=\$(echo \"\$response\" | grep -q '\"status\".*\"healthy\"' && echo 0 || echo 1)
    
    # Kill port-forward
    kill \$pf_pid 2>/dev/null
    
    [ \$success -eq 0 ]
"

# Step 12: Configuration validation
echo -e "\n${CYAN}=== Step 12: Validating Configuration ===${NC}"

test_step "Prometheus URL is configured" "
    pod_name=\$(kubectl get pods -l app=infraguard --namespace=$NAMESPACE -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    config=\$(kubectl exec \$pod_name --namespace=$NAMESPACE -- cat /app/config/settings.yaml 2>/dev/null)
    echo \"\$config\" | grep -q 'prometheus:'
"

test_step "ML thresholds are configured" "
    pod_name=\$(kubectl get pods -l app=infraguard --namespace=$NAMESPACE -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    config=\$(kubectl exec \$pod_name --namespace=$NAMESPACE -- cat /app/config/settings.yaml 2>/dev/null)
    echo \"\$config\" | grep -q 'thresholds:'
"

# Summary
echo -e "\n${CYAN}============================================================${NC}"
echo -e "${CYAN}Validation Summary${NC}"
echo -e "${CYAN}============================================================${NC}"
echo "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}SUCCESS: All validation tests passed!${NC}"
    echo ""
    echo -e "${GREEN}InfraGuard is successfully deployed to Kubernetes!${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. View logs: kubectl logs -f deployment/infraguard --namespace=$NAMESPACE"
    echo "  2. Check health: kubectl port-forward deployment/infraguard 8000:8000 --namespace=$NAMESPACE"
    echo "  3. Access health endpoint: curl http://localhost:8000/health"
    echo ""
    exit 0
else
    echo -e "${RED}FAILURE: $FAILED_TESTS test(s) failed${NC}"
    echo ""
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo "  1. Check pod status: kubectl get pods -l app=infraguard --namespace=$NAMESPACE"
    echo "  2. View logs: kubectl logs deployment/infraguard --namespace=$NAMESPACE"
    echo "  3. Describe pod: kubectl describe pod -l app=infraguard --namespace=$NAMESPACE"
    echo ""
    exit 1
fi
