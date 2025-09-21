"""
TXT File Processor for RAG System with Bedrock Embeddings
Processes multiple TXT files and uploads them to MongoDB with Bedrock-generated embeddings
"""

import os
import glob
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from bedrock_rag_adapter import BedrockRAGAdapter

# Load environment variables
load_dotenv()

class TXTProcessor:
    """Process TXT files and upload to RAG system"""
    
    def __init__(
        self,
        mongo_uri: str,
        db_name: str = "dev_trees_hire",
        collection_name: str = "txt_documents_rag",
        aws_region: str = "us-east-1",
        model_name: str = "amazon.titan-embed-text-v1"
    ):
        self.rag_adapter = BedrockRAGAdapter(
            mongo_uri=mongo_uri,
            db_name=db_name,
            collection_name=collection_name,
            embedding_method="bedrock",
            model_name=model_name,
            aws_region=aws_region
        )
        
        print(f"✅ Initialized Bedrock RAG Adapter")
        print(f"📊 Database: {db_name}")
        print(f"📁 Collection: {collection_name}")
        print(f"🤖 Model: {model_name}")
    
    def read_txt_file(self, file_path: str) -> Dict[str, Any]:
        """Read a TXT file and extract content and metadata"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
            
            if not content:
                raise ValueError("File is empty")
            
            # Extract metadata from file
            file_info = Path(file_path)
            metadata = {
                "source_file": file_info.name,
                "file_path": str(file_info.absolute()),
                "file_size": file_info.stat().st_size,
                "file_extension": file_info.suffix,
                "character_count": len(content),
                "word_count": len(content.split()),
                "processing_method": "bedrock_embeddings"
            }
            
            return {
                "content": content,
                "metadata": metadata
            }
            
        except Exception as e:
            print(f"❌ Error reading file {file_path}: {e}")
            return None
    
    def chunk_large_text(self, text: str, max_chars: int = 8000) -> List[str]:
        """Break large text into smaller chunks for better embedding quality"""
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        paragraphs = text.split('\n\n')
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk + paragraph) <= max_chars:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # If paragraphs are too long, split by sentences
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= max_chars:
                final_chunks.append(chunk)
            else:
                sentences = chunk.split('. ')
                temp_chunk = ""
                for sentence in sentences:
                    if len(temp_chunk + sentence) <= max_chars:
                        temp_chunk += sentence + ". "
                    else:
                        if temp_chunk:
                            final_chunks.append(temp_chunk.strip())
                        temp_chunk = sentence + ". "
                if temp_chunk:
                    final_chunks.append(temp_chunk.strip())
        
        return final_chunks
    
    def process_single_file(self, file_path: str) -> List[str]:
        """Process a single TXT file and upload to RAG system"""
        print(f"\n📄 Processing: {file_path}")
        
        # Read file
        file_data = self.read_txt_file(file_path)
        if not file_data:
            return []
        
        content = file_data["content"]
        base_metadata = file_data["metadata"]
        
        # Chunk large files
        chunks = self.chunk_large_text(content)
        print(f"📋 Split into {len(chunks)} chunks")
        
        document_ids = []
        
        for i, chunk in enumerate(chunks):
            try:
                # Create metadata for this chunk
                chunk_metadata = base_metadata.copy()
                chunk_metadata.update({
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "is_chunked": len(chunks) > 1
                })
                
                # Store in RAG system
                doc_id = self.rag_adapter.store_document(
                    text=chunk,
                    metadata=chunk_metadata
                )
                
                document_ids.append(doc_id)
                print(f"  ✅ Chunk {i+1}/{len(chunks)} stored (ID: {doc_id[:8]}...)")
                
            except Exception as e:
                print(f"  ❌ Error processing chunk {i+1}: {e}")
        
        return document_ids
    
    def process_directory(self, directory_path: str, pattern: str = "*.txt") -> Dict[str, List[str]]:
        """Process all TXT files in a directory"""
        print(f"\n🔍 Scanning directory: {directory_path}")
        print(f"📋 Pattern: {pattern}")
        
        # Find all matching files
        file_pattern = os.path.join(directory_path, pattern)
        txt_files = glob.glob(file_pattern)
        
        if not txt_files:
            print(f"❌ No files found matching pattern: {file_pattern}")
            return {}
        
        print(f"📁 Found {len(txt_files)} files to process")
        
        results = {}
        
        for file_path in txt_files:
            try:
                document_ids = self.process_single_file(file_path)
                results[file_path] = document_ids
                print(f"✅ Completed: {os.path.basename(file_path)} ({len(document_ids)} documents)")
            except Exception as e:
                print(f"❌ Failed to process {file_path}: {e}")
                results[file_path] = []
        
        return results
    
    def process_file_list(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """Process a list of specific files"""
        print(f"\n📋 Processing {len(file_paths)} files")
        
        results = {}
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                results[file_path] = []
                continue
            
            try:
                document_ids = self.process_single_file(file_path)
                results[file_path] = document_ids
                print(f"✅ Completed: {os.path.basename(file_path)} ({len(document_ids)} documents)")
            except Exception as e:
                print(f"❌ Failed to process {file_path}: {e}")
                results[file_path] = []
        
        return results
    
    def get_collection_stats(self):
        """Display statistics about the processed documents"""
        try:
            stats = self.rag_adapter.get_collection_stats()
            print(f"\n📊 Collection Statistics:")
            print(f"  📄 Total documents: {stats.get('total_documents', 0)}")
            print(f"  🔢 Embedding dimension: {stats.get('embedding_dimension', 0)}")
            print(f"  🤖 Embedding method: {stats.get('embedding_method', 'unknown')}")
            print(f"  🎯 Model name: {stats.get('model_name', 'unknown')}")
            return stats
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return None
    
    def test_search(self, query: str, limit: int = 3):
        """Test search functionality with a sample query"""
        print(f"\n🔍 Testing search with query: '{query}'")
        try:
            results = self.rag_adapter.similarity_search(
                query=query,
                limit=limit,
                min_score=0.3
            )
            
            print(f"📋 Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"\n  {i}. Score: {result.score:.3f}")
                print(f"     File: {result.metadata.get('source_file', 'unknown')}")
                print(f"     Preview: {result.text[:200]}...")
            
            return results
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []

def main():
    """Main function to demonstrate usage"""
    
    # Configuration from environment variables
    MONGO_URI = os.getenv("MONGO_URI")
    if not MONGO_URI:
        print("❌ MONGO_URI environment variable is required")
        return
    
    # Initialize processor
    processor = TXTProcessor(
        mongo_uri=MONGO_URI,
        db_name="dev_trees_hire",
        collection_name="txt_documents_rag",
        aws_region="us-east-1",  # Change to your preferred region
        model_name="amazon.titan-embed-text-v1"  # or "cohere.embed-english-v3"
    )
    
    print("🚀 TXT File Processor initialized!")
    print("\n" + "="*60)
    print("USAGE EXAMPLES:")
    print("="*60)
    print("\n1. Process all TXT files in current directory:")
    print("   results = processor.process_directory('.')")
    print("\n2. Process specific files:")
    print("   results = processor.process_file_list(['file1.txt', 'file2.txt'])")
    print("\n3. Process files in another directory:")
    print("   results = processor.process_directory('/path/to/your/files')")
    print("\n4. Get collection statistics:")
    print("   processor.get_collection_stats()")
    print("\n5. Test search:")
    print("   processor.test_search('your search query')")
    print("="*60)
    
    # Example usage (uncomment to run)
    # results = processor.process_directory(".", "*.txt")
    # processor.get_collection_stats()
    # processor.test_search("example query")

if __name__ == "__main__":
    main()