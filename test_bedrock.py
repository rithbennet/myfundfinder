#!/usr/bin/env python3
"""
Simple Bedrock Test Script - Test AWS Bedrock without exposing credentials in codebase
Run this locally to test Bedrock functionality before integrating.
"""

import boto3
import json
import os
from typing import Dict, Any

class BedrockTester:
    def __init__(self):
        # Use AWS CLI credentials or environment variables
        # Never hardcode credentials!
        self.bedrock_runtime = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        
    def test_claude_chat(self, message: str) -> str:
        """Test basic chat with Claude"""
        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                body=json.dumps(body)
            )
            
            result = json.loads(response['body'].read())
            return result['content'][0]['text']
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def test_embeddings(self, text: str) -> Dict[str, Any]:
        """Test text embeddings generation"""
        try:
            body = json.dumps({
                "inputText": text
            })
            
            response = self.bedrock_runtime.invoke_model(
                modelId="amazon.titan-embed-text-v1",
                body=body
            )
            
            result = json.loads(response['body'].read())
            return {
                "success": True,
                "embedding_length": len(result['embedding']),
                "first_few_values": result['embedding'][:5]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

def main():
    print("🧪 AWS Bedrock Tester")
    print("=" * 40)
    
    # Check if AWS credentials are configured
    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        if not credentials:
            print("❌ No AWS credentials found!")
            print("Run: aws configure")
            return
        print("✅ AWS credentials found")
    except Exception as e:
        print(f"❌ AWS setup error: {e}")
        return
    
    tester = BedrockTester()
    
    # Test 1: Basic Chat
    print("\n📝 Testing Claude Chat...")
    response = tester.test_claude_chat("Hello! Can you help me find funding for my small tech startup?")
    print(f"Claude Response: {response[:200]}...")
    
    # Test 2: Embeddings
    print("\n🔢 Testing Embeddings...")
    embedding_result = tester.test_embeddings("Small business technology grant funding")
    if embedding_result["success"]:
        print(f"✅ Embeddings generated: {embedding_result['embedding_length']} dimensions")
        print(f"Sample values: {embedding_result['first_few_values']}")
    else:
        print(f"❌ Embeddings failed: {embedding_result['error']}")
    
    # Test 3: Fund Matching Simulation
    print("\n💰 Testing Fund Matching...")
    fund_query = """
    I have a small technology startup focused on AI and machine learning. 
    We're looking for grants or funding opportunities. 
    Can you suggest what types of funding we should look for?
    """
    
    matching_response = tester.test_claude_chat(fund_query)
    print(f"Fund Matching Response: {matching_response}")
    
    print("\n✅ Testing complete!")
    print("\nNext steps:")
    print("1. If tests pass, your AWS Bedrock is working")
    print("2. You can now integrate with your FastAPI backend")
    print("3. Make sure to never commit AWS credentials to Git")

if __name__ == "__main__":
    main()