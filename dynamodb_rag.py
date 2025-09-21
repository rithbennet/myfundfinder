#!/usr/bin/env python3
"""
Simple RAG using DynamoDB for metadata + S3 for embeddings
"""

import boto3
import json
import numpy as np
from typing import List, Dict
import hashlib
import time

class DynamoDBRAG:
    def __init__(self, bucket_name: str, table_name: str = "rag-documents", aws_region: str = "us-east-1"):
        self.s3_client = boto3.client('s3', region_name=aws_region)
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=aws_region)
        self.dynamodb = boto3.resource('dynamodb', region_name=aws_region)
        
        self.bucket_name = bucket_name
        self.table_name = table_name
        self.table = self._get_or_create_table()
    
    def _get_or_create_table(self):
        """Create DynamoDB table if it doesn't exist"""
        try:
            table = self.dynamodb.Table(self.table_name)
            table.load()  # Check if table exists
            return table
        except:
            # Create table
            table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {'AttributeName': 'doc_id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'doc_id', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            
            # Wait for table to be created
            table.wait_until_exists()
            print(f"✅ Created DynamoDB table: {self.table_name}")
            return table
    
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
        """Store document with embedding"""
        # Generate unique ID
        doc_id = hashlib.md5(f"{filename}_{text[:100]}".encode()).hexdigest()
        
        # Generate embedding
        embedding = self.generate_embedding(text)
        
        # Store embedding in S3
        embedding_key = f"embeddings/{doc_id}.json"
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=embedding_key,
            Body=json.dumps(embedding),
            ContentType='application/json'
        )
        
        # Store metadata in DynamoDB
        self.table.put_item(
            Item={
                'doc_id': doc_id,
                'filename': filename,
                'text': text,
                'embedding_s3_key': embedding_key,
                'char_count': len(text),
                'word_count': len(text.split()),
                'timestamp': int(time.time())
            }
        )
        
        return doc_id
    
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
        
        # Get all documents from DynamoDB
        response = self.table.scan()
        documents = response['Items']
        
        results = []
        
        for doc in documents:
            try:
                # Get embedding from S3
                embedding_response = self.s3_client.get_object(
                    Bucket=self.bucket_name,
                    Key=doc['embedding_s3_key']
                )
                doc_embedding = json.loads(embedding_response['Body'].read())
                
                # Calculate similarity
                similarity = self.cosine_similarity(query_embedding, doc_embedding)
                
                if similarity > 0.2:  # Minimum threshold
                    results.append({
                        'doc_id': doc['doc_id'],
                        'text': doc['text'],
                        'filename': doc['filename'],
                        'score': similarity,
                        'word_count': doc.get('word_count', 0),
                        'timestamp': doc.get('timestamp', 0)
                    })
                    
            except Exception as e:
                print(f"Error processing document {doc['doc_id']}: {e}")
                continue
        
        # Sort by similarity and return top results
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]
    
    def get_document_count(self) -> int:
        """Get total number of documents"""
        response = self.table.scan(Select='COUNT')
        return response['Count']
    
    def list_documents(self) -> List[Dict]:
        """List all documents with metadata"""
        response = self.table.scan()
        
        documents = []
        for item in response['Items']:
            documents.append({
                'doc_id': item['doc_id'],
                'filename': item['filename'],
                'char_count': item.get('char_count', 0),
                'word_count': item.get('word_count', 0),
                'timestamp': item.get('timestamp', 0)
            })
        
        return documents
