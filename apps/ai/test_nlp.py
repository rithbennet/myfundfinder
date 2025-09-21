"""
Quick test script for Nova Pro NLP functionality
Run this after adding your AWS credentials to .env
"""

import os
import sys
sys.path.append('app')

from dotenv import load_dotenv
load_dotenv()

def test_credentials():
    """Test if AWS credentials are set"""
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_REGION')
    
    print(f"AWS Access Key: {'✓ Set' if access_key and access_key != 'your-access-key-here' else '✗ Missing'}")
    print(f"AWS Secret Key: {'✓ Set' if secret_key and secret_key != 'your-secret-key-here' else '✗ Missing'}")
    print(f"AWS Region: {region}")
    
    return access_key and secret_key and access_key != 'your-access-key-here'

def test_nova_pro():
    """Test Nova Pro connection"""
    try:
        from bedrock_service import BedrockService
        
        service = BedrockService()
        
        # Test simple text extraction
        test_text = "TechStartup Inc is a small technology company based in California focusing on AI solutions for healthcare. We have 15 employees and need funding for product development."
        
        print("\n🧪 Testing Nova Pro NLP...")
        print(f"Input: {test_text}")
        
        # Test company info extraction
        result = service.extract_company_info_from_text(test_text)
        print(f"\n✅ Company Info Extracted:")
        for key, value in result.items():
            print(f"  {key}: {value}")
        
        return True
    except Exception as e:
        print(f"\n❌ Error testing Nova Pro: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing MyFundFinder NLP Setup\n")
    
    # Test 1: Check credentials
    if not test_credentials():
        print("\n❌ Please add your AWS credentials to .env file first!")
        exit(1)
    
    # Test 2: Test Nova Pro
    if test_nova_pro():
        print("\n🎉 Success! Your NLP is ready for the hackathon!")
    else:
        print("\n❌ NLP test failed. Check your AWS permissions for Bedrock.")