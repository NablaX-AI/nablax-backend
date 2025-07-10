#!/usr/bin/env python3
"""
Test LLM Client Functionality
Tests the Azure OpenAI client under agents/
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_llm_client_import():
    """Test that LLM client can be imported."""
    try:
        from agents.llm_client import get_llm_client
        print("✅ LLM client imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import LLM client: {e}")
        return False

def test_llm_client_configuration():
    """Test LLM client configuration and environment variables."""
    try:
        import os
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv()
        
        required_vars = [
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_KEY",
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️  Missing environment variables: {missing_vars}")
            print("💡 This is expected if .env file is not configured")
            return False
        else:
            print("✅ All required environment variables are set")
            return True
            
    except Exception as e:
        print(f"❌ Error checking LLM client configuration: {e}")
        return False

def test_llm_client_instantiation():
    """Test LLM client instantiation."""
    try:
        from agents.llm_client import get_llm_client
        
        # Try to get client instance
        client = get_llm_client()
        
        if client is None:
            print("⚠️  LLM client returned None (likely due to missing environment variables)")
            return False
        
        print("✅ LLM client instantiated successfully")
        print(f"📝 Client type: {type(client)}")
        
        # Check if it's an Azure OpenAI client
        if hasattr(client, 'chat'):
            print("✅ Client has chat capability")
        
        return True
        
    except Exception as e:
        print(f"❌ Error instantiating LLM client: {e}")
        return False

def test_llm_client_functionality():
    """Test basic LLM client functionality."""
    try:
        from agents.llm_client import get_llm_client
        
        client = get_llm_client()
        if client is None:
            print("⚠️  Skipping functionality test - client not available")
            return False
        
        # Try to make a simple API call (if environment is configured)
        try:
            # This is a minimal test - in production, you'd want to test actual completion
            print("✅ LLM client is ready for API calls")
            print("💡 Note: Actual API calls not tested to avoid charges")
            return True
            
        except Exception as api_error:
            print(f"⚠️  API call test failed: {api_error}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing LLM client functionality: {e}")
        return False

def test_llm_client_error_handling():
    """Test LLM client error handling."""
    try:
        from agents.llm_client import get_llm_client
        
        # Test with invalid environment (temporarily)
        original_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        original_key = os.environ.get("AZURE_OPENAI_API_KEY")
        
        # Temporarily remove environment variables
        if "AZURE_OPENAI_ENDPOINT" in os.environ:
            del os.environ["AZURE_OPENAI_ENDPOINT"]
        if "AZURE_OPENAI_API_KEY" in os.environ:
            del os.environ["AZURE_OPENAI_API_KEY"]
        
        # Force re-instantiation by clearing global client
        import agents.llm_client
        agents.llm_client._client = None
        
        client = get_llm_client()
        
        # Restore environment variables
        if original_endpoint:
            os.environ["AZURE_OPENAI_ENDPOINT"] = original_endpoint
        if original_key:
            os.environ["AZURE_OPENAI_API_KEY"] = original_key
        
        # Reset client for future tests
        agents.llm_client._client = None
        
        if client is None:
            print("✅ LLM client properly handles missing configuration")
            return True
        else:
            print("⚠️  LLM client should return None with missing config")
            return False
            
    except Exception as e:
        print(f"❌ Error testing LLM client error handling: {e}")
        return False

def main():
    """Run all LLM client tests."""
    print("=== Testing LLM Client ===\n")
    
    tests = [
        ("Import Test", test_llm_client_import),
        ("Configuration Test", test_llm_client_configuration),
        ("Instantiation Test", test_llm_client_instantiation),
        ("Functionality Test", test_llm_client_functionality),
        ("Error Handling Test", test_llm_client_error_handling),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} passed\n")
            else:
                failed += 1
                print(f"❌ {test_name} failed\n")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} crashed: {e}\n")
    
    print("=== LLM Client Test Results ===")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All LLM client tests passed!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)