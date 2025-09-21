#!/usr/bin/env python3
"""
Test script for MyFundFinder AI FastAPI endpoints
"""

import requests
import sys
import json

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Health endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health endpoint failed: {e}")
        return False

def test_document_formats_endpoint():
    """Test the supported formats endpoint"""
    try:
        response = requests.get("http://localhost:8000/documents/supported-formats")
        print(f"Supported formats endpoint: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Supported formats endpoint failed: {e}")
        return False

def test_text_analysis():
    """Test text analysis endpoint"""
    try:
        test_data = {
            "text": "TechStartup Inc is a small technology company based in California focusing on AI solutions for healthcare. We have 15 employees and need funding for product development.",
            "analysis_type": "company_info"
        }
        response = requests.post("http://localhost:8000/documents/analyze-text", json=test_data)
        print(f"Text analysis endpoint: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Text analysis endpoint failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing MyFundFinder AI FastAPI endpoints...")
    print("=" * 50)
    
    # Test basic health
    print("1. Testing health endpoint...")
    health_ok = test_health_endpoint()
    print()
    
    # Test document formats
    print("2. Testing supported formats endpoint...")
    formats_ok = test_document_formats_endpoint()
    print()
    
    # Test text analysis
    print("3. Testing text analysis endpoint...")
    analysis_ok = test_text_analysis()
    print()
    
    # Summary
    print("=" * 50)
    print("Test Results:")
    print(f"Health endpoint: {'✅' if health_ok else '❌'}")
    print(f"Formats endpoint: {'✅' if formats_ok else '❌'}")
    print(f"Text analysis: {'✅' if analysis_ok else '❌'}")
    
    if all([health_ok, formats_ok, analysis_ok]):
        print("\n🎉 All tests passed! FastAPI endpoints are working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check the FastAPI server.")
        sys.exit(1)