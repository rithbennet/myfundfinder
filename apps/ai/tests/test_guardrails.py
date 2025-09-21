#!/usr/bin/env python3
"""
Test chatbot guardrails and funding responses.
"""

import requests
import json

def test_queries():
    """Test various queries to check guardrails."""
    
    test_cases = [
        # Valid funding queries
        ("What grants are available for tech startups?", "✅ SHOULD WORK"),
        ("I need funding for digital transformation", "✅ SHOULD WORK"), 
        ("How do I apply for SME loans?", "✅ SHOULD WORK"),
        ("What documents do I need for grant applications?", "✅ SHOULD WORK"),
        
        # Invalid queries (should be blocked)
        ("What's the weather today?", "❌ SHOULD BLOCK"),
        ("Tell me a joke", "❌ SHOULD BLOCK"),
        ("What's your favorite movie?", "❌ SHOULD BLOCK"),
        ("How do I cook rice?", "❌ SHOULD BLOCK"),
        ("What are the latest sports scores?", "❌ SHOULD BLOCK"),
    ]
    
    print("🛡️ Testing Chatbot Guardrails\n")
    
    for query, expected in test_cases:
        print(f"Query: {query}")
        print(f"Expected: {expected}")
        
        payload = {
            "company_id": 1,
            "message": query
        }
        
        try:
            response = requests.post(
                "http://localhost:8000/chat/",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get('response', '')
                
                # Check if it's a guardrail response
                if "specialized assistant for Malaysian SME funding" in ai_response:
                    print("Result: 🛡️ BLOCKED (Guardrail activated)")
                else:
                    print(f"Result: 💬 ALLOWED")
                    print(f"Response: {ai_response[:100]}...")
            else:
                print(f"Result: ❌ ERROR {response.status_code}")
                
        except Exception as e:
            print(f"Result: ❌ ERROR - {e}")
        
        print("-" * 80)

if __name__ == "__main__":
    test_queries()
