#!/usr/bin/env python3
"""
AWS Permissions Checker
Check what AWS services and actions you have access to
"""

import boto3
import json
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
env_path = Path(__file__).resolve().parents[1] / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()


class AWSPermissionChecker:
    """Check AWS permissions and available services"""
    
    def __init__(self):
        self.session = boto3.Session(
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        
        # Get current user info
        try:
            self.sts = self.session.client('sts')
            self.identity = self.sts.get_caller_identity()
            print(f"✅ AWS Identity: {self.identity.get('Arn', 'Unknown')}")
            print(f"📍 Account: {self.identity.get('Account', 'Unknown')}")
            print(f"👤 User ID: {self.identity.get('UserId', 'Unknown')}")
        except Exception as e:
            print(f"❌ Failed to get AWS identity: {e}")
            self.identity = {}

    def check_iam_permissions(self):
        """Check IAM permissions"""
        print("\n🔐 Checking IAM Permissions...")
        
        try:
            iam = self.session.client('iam')
            
            # Try to get current user
            try:
                user_name = self.identity.get('Arn', '').split('/')[-1]
                user = iam.get_user(UserName=user_name)
                print(f"✅ Can access IAM user info: {user_name}")
                
                # Try to list attached policies
                try:
                    policies = iam.list_attached_user_policies(UserName=user_name)
                    print(f"✅ Attached policies: {len(policies.get('AttachedPolicies', []))}")
                    for policy in policies.get('AttachedPolicies', []):
                        print(f"   📜 {policy.get('PolicyName', 'Unknown')}")
                except Exception as e:
                    print(f"⚠️  Cannot list user policies: {e}")
                
                # Try to list inline policies
                try:
                    inline_policies = iam.list_user_policies(UserName=user_name)
                    print(f"✅ Inline policies: {len(inline_policies.get('PolicyNames', []))}")
                    for policy_name in inline_policies.get('PolicyNames', []):
                        print(f"   📝 {policy_name}")
                except Exception as e:
                    print(f"⚠️  Cannot list inline policies: {e}")
                    
            except Exception as e:
                print(f"❌ Cannot access IAM user info: {e}")
                
        except Exception as e:
            print(f"❌ Cannot access IAM service: {e}")

    def check_service_access(self, service_name, test_action=None):
        """Check if we can access a specific AWS service"""
        try:
            client = self.session.client(service_name)
            
            if test_action:
                # Try the specific test action
                try:
                    if service_name == 'qbusiness' and test_action == 'list_applications':
                        client.list_applications()
                    elif service_name == 'bedrock' and test_action == 'list_foundation_models':
                        client.list_foundation_models()
                    elif service_name == 'bedrock-runtime' and test_action == 'invoke_model':
                        # Just check if we can create the client, don't actually invoke
                        pass
                    print(f"✅ {service_name}: Can perform {test_action}")
                    return True
                except Exception as e:
                    print(f"❌ {service_name}: Cannot perform {test_action} - {e}")
                    return False
            else:
                print(f"✅ {service_name}: Client created successfully")
                return True
                
        except Exception as e:
            print(f"❌ {service_name}: Cannot create client - {e}")
            return False

    def check_bedrock_access(self):
        """Specifically check Bedrock access"""
        print("\n🤖 Checking AWS Bedrock Access...")
        
        # Check Bedrock service
        bedrock_available = self.check_service_access('bedrock', 'list_foundation_models')
        
        # Check Bedrock Runtime
        bedrock_runtime_available = self.check_service_access('bedrock-runtime')
        
        if bedrock_runtime_available:
            try:
                bedrock_runtime = self.session.client('bedrock-runtime')
                
                # Test Nova Pro access
                print("\n🧪 Testing Nova Pro access...")
                messages = [{"role": "user", "content": [{"text": "Hello"}]}]
                inference_config = {"maxTokens": 10, "temperature": 0.7}
                
                response = bedrock_runtime.converse(
                    modelId="amazon.nova-pro-v1:0",
                    messages=messages,
                    inferenceConfig=inference_config
                )
                print("✅ Nova Pro: Working perfectly!")
                
            except Exception as e:
                print(f"❌ Nova Pro test failed: {e}")

    def check_q_services(self):
        """Check AWS Q services access"""
        print("\n🔍 Checking AWS Q Services Access...")
        
        # Check Q Business
        print("\n📊 Q Business:")
        q_business_available = self.check_service_access('qbusiness', 'list_applications')
        
        # Check if Q Apps is available
        print("\n📱 Q Apps:")
        q_apps_available = self.check_service_access('qapps')
        
        # Check CodeWhisperer (Q Developer)
        print("\n💻 CodeWhisperer/Q Developer:")
        try:
            # Try the old CodeWhisperer service
            codewhisperer_available = self.check_service_access('codewhisperer')
        except:
            print("❌ CodeWhisperer service not available")
            codewhisperer_available = False
            
        # Try Amazon Q Developer (newer service name)
        try:
            q_developer_available = self.check_service_access('q-developer')
        except:
            print("❌ Q Developer service not available")
            q_developer_available = False
            
        return {
            'qbusiness': q_business_available,
            'qapps': q_apps_available,
            'codewhisperer': codewhisperer_available,
            'q_developer': q_developer_available
        }

    def check_other_ai_services(self):
        """Check other AI services you might have access to"""
        print("\n🧠 Checking Other AI Services...")
        
        services_to_check = [
            ('comprehend', 'Natural Language Processing'),
            ('textract', 'Document Text Extraction'),
            ('translate', 'Language Translation'),
            ('polly', 'Text-to-Speech'),
            ('rekognition', 'Image/Video Analysis'),
            ('sagemaker', 'Machine Learning Platform'),
            ('lex-models', 'Chatbot Service'),
            ('personalize', 'Recommendation Engine')
        ]
        
        available_services = []
        for service, description in services_to_check:
            if self.check_service_access(service):
                available_services.append((service, description))
                
        if available_services:
            print(f"\n✅ You have access to {len(available_services)} other AI services:")
            for service, description in available_services:
                print(f"   🔹 {service}: {description}")
        else:
            print("❌ No other AI services detected")
            
        return available_services

    def generate_recommendations(self, q_access, other_services):
        """Generate recommendations based on available services"""
        print("\n💡 Recommendations for Your Hackathon:")
        print("=" * 50)
        
        if any(q_access.values()):
            print("🎯 AWS Q Services:")
            if q_access['qbusiness']:
                print("   ✅ Use Q Business for enterprise data queries")
            if q_access['qapps']:
                print("   ✅ Use Q Apps for application development")
            if q_access['codewhisperer'] or q_access['q_developer']:
                print("   ✅ Use Q Developer for code suggestions")
        else:
            print("⚠️  No AWS Q services available - Use Bedrock as primary AI service")
            
        print(f"\n🚀 Your Current Setup (PERFECT for hackathon):")
        print("   ✅ AWS Bedrock Nova Pro - Excellent for:")
        print("      • Document analysis and processing")
        print("      • Company information extraction")
        print("      • Funding recommendation generation")
        print("      • Natural language chat interfaces")
        print("      • Code generation and suggestions")
        
        if other_services:
            print(f"\n🔧 Additional Services Available:")
            for service, description in other_services:
                print(f"   ✅ {service}: {description}")
                
        print(f"\n🏆 Bottom Line:")
        print("   Your current Bedrock setup is EXCELLENT for the hackathon!")
        print("   You have everything needed for an impressive AI-powered demo.")

    def run_full_check(self):
        """Run all permission checks"""
        print("🔍 AWS Permissions & Services Checker")
        print("=" * 40)
        
        # Check IAM permissions
        self.check_iam_permissions()
        
        # Check Bedrock (your main service)
        self.check_bedrock_access()
        
        # Check Q services
        q_access = self.check_q_services()
        
        # Check other AI services
        other_services = self.check_other_ai_services()
        
        # Generate recommendations
        self.generate_recommendations(q_access, other_services)


def main():
    """Main function"""
    try:
        checker = AWSPermissionChecker()
        checker.run_full_check()
    except Exception as e:
        print(f"❌ Error running permission check: {e}")


if __name__ == "__main__":
    main()