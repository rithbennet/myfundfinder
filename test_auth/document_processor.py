#!/usr/bin/env python3
"""
Document Processor for SME RAG System
Handles document chunking, embedding generation, and basic search functionality.
"""

import boto3
import json
import re
from typing import List, Dict
import hashlib

class DocumentProcessor:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket_name = "sme-rag-documents-1758382778"
        
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict]:
        """Split text into overlapping chunks"""
        # Clean the text
        text = re.sub(r'\s+', ' ', text.strip())
        
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            # Create chunk metadata
            chunk_id = hashlib.md5(chunk_text.encode()).hexdigest()[:12]
            chunk = {
                'id': chunk_id,
                'text': chunk_text,
                'start_word': i,
                'end_word': min(i + chunk_size, len(words)),
                'word_count': len(chunk_words)
            }
            chunks.append(chunk)
            
        return chunks
    
    def process_document(self, document_key: str) -> List[Dict]:
        """Process a document from S3 and create chunks"""
        try:
            # Download document from S3
            response = self.s3_client.get_object(
                Bucket=self.bucket_name, 
                Key=document_key
            )
            content = response['Body'].read().decode('utf-8')
            
            # Create chunks
            chunks = self.chunk_text(content)
            
            # Add document metadata to each chunk
            for chunk in chunks:
                chunk['source_document'] = document_key
                chunk['document_type'] = document_key.split('.')[-1]
            
            return chunks
            
        except Exception as e:
            print(f"Error processing document {document_key}: {e}")
            return []
    
    def save_processed_chunks(self, chunks: List[Dict], output_key: str):
        """Save processed chunks to S3"""
        try:
            chunks_json = json.dumps(chunks, indent=2)
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=f"processed/{output_key}",
                Body=chunks_json.encode('utf-8'),
                ContentType='application/json'
            )
            print(f"✅ Saved {len(chunks)} chunks to processed/{output_key}")
            
        except Exception as e:
            print(f"❌ Error saving chunks: {e}")
    
    def simple_search(self, query: str, processed_file: str) -> List[Dict]:
        """Simple keyword-based search (before we have vector search)"""
        try:
            # Load processed chunks
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=f"processed/{processed_file}"
            )
            chunks = json.loads(response['Body'].read().decode('utf-8'))
            
            # Simple keyword matching
            query_words = query.lower().split()
            results = []
            
            for chunk in chunks:
                score = 0
                chunk_text_lower = chunk['text'].lower()
                
                # Count keyword matches
                for word in query_words:
                    score += chunk_text_lower.count(word)
                
                if score > 0:
                    chunk['relevance_score'] = score
                    results.append(chunk)
            
            # Sort by relevance
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
            return results[:5]  # Return top 5 results
            
        except Exception as e:
            print(f"❌ Error searching: {e}")
            return []
    
    def display_search_results(self, results: List[Dict], query: str):
        """Display search results in a nice format"""
        print(f"\n🔍 Search Results for: '{query}'")
        print("=" * 60)
        
        if not results:
            print("No results found.")
            return
        
        for i, result in enumerate(results, 1):
            print(f"\n📄 Result {i} (Score: {result.get('relevance_score', 0)})")
            print(f"Source: {result.get('source_document', 'Unknown')}")
            print(f"Chunk ID: {result.get('id', 'Unknown')}")
            print(f"Text: {result.get('text', '')[:200]}...")
            print("-" * 40)

def main():
    processor = DocumentProcessor()
    
    print("🚀 SME RAG Document Processor")
    print("=" * 40)
    
    # Process the sample document
    print("\n1. Processing sample document...")
    chunks = processor.process_document('documents/sample_sme_doc.txt')
    
    if chunks:
        print(f"✅ Created {len(chunks)} chunks from sample document")
        
        # Save processed chunks
        processor.save_processed_chunks(chunks, 'sample_sme_doc_chunks.json')
        
        # Demo search functionality
        print("\n2. Testing search functionality...")
        
        search_queries = [
            "SME business process",
            "vector search OpenSearch",
            "document ingestion"
        ]
        
        for query in search_queries:
            results = processor.simple_search(query, 'sample_sme_doc_chunks.json')
            processor.display_search_results(results, query)
            
    else:
        print("❌ Failed to process document")
    
    print("\n✨ Next steps:")
    print("1. Add more documents to the 'documents/' folder in S3")
    print("2. Set up OpenSearch for proper vector search")
    print("3. Integrate with embedding models (OpenAI, Bedrock, etc.)")
    print("4. Create API endpoints for document upload and search")

if __name__ == "__main__":
    main()