"""
Dummy metrics application for testing InfraGuard.

This application generates realistic metrics with periodic spikes and anomalies
for testing the anomaly detection system.
"""

import os
import time
import random
import math
from datetime import datetime
from flask import Flask, Response


app = Flask(__name__)

# Configuration
METRICS_PORT = int(os.getenv('METRICS_PORT', 8080))
ANOMALY_PROBABILITY = float(os.getenv('ANOMALY_PROBABILITY', 0.05))

# Metric state
start_time = time.time()
request_count = 0


def generate_cpu_usage():
    """
    Generate realistic CPU usage metric with daily patterns and anomalies.
    
    Returns:
        Float between 0 and 100 representing CPU percentage
    """
    current_time = time.time()
    elapsed = current_time - start_time
    
    # Base CPU usage with daily pattern (higher during business hours)
    hour = datetime.now().hour
    base_cpu = 30 + 20 * math.sin((hour - 6) * math.pi / 12)
    
    # Add some noise
    noise = random.gauss(0, 5)
    
    # Periodic spike every 5 minutes
    if int(elapsed) % 300 < 30:
        spike = random.uniform(20, 40)
    else:
        spike = 0
    
    # Random anomaly
    if random.random() < ANOMALY_PROBABILITY:
        anomaly = random.uniform(40, 60)
    else:
        anomaly = 0
    
    cpu = max(0, min(100, base_cpu + noise + spike + anomaly))
    return cpu


def generate_memory_usage():
    """
    Generate realistic memory usage metric with gradual increase (memory leak simulation).
    
    Returns:
        Float between 0 and 100 representing memory percentage
    """
    current_time = time.time()
    elapsed = current_time - start_time
    
    # Base memory usage
    base_memory = 40
    
    # Gradual increase (simulating memory leak)
    leak = (elapsed / 3600) * 5  # 5% increase per hour
    
    # Add some noise
    noise = random.gauss(0, 3)
    
    # Random anomaly (sudden spike)
    if random.random() < ANOMALY_PROBABILITY:
        anomaly = random.uniform(30, 50)
    else:
        anomaly = 0
    
    memory = max(0, min(100, base_memory + leak + noise + anomaly))
    return memory


def generate_http_error_rate():
    """
    Generate HTTP error rate metric with occasional spikes.
    
    Returns:
        Float between 0 and 100 representing error percentage
    """
    # Normal error rate is low
    base_error_rate = 1.0
    
    # Add some noise
    noise = random.gauss(0, 0.5)
    
    # Random error spike
    if random.random() < ANOMALY_PROBABILITY * 2:  # More frequent errors
        spike = random.uniform(10, 30)
    else:
        spike = 0
    
    error_rate = max(0, min(100, base_error_rate + noise + spike))
    return error_rate


def generate_request_latency():
    """
    Generate request latency metric in milliseconds.
    
    Returns:
        Float representing latency in milliseconds
    """
    # Normal latency
    base_latency = 50
    
    # Add some noise
    noise = random.gauss(0, 10)
    
    # Random latency spike
    if random.random() < ANOMALY_PROBABILITY:
        spike = random.uniform(200, 500)
    else:
        spike = 0
    
    latency = max(0, base_latency + noise + spike)
    return latency


@app.route('/metrics')
def metrics():
    """
    Prometheus metrics endpoint.
    
    Returns metrics in Prometheus text format.
    """
    global request_count
    request_count += 1
    
    # Generate current metric values
    cpu = generate_cpu_usage()
    memory = generate_memory_usage()
    error_rate = generate_http_error_rate()
    latency = generate_request_latency()
    
    # Format metrics in Prometheus format
    metrics_output = f"""# HELP cpu_usage_percent Current CPU usage percentage
# TYPE cpu_usage_percent gauge
cpu_usage_percent{{instance="dummy-app",job="dummy"}} {cpu:.2f}

# HELP memory_usage_percent Current memory usage percentage
# TYPE memory_usage_percent gauge
memory_usage_percent{{instance="dummy-app",job="dummy"}} {memory:.2f}

# HELP http_error_rate_percent HTTP error rate percentage
# TYPE http_error_rate_percent gauge
http_error_rate_percent{{instance="dummy-app",job="dummy"}} {error_rate:.2f}

# HELP request_latency_ms Request latency in milliseconds
# TYPE request_latency_ms gauge
request_latency_ms{{instance="dummy-app",job="dummy"}} {latency:.2f}

# HELP http_requests_total Total number of HTTP requests
# TYPE http_requests_total counter
http_requests_total{{instance="dummy-app",job="dummy"}} {request_count}

# HELP app_uptime_seconds Application uptime in seconds
# TYPE app_uptime_seconds gauge
app_uptime_seconds{{instance="dummy-app",job="dummy"}} {time.time() - start_time:.2f}
"""
    
    return Response(metrics_output, mimetype='text/plain')


@app.route('/health')
def health():
    """Health check endpoint."""
    return {'status': 'healthy', 'uptime': time.time() - start_time}


@app.route('/')
def index():
    """Root endpoint."""
    return {
        'service': 'InfraGuard Dummy Metrics App',
        'endpoints': {
            '/metrics': 'Prometheus metrics',
            '/health': 'Health check'
        }
    }


if __name__ == '__main__':
    print(f"Starting dummy metrics app on port {METRICS_PORT}")
    print(f"Anomaly probability: {ANOMALY_PROBABILITY}")
    app.run(host='0.0.0.0', port=METRICS_PORT)
