#!/usr/bin/env python3
"""
Process existing TXT files and add embeddings
"""

import os
import glob
from dynamodb_rag import DynamoDBRAG

def process_txt_files(directory_path: str = "."):
    """Process all TXT files in directory and add embeddings"""
    
    # Initialize RAG system
    rag = DynamoDBRAG("sme-rag-documents-1758382778")
    
    # Find all TXT files
    txt_files = glob.glob(os.path.join(directory_path, "*.txt"))
    
    if not txt_files:
        print("❌ No TXT files found in current directory")
        return
    
    print(f"📄 Found {len(txt_files)} TXT files")
    
    processed_count = 0
    
    for file_path in txt_files:
        filename = os.path.basename(file_path)
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if not content:
                print(f"⚠️  Skipping empty file: {filename}")
                continue
            
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
            print(f"❌ Error processing {filename}: {e}")
    
    print(f"\n🎉 Successfully processed {processed_count}/{len(txt_files)} files")
    
    # Test search
    print("\n🔍 Testing search with sample queries...")
    test_queries = ["criteria", "requirements", "skills", "experience"]
    
    for query in test_queries:
        results = rag.search_documents(query, limit=2)
        if results:
            print(f"\n🔎 '{query}' -> {len(results)} results (best score: {results[0]['score']:.3f})")

def chunk_text(text: str, chunk_size: int = 1000) -> list:
    """Split text into chunks"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
    
    return chunks

if __name__ == "__main__":
    print("🚀 Processing TXT files and adding embeddings...")
    print("=" * 50)
    
    process_txt_files()
    
    print("\n✅ Done! You can now query these files using the chatbot.")
