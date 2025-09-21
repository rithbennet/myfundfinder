#!/usr/bin/env python3
"""
SME RAG System Setup Script
This script sets up the basic infrastructure for a RAG system using AWS services.
"""

import boto3
import json
import time
from datetime import datetime

class RAGSetup:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.opensearch_client = boto3.client('opensearch')
        self.iam_client = boto3.client('iam')
        
        # Configuration
        self.bucket_name = "sme-rag-documents-1758382778"  # Your existing bucket
        self.opensearch_domain = "sme-rag-search"
        self.region = "us-east-1"
        
    def check_s3_bucket(self):
        """Check if S3 bucket exists and is accessible"""
        try:
            response = self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f"✅ S3 bucket '{self.bucket_name}' is ready")
            return True
        except Exception as e:
            print(f"❌ S3 bucket error: {e}")
            return False
    
    def setup_bucket_structure(self):
        """Create folder structure in S3 bucket"""
        folders = ['documents/', 'processed/', 'embeddings/']
        
        for folder in folders:
            try:
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=folder,
                    Body=''
                )
                print(f"✅ Created folder: {folder}")
            except Exception as e:
                print(f"❌ Error creating folder {folder}: {e}")
    
    def upload_sample_document(self):
        """Upload a sample document for testing"""
        sample_content = """
        Sample SME Document for RAG Testing
        
        This is a sample document that demonstrates how the RAG system works.
        
        Key Information:
        - Small and Medium Enterprises (SMEs) are crucial for economic growth
        - RAG systems can help SMEs access relevant information quickly
        - Vector search enables semantic similarity matching
        - OpenSearch provides scalable search capabilities
        
        Business Process:
        1. Document ingestion and preprocessing
        2. Text chunking and embedding generation
        3. Vector storage in OpenSearch
        4. Query processing and retrieval
        5. Response generation with context
        """
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key='documents/sample_sme_doc.txt',
                Body=sample_content.encode('utf-8'),
                ContentType='text/plain'
            )
            print("✅ Uploaded sample document")
        except Exception as e:
            print(f"❌ Error uploading sample document: {e}")
    
    def create_iam_role_for_lambda(self):
        """Create IAM role for Lambda functions"""
        assume_role_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        try:
            response = self.iam_client.create_role(
                RoleName='SME-RAG-Lambda-Role',
                AssumeRolePolicyDocument=json.dumps(assume_role_policy),
                Description='IAM role for SME RAG Lambda functions'
            )
            print("✅ Created IAM role for Lambda")
            
            # Attach necessary policies
            policies = [
                'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
                'arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess'
            ]
            
            for policy_arn in policies:
                self.iam_client.attach_role_policy(
                    RoleName='SME-RAG-Lambda-Role',
                    PolicyArn=policy_arn
                )
            
            return response['Role']['Arn']
            
        except Exception as e:
            if 'EntityAlreadyExists' in str(e):
                print("✅ IAM role already exists")
                response = self.iam_client.get_role(RoleName='SME-RAG-Lambda-Role')
                return response['Role']['Arn']
            else:
                print(f"❌ Error creating IAM role: {e}")
                return None
    
    def display_next_steps(self):
        """Display what to do next"""
        print("\n" + "="*60)
        print("🎯 NEXT STEPS FOR YOUR RAG SYSTEM")
        print("="*60)
        print("\n1. Add these AWS managed policies to your IAM user:")
        print("   - AmazonAPIGatewayAdministrator")
        print("   - AWSLambdaFullAccess") 
        print("   - IAMFullAccess (for role creation)")
        
        print("\n2. Your current infrastructure:")
        print(f"   ✅ S3 Bucket: {self.bucket_name}")
        print("   ⏳ OpenSearch: Creating (this takes 10-15 minutes)")
        print("   ⏳ Lambda Functions: Ready to create")
        print("   ⏳ API Gateway: Ready to create")
        
        print("\n3. Core RAG Components to implement:")
        print("   📄 Document processor (Lambda)")
        print("   🧠 Embedding generator (using OpenAI/Bedrock)")
        print("   🔍 Vector search (OpenSearch)")
        print("   💬 Query handler (Lambda + API Gateway)")
        
        print("\n4. Test your setup:")
        print(f"   aws s3 ls s3://{self.bucket_name}/")
        print("   python3 rag_setup.py")
        
        print("\n5. Development workflow:")
        print("   - Upload documents to S3")
        print("   - Process and generate embeddings")
        print("   - Store vectors in OpenSearch")
        print("   - Query via API endpoints")

def main():
    print("🚀 Setting up SME RAG System...")
    print("="*50)
    
    rag = RAGSetup()
    
    # Check S3 bucket
    if rag.check_s3_bucket():
        rag.setup_bucket_structure()
        rag.upload_sample_document()
    
    # Create IAM role
    lambda_role_arn = rag.create_iam_role_for_lambda()
    
    # Display next steps
    rag.display_next_steps()

if __name__ == "__main__":
    main()