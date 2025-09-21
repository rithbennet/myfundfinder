#!/usr/bin/env python3
"""
SME RAG Chatbot Web Application
A Flask web app that provides a chat interface for the RAG system
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import boto3
import json
import os
import re
from typing import List, Dict
import hashlib
from werkzeug.utils import secure_filename
import time
from bedrock_rag_adapter import BedrockRAGAdapter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

class RAGChatbot:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket_name = "sme-rag-documents-1758382778"
        self.chat_history = []
        
        # Initialize Bedrock RAG adapter
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            raise ValueError("MONGO_URI environment variable is required")
            
        self.rag_adapter = BedrockRAGAdapter(
            mongo_uri=mongo_uri,
            db_name="dev_trees_hire",
            collection_name="txt_documents_rag",
            embedding_method="bedrock",
            model_name="amazon.titan-embed-text-v1",
            aws_region="us-east-1"
        )
        
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict]:
        """Split text into overlapping chunks"""
        text = re.sub(r'\\s+', ' ', text.strip())
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            
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
            response = self.s3_client.get_object(
                Bucket=self.bucket_name, 
                Key=document_key
            )
            content = response['Body'].read().decode('utf-8')
            
            chunks = self.chunk_text(content)
            
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
            return True
            
        except Exception as e:
            print(f"Error saving chunks: {e}")
            return False
    
    def search_documents(self, query: str) -> List[Dict]:
        """Search across all processed documents using Bedrock embeddings"""
        try:
            results = self.rag_adapter.similarity_search(
                query=query,
                limit=5,
                min_score=0.3
            )
            
            # Convert to dict format for compatibility
            search_results = []
            for result in results:
                search_results.append({
                    'text': result.text,
                    'score': result.score,
                    'source_document': result.metadata.get('source_file', 'Unknown'),
                    'chunk_index': result.metadata.get('chunk_index', 0),
                    'metadata': result.metadata
                })
            
            return search_results
            
        except Exception as e:
            print(f"Error searching with Bedrock: {e}")
            return []
    
    def generate_response(self, query: str, search_results: List[Dict]) -> str:
        """Generate a response based on search results"""
        if not search_results:
            return f"""I couldn't find specific information about "{query}" in the uploaded documents. 
            
Here's what you can try:
• Upload more TXT documents related to your query
• Try different keywords or phrases
• Check if your documents are properly processed

Would you like to upload a document or try a different search?"""
        
        # Create context from search results
        context_parts = []
        sources = set()
        
        for result in search_results:
            context_parts.append(result['text'][:400])
            sources.add(result.get('source_document', 'Unknown'))
        
        context = "\n\n".join(context_parts)
        
        # Generate response with better formatting
        response = f"""Based on the documents I found, here's what I can tell you about "{query}":

{context[:1200]}

**Sources:** {', '.join(sources)}
**Confidence Scores:** {', '.join([f"{r['score']:.2f}" for r in search_results[:3]])}

**Detailed Results:**
"""
        
        for i, result in enumerate(search_results[:3], 1):
            response += f"\n{i}. **Score: {result['score']:.2f}** | **Source: {result['source_document']}**\n   {result['text'][:200]}...\n"
        
        return response
    
    def chat(self, user_message: str) -> Dict:
        """Main chat function"""
        # Add user message to history
        self.chat_history.append({
            'type': 'user',
            'message': user_message,
            'timestamp': time.time()
        })
        
        # Search for relevant documents
        search_results = self.search_documents(user_message)
        
        # Generate response
        bot_response = self.generate_response(user_message, search_results)
        
        # Add bot response to history
        self.chat_history.append({
            'type': 'bot',
            'message': bot_response,
            'timestamp': time.time(),
            'search_results': len(search_results)
        })
        
        return {
            'response': bot_response,
            'search_results_count': len(search_results),
            'sources': list(set([r.get('source_document', 'Unknown') for r in search_results]))
        }
    
    def upload_document(self, file_content: str, filename: str) -> Dict:
        """Upload and process a new TXT document with Bedrock embeddings"""
        try:
            # Save to S3 for backup
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=f"documents/{filename}",
                Body=file_content.encode('utf-8'),
                ContentType='text/plain'
            )
            
            # Process with Bedrock RAG adapter
            chunks = self.chunk_large_text(file_content)
            document_ids = []
            
            for i, chunk in enumerate(chunks):
                metadata = {
                    "source_file": filename,
                    "file_path": f"uploaded/{filename}",
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "is_chunked": len(chunks) > 1,
                    "upload_method": "web_interface",
                    "character_count": len(chunk),
                    "word_count": len(chunk.split())
                }
                
                doc_id = self.rag_adapter.store_document(
                    text=chunk,
                    metadata=metadata
                )
                document_ids.append(doc_id)
            
            return {
                'success': True,
                'message': f"Document '{filename}' uploaded and processed with Bedrock embeddings! Created {len(chunks)} chunks.",
                'chunks_count': len(chunks),
                'document_ids': document_ids
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Error uploading document: {str(e)}"
            }
    
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
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

# Initialize the chatbot
chatbot = RAGChatbot()

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    try:
        result = chatbot.chat(user_message)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_document():
    """Handle document uploads"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        file_content = file.read().decode('utf-8')
        
        result = chatbot.upload_document(file_content, filename)
        return jsonify(result)

@app.route('/documents', methods=['GET'])
def list_documents():
    """List all available documents"""
    try:
        response = chatbot.s3_client.list_objects_v2(
            Bucket=chatbot.bucket_name,
            Prefix="documents/"
        )
        
        documents = []
        if 'Contents' in response:
            for obj in response['Contents']:
                if obj['Key'] != 'documents/':  # Skip the folder itself
                    documents.append({
                        'name': obj['Key'].replace('documents/', ''),
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat()
                    })
        
        return jsonify({'documents': documents})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/rag-stats', methods=['GET'])
def rag_stats():
    """Get RAG system statistics"""
    try:
        stats = chatbot.rag_adapter.get_collection_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """Get system status"""
    try:
        # Check S3 connection
        chatbot.s3_client.head_bucket(Bucket=chatbot.bucket_name)
        
        # Count documents and processed files
        docs_response = chatbot.s3_client.list_objects_v2(
            Bucket=chatbot.bucket_name,
            Prefix="documents/"
        )
        
        docs_count = len(docs_response.get('Contents', [])) - 1  # Subtract folder
        
        # Get RAG statistics
        rag_stats = chatbot.rag_adapter.get_collection_stats()
        
        return jsonify({
            'status': 'healthy',
            'bucket': chatbot.bucket_name,
            'documents_count': max(0, docs_count),
            'rag_documents': rag_stats.get('total_documents', 0),
            'embedding_method': rag_stats.get('embedding_method', 'bedrock'),
            'model_name': rag_stats.get('model_name', 'amazon.titan-embed-text-v1'),
            'chat_history_length': len(chatbot.chat_history)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("🚀 Starting SME RAG Chatbot...")
    print("📁 Bucket:", chatbot.bucket_name)
    print("🌐 Open your browser to: http://localhost:9000")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=9000)
