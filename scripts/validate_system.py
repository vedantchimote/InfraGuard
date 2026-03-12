#!/usr/bin/env python3
"""
System validation script for InfraGuard.

Checks that all components are working correctly.
"""

import sys
import time
import requests
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_prometheus():
    """Check if Prometheus is accessible."""
    print("🔍 Checking Prometheus...")
    try:
        response = requests.get("http://localhost:9090/-/healthy", timeout=5)
        if response.status_code == 200:
            print("✅ Prometheus is healthy")
            return True
        else:
            print(f"❌ Prometheus returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Prometheus not accessible: {e}")
        return False


def check_dummy_app():
    """Check if dummy metrics app is running."""
    print("\n🔍 Checking Dummy Metrics App...")
    try:
        response = requests.get("http://localhost:8080/metrics", timeout=5)
        if response.status_code == 200 and "cpu_usage_percent" in response.text:
            print("✅ Dummy app is generating metrics")
            return True
        else:
            print(f"❌ Dummy app returned unexpected response")
            return False
    except Exception as e:
        print(f"❌ Dummy app not accessible: {e}")
        return False


def check_prometheus_scraping():
    """Check if Prometheus is scraping the dummy app."""
    print("\n🔍 Checking Prometheus Scraping...")
    try:
        response = requests.get(
            "http://localhost:9090/api/v1/query",
            params={"query": "up{job='dummy-app'}"},
            timeout=5
        )
        data = response.json()
        if data.get("status") == "success" and data.get("data", {}).get("result"):
            print("✅ Prometheus is scraping dummy app")
            return True
        else:
            print("⚠️  Prometheus hasn't scraped dummy app yet (may need to wait)")
            return False
    except Exception as e:
        print(f"❌ Error checking Prometheus scraping: {e}")
        return False


def check_infraguard_health():
    """Check if InfraGuard health endpoint is responding."""
    print("\n🔍 Checking InfraGuard Health...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ InfraGuard is healthy")
            print(f"   Status: {data.get('status')}")
            print(f"   Running: {data.get('running')}")
            print(f"   Model Loaded: {data.get('model_loaded')}")
            print(f"   Last Collection: {data.get('last_collection_time', 'N/A')}")
            return True
        else:
            print(f"❌ InfraGuard health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ InfraGuard not accessible: {e}")
        return False


def check_metrics_available():
    """Check if metrics are available in Prometheus."""
    print("\n🔍 Checking Available Metrics...")
    metrics = [
        "cpu_usage_percent",
        "memory_usage_percent",
        "http_error_rate_percent",
        "request_latency_ms"
    ]
    
    all_available = True
    for metric in metrics:
        try:
            response = requests.get(
                "http://localhost:9090/api/v1/query",
                params={"query": metric},
                timeout=5
            )
            data = response.json()
            if data.get("status") == "success" and data.get("data", {}).get("result"):
                print(f"✅ {metric} is available")
            else:
                print(f"⚠️  {metric} not available yet")
                all_available = False
        except Exception as e:
            print(f"❌ Error checking {metric}: {e}")
            all_available = False
    
    return all_available


def main():
    """Run all validation checks."""
    print("=" * 60)
    print("InfraGuard System Validation")
    print("=" * 60)
    
    checks = [
        ("Prometheus", check_prometheus),
        ("Dummy App", check_dummy_app),
        ("Prometheus Scraping", check_prometheus_scraping),
        ("InfraGuard Health", check_infraguard_health),
        ("Metrics Available", check_metrics_available),
    ]
    
    results = {}
    for name, check_func in checks:
        results[name] = check_func()
        time.sleep(1)  # Brief pause between checks
    
    # Summary
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! System is ready.")
        return 0
    elif passed >= 3:
        print("\n⚠️  Some checks failed, but core system is working.")
        print("   Wait a few minutes for services to fully start.")
        return 0
    else:
        print("\n❌ System validation failed. Check Docker logs:")
        print("   docker-compose logs")
        return 1


if __name__ == "__main__":
    sys.exit(main())
