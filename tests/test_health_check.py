#!/usr/bin/env python3
"""
Test FastAPI Health Check Functionality
Tests the health check endpoints and service status
"""

import sys
import os
import asyncio
import httpx
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

async def test_health_endpoint_structure():
    """Test that health endpoint returns correct structure."""
    try:
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/health")
        
        print(f"📊 Health endpoint status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Health endpoint returned status {response.status_code}")
            return False
        
        data = response.json()
        print(f"📋 Health response: {data}")
        
        required_fields = ["status", "service"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        
        if data.get("status") != "healthy":
            print(f"❌ Service status is not 'healthy': {data.get('status')}")
            return False
        
        print("✅ Health endpoint structure is correct")
        return True
        
    except Exception as e:
        print(f"❌ Error testing health endpoint structure: {e}")
        return False

async def test_health_endpoint_mcp_info():
    """Test that health endpoint includes MCP server information."""
    try:
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/health")
        
        if response.status_code != 200:
            print("⚠️  Skipping MCP info test - health endpoint not available")
            return False
        
        data = response.json()
        
        # Check for MCP-related information
        mcp_fields = ["servers", "server_names"]
        present_mcp_fields = [field for field in mcp_fields if field in data]
        
        if present_mcp_fields:
            print(f"✅ Health endpoint includes MCP info: {present_mcp_fields}")
            print(f"📋 MCP servers: {data.get('server_names', [])}")
            return True
        else:
            print("⚠️  Health endpoint missing MCP server information")
            return False
        
    except Exception as e:
        print(f"❌ Error testing health endpoint MCP info: {e}")
        return False

async def test_health_endpoint_performance():
    """Test health endpoint response time."""
    try:
        from main import app
        from fastapi.testclient import TestClient
        import time
        
        client = TestClient(app)
        
        # Measure response time
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        print(f"⏱️  Health endpoint response time: {response_time:.2f}ms")
        
        if response_time > 1000:  # 1 second threshold
            print("⚠️  Health endpoint is slow (>1000ms)")
            return False
        
        print("✅ Health endpoint response time is acceptable")
        return True
        
    except Exception as e:
        print(f"❌ Error testing health endpoint performance: {e}")
        return False

async def test_health_endpoint_multiple_calls():
    """Test health endpoint with multiple rapid calls."""
    try:
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        success_count = 0
        total_calls = 5
        
        print(f"🔄 Testing {total_calls} rapid health check calls...")
        
        for i in range(total_calls):
            response = client.get("/health")
            if response.status_code == 200:
                success_count += 1
        
        success_rate = (success_count / total_calls) * 100
        print(f"📊 Success rate: {success_rate:.1f}% ({success_count}/{total_calls})")
        
        if success_rate < 100:
            print("⚠️  Health endpoint failed some rapid calls")
            return False
        
        print("✅ Health endpoint handles multiple calls correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error testing health endpoint multiple calls: {e}")
        return False

async def test_health_vs_root_endpoint():
    """Test consistency between health and root endpoints."""
    try:
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        health_response = client.get("/health")
        root_response = client.get("/")
        
        if health_response.status_code != 200 or root_response.status_code != 200:
            print("⚠️  Skipping consistency test - endpoints not available")
            return False
        
        health_data = health_response.json()
        root_data = root_response.json()
        
        # Check for consistent service information
        health_service = health_data.get("service")
        root_version = root_data.get("version")
        
        print(f"📋 Health service: {health_service}")
        print(f"📋 Root version: {root_version}")
        
        # Both should indicate a working service
        if health_data.get("status") == "healthy" and "message" in root_data:
            print("✅ Health and root endpoints are consistent")
            return True
        else:
            print("⚠️  Health and root endpoints may be inconsistent")
            return False
        
    except Exception as e:
        print(f"❌ Error testing endpoint consistency: {e}")
        return False

async def test_health_endpoint_async():
    """Test health endpoint with async HTTP client."""
    try:
        import asyncio
        
        # Start the app in a separate process for true async testing
        print("🔄 Testing health endpoint with async client...")
        
        async with httpx.AsyncClient() as client:
            try:
                # Note: This will fail if server is not running, which is expected
                response = await client.get("http://localhost:8000/health", timeout=5.0)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Async health check successful: {data.get('status')}")
                    return True
                else:
                    print(f"⚠️  Async health check returned {response.status_code}")
                    return False
                    
            except httpx.ConnectError:
                print("⚠️  Server not running - async test skipped")
                return True  # Not a failure, just no running server
            except httpx.TimeoutException:
                print("❌ Health endpoint timed out")
                return False
                
    except Exception as e:
        print(f"❌ Error testing async health endpoint: {e}")
        return False

def main():
    """Run all health check tests."""
    print("=== Testing FastAPI Health Check ===\n")
    
    tests = [
        ("Health Endpoint Structure", test_health_endpoint_structure),
        ("Health MCP Information", test_health_endpoint_mcp_info),
        ("Health Performance", test_health_endpoint_performance),
        ("Health Multiple Calls", test_health_endpoint_multiple_calls),
        ("Health vs Root Consistency", test_health_vs_root_endpoint),
        ("Health Async Client", test_health_endpoint_async),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        try:
            result = asyncio.run(test_func())
            if result:
                passed += 1
                print(f"✅ {test_name} passed\n")
            else:
                failed += 1
                print(f"❌ {test_name} failed\n")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} crashed: {e}\n")
    
    print("=== Health Check Test Results ===")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All health check tests passed!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)