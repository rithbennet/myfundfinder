#!/usr/bin/env python3
"""
Quick test script for the SME RAG Chatbot
"""

import requests
import json
import time

def test_chatbot_api():
    base_url = "http://localhost:8080"
    
    print("🧪 Testing SME RAG Chatbot API")
    print("=" * 40)
    
    # Test 1: Status endpoint
    print("\n1. Testing status endpoint...")
    try:
        response = requests.get(f"{base_url}/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status')}")
            print(f"📁 Documents: {data.get('documents_count')}")
            print(f"🔄 Processed: {data.get('processed_count')}")
        else:
            print(f"❌ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Status error: {e}")
    
    # Test 2: Documents endpoint
    print("\n2. Testing documents endpoint...")
    try:
        response = requests.get(f"{base_url}/documents", timeout=5)
        if response.status_code == 200:
            data = response.json()
            documents = data.get('documents', [])
            print(f"✅ Found {len(documents)} documents:")
            for doc in documents[:3]:  # Show first 3
                print(f"   📄 {doc['name']} ({doc['size']} bytes)")
        else:
            print(f"❌ Documents check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Documents error: {e}")
    
    # Test 3: Chat endpoint
    print("\n3. Testing chat endpoint...")
    test_queries = [
        "What is this document about?",
        "Tell me about SME",
        "How does RAG work?"
    ]
    
    for query in test_queries:
        try:
            response = requests.post(
                f"{base_url}/chat",
                json={"message": query},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Query: '{query}'")
                print(f"   📖 Found {data.get('search_results_count', 0)} results")
                print(f"   🤖 Response preview: {data.get('response', '')[:100]}...")
            else:
                print(f"❌ Chat failed for '{query}': {response.status_code}")
        except Exception as e:
            print(f"❌ Chat error for '{query}': {e}")
        
        time.sleep(1)  # Brief pause between requests
    
    print("\n✅ API testing complete!")
    print("\n🌐 Open http://localhost:8080 in your browser to use the chatbot interface")

if __name__ == "__main__":
    test_chatbot_api()