#!/usr/bin/env python3
"""
Simple Bedrock RAG without MongoDB - stores embeddings in S3
"""

import boto3
import json
import numpy as np
from typing import List, Dict, Any
import hashlib

class SimpleBedrockRAG:
    def __init__(self, bucket_name: str, aws_region: str = "us-east-1"):
        self.s3_client = boto3.client('s3', region_name=aws_region)
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=aws_region)
        self.bucket_name = bucket_name
        self.model_name = "amazon.titan-embed-text-v1"
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using Bedrock Titan"""
        body = json.dumps({"inputText": text})
        
        response = self.bedrock_client.invoke_model(
            modelId=self.model_name,
            body=body,
            contentType='application/json',
            accept='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['embedding']
    
    def store_document_with_embedding(self, text: str, filename: str) -> str:
        """Store document and its embedding in S3"""
        # Generate embedding
        embedding = self.generate_embedding(text)
        
        # Create document object
        doc_data = {
            "text": text,
            "embedding": embedding,
            "filename": filename,
            "char_count": len(text),
            "word_count": len(text.split())
        }
        
        # Store in S3
        doc_key = f"embeddings/{filename}.json"
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=doc_key,
            Body=json.dumps(doc_data),
            ContentType='application/json'
        )
        
        return doc_key
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def search_documents(self, query: str, limit: int = 5) -> List[Dict]:
        """Search documents using embeddings"""
        # Generate query embedding
        query_embedding = self.generate_embedding(query)
        
        # Get all embedded documents
        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket_name,
            Prefix="embeddings/"
        )
        
        results = []
        
        if 'Contents' in response:
            for obj in response['Contents']:
                if obj['Key'].endswith('.json'):
                    # Load document
                    doc_response = self.s3_client.get_object(
                        Bucket=self.bucket_name,
                        Key=obj['Key']
                    )
                    doc_data = json.loads(doc_response['Body'].read())
                    
                    # Calculate similarity
                    similarity = self.cosine_similarity(
                        query_embedding, 
                        doc_data['embedding']
                    )
                    
                    if similarity > 0.2:  # Minimum threshold
                        results.append({
                            'text': doc_data['text'],
                            'filename': doc_data['filename'],
                            'score': similarity,
                            'word_count': doc_data.get('word_count', 0)
                        })
        
        # Sort by similarity and return top results
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]
