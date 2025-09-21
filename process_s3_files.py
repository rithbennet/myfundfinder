#!/usr/bin/env python3
"""
Download and process existing TXT files from S3 bucket
"""

import boto3
from dynamodb_rag import DynamoDBRAG

def process_s3_txt_files():
    """Download and process all TXT files from S3 bucket"""
    
    bucket_name = "sme-rag-documents-1758382778"
    s3_client = boto3.client('s3')
    rag = DynamoDBRAG(bucket_name)
    
    print(f"📁 Checking S3 bucket: {bucket_name}")
    
    try:
        # List all objects in the bucket
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' not in response:
            print("❌ No files found in S3 bucket")
            return
        
        txt_files = []
        for obj in response['Contents']:
            if obj['Key'].endswith('.txt'):
                txt_files.append(obj['Key'])
        
        if not txt_files:
            print("❌ No TXT files found in S3 bucket")
            return
        
        print(f"📄 Found {len(txt_files)} TXT files in S3:")
        for file_key in txt_files:
            print(f"  - {file_key}")
        
        processed_count = 0
        
        for file_key in txt_files:
            try:
                # Download file content
                response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
                content = response['Body'].read().decode('utf-8').strip()
                
                if not content:
                    print(f"⚠️  Skipping empty file: {file_key}")
                    continue
                
                # Get filename without path
                filename = file_key.split('/')[-1]
                
                # Chunk large files
                if len(content) > 2000:
                    chunks = chunk_text(content)
                    for i, chunk in enumerate(chunks):
                        chunk_name = f"{filename}_chunk_{i}"
                        doc_id = rag.store_document(chunk, chunk_name)
                        print(f"✅ Processed chunk {i+1}/{len(chunks)} of {filename}")
                else:
                    doc_id = rag.store_document(content, filename)
                    print(f"✅ Processed: {filename}")
                
                processed_count += 1
                
            except Exception as e:
                print(f"❌ Error processing {file_key}: {e}")
        
        print(f"\n🎉 Successfully processed {processed_count}/{len(txt_files)} files from S3")
        
        # Test search
        print("\n🔍 Testing search...")
        test_queries = ["criteria", "requirements", "skills", "hiring"]
        
        for query in test_queries:
            results = rag.search_documents(query, limit=2)
            if results:
                print(f"🔎 '{query}' -> {len(results)} results (best: {results[0]['score']:.3f})")
        
    except Exception as e:
        print(f"❌ Error accessing S3 bucket: {e}")

def chunk_text(text: str, chunk_size: int = 1000) -> list:
    """Split text into chunks"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
    
    return chunks

if __name__ == "__main__":
    print("🚀 Processing TXT files from S3 bucket...")
    print("=" * 50)
    
    process_s3_txt_files()
    
    print("\n✅ Done! You can now query these S3 files using the chatbot.")
