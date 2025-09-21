#!/usr/bin/env python3
"""
RAG using Amazon Bedrock Knowledge Bases for vector storage
"""

import boto3
import json
import time
from typing import List, Dict, Any

class BedrockKnowledgeBaseRAG:
    def __init__(self, bucket_name: str, aws_region: str = "us-east-1"):
        self.s3_client = boto3.client('s3', region_name=aws_region)
        self.bedrock_agent = boto3.client('bedrock-agent-runtime', region_name=aws_region)
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=aws_region)
        self.bucket_name = bucket_name
        
        # Knowledge Base ID (we'll create this)
        self.knowledge_base_id = "YOUR_KB_ID"  # Will be set after creation
    
    def upload_document_to_s3(self, content: str, filename: str) -> str:
        """Upload document to S3 for Knowledge Base ingestion"""
        key = f"knowledge-base-docs/{filename}"
        
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=content.encode('utf-8'),
            ContentType='text/plain'
        )
        
        return key
    
    def search_knowledge_base(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search using Bedrock Knowledge Base"""
        try:
            response = self.bedrock_agent.retrieve(
                knowledgeBaseId=self.knowledge_base_id,
                retrievalQuery={
                    'text': query
                },
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': max_results
                    }
                }
            )
            
            results = []
            for item in response.get('retrievalResults', []):
                results.append({
                    'text': item['content']['text'],
                    'score': item['score'],
                    'source': item['location']['s3Location']['uri'],
                    'metadata': item.get('metadata', {})
                })
            
            return results
            
        except Exception as e:
            print(f"Knowledge Base search error: {e}")
            return []
    
    def generate_rag_response(self, query: str, max_results: int = 3) -> Dict:
        """Generate response using Knowledge Base + LLM"""
        try:
            response = self.bedrock_agent.retrieve_and_generate(
                input={
                    'text': query
                },
                retrieveAndGenerateConfiguration={
                    'type': 'KNOWLEDGE_BASE',
                    'knowledgeBaseConfiguration': {
                        'knowledgeBaseId': self.knowledge_base_id,
                        'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0'
                    }
                }
            )
            
            return {
                'response': response['output']['text'],
                'citations': response.get('citations', []),
                'session_id': response.get('sessionId')
            }
            
        except Exception as e:
            print(f"RAG generation error: {e}")
            return {'response': f"Error: {str(e)}", 'citations': []}
