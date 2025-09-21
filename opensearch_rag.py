#!/usr/bin/env python3
"""
Simple RAG using OpenSearch Serverless for vector storage
"""

import boto3
import json
import numpy as np
from typing import List, Dict
from opensearchpy import OpenSearch, RequestsHttpConnection
from aws_requests_auth.aws_auth import AWSRequestsAuth

class OpenSearchRAG:
    def __init__(self, bucket_name: str, opensearch_endpoint: str, aws_region: str = "us-east-1"):
        self.s3_client = boto3.client('s3', region_name=aws_region)
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=aws_region)
        self.bucket_name = bucket_name
        self.aws_region = aws_region
        
        # OpenSearch client with AWS auth
        credentials = boto3.Session().get_credentials()
        awsauth = AWSRequestsAuth(credentials, aws_region, 'aoss')
        
        self.opensearch_client = OpenSearch(
            hosts=[{'host': opensearch_endpoint, 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )
        
        self.index_name = "documents"
        self._create_index()
    
    def _create_index(self):
        """Create OpenSearch index for vectors"""
        index_body = {
            "mappings": {
                "properties": {
                    "text": {"type": "text"},
                    "filename": {"type": "keyword"},
                    "embedding": {
                        "type": "knn_vector",
                        "dimension": 1536,
                        "method": {
                            "name": "hnsw",
                            "space_type": "cosinesimil"
                        }
                    },
                    "timestamp": {"type": "date"}
                }
            }
        }
        
        try:
            if not self.opensearch_client.indices.exists(self.index_name):
                self.opensearch_client.indices.create(self.index_name, body=index_body)
        except Exception as e:
            print(f"Index creation error: {e}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using Bedrock"""
        body = json.dumps({"inputText": text})
        
        response = self.bedrock_client.invoke_model(
            modelId="amazon.titan-embed-text-v1",
            body=body,
            contentType='application/json',
            accept='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['embedding']
    
    def store_document(self, text: str, filename: str) -> str:
        """Store document with embedding in OpenSearch"""
        embedding = self.generate_embedding(text)
        
        doc = {
            "text": text,
            "filename": filename,
            "embedding": embedding,
            "timestamp": "now"
        }
        
        response = self.opensearch_client.index(
            index=self.index_name,
            body=doc
        )
        
        return response['_id']
    
    def search_documents(self, query: str, limit: int = 5) -> List[Dict]:
        """Search documents using vector similarity"""
        query_embedding = self.generate_embedding(query)
        
        search_body = {
            "size": limit,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": query_embedding,
                        "k": limit
                    }
                }
            }
        }
        
        response = self.opensearch_client.search(
            index=self.index_name,
            body=search_body
        )
        
        results = []
        for hit in response['hits']['hits']:
            results.append({
                'text': hit['_source']['text'],
                'filename': hit['_source']['filename'],
                'score': hit['_score'],
                'id': hit['_id']
            })
        
        return results
