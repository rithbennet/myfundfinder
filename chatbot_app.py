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
    
    def expand_query(self, query: str) -> List[str]:
        """Expand query with related terms and variations"""
        expanded_queries = [query]
        
        # Add variations
        words = query.lower().split()
        
        # Add individual important words (longer than 3 characters)
        important_words = [w for w in words if len(w) > 3 and w not in ['what', 'how', 'when', 'where', 'why', 'which', 'that', 'this']]
        expanded_queries.extend(important_words)
        
        # Add partial phrases
        if len(words) > 2:
            for i in range(len(words) - 1):
                phrase = ' '.join(words[i:i+2])
                if len(phrase) > 5:
                    expanded_queries.append(phrase)
        
        return list(set(expanded_queries))  # Remove duplicates
    
    def search_documents(self, query: str) -> List[Dict]:
        """Enhanced search with query expansion and multi-tier results"""
        try:
            all_results = {}
            
            # Get expanded queries
            queries = self.expand_query(query)
            
            # Search with main query (highest weight)
            main_results = self.rag_adapter.similarity_search(
                query=query,
                limit=6,
                min_score=0.3
            )
            
            # Add main results with full weight
            for result in main_results:
                doc_id = result.doc_id
                score = result.score
                
                if doc_id not in all_results or score > all_results[doc_id]['score']:
                    confidence_tier = 'high' if score > 0.7 else 'medium' if score > 0.5 else 'low'
                    all_results[doc_id] = {
                        'text': result.text,
                        'score': score,
                        'confidence_tier': confidence_tier,
                        'source_document': result.metadata.get('source_file', 'Unknown'),
                        'chunk_index': result.metadata.get('chunk_index', 0),
                        'metadata': result.metadata,
                        'match_type': 'direct'
                    }
            
            # Search with expanded queries (reduced weight)
            for expanded_query in queries[1:3]:  # Use top 2 expanded queries
                expanded_results = self.rag_adapter.similarity_search(
                    query=expanded_query,
                    limit=3,
                    min_score=0.4
                )
                
                for result in expanded_results:
                    doc_id = result.doc_id
                    # Reduce score for expanded query matches
                    adjusted_score = result.score * 0.8
                    
                    if doc_id not in all_results or adjusted_score > all_results[doc_id]['score']:
                        confidence_tier = 'medium' if adjusted_score > 0.5 else 'low'
                        all_results[doc_id] = {
                            'text': result.text,
                            'score': adjusted_score,
                            'confidence_tier': confidence_tier,
                            'source_document': result.metadata.get('source_file', 'Unknown'),
                            'chunk_index': result.metadata.get('chunk_index', 0),
                            'metadata': result.metadata,
                            'match_type': 'expanded'
                        }
            
            # Sort by score and return top results
            search_results = list(all_results.values())
            search_results.sort(key=lambda x: x['score'], reverse=True)
            
            return search_results[:8]  # Return top 8 results
            
        except Exception as e:
            print(f"Error in enhanced search: {e}")
            return []
    
    def generate_response(self, query: str, search_results: List[Dict]) -> str:
        """Generate an enhanced response based on search results with better information synthesis"""
        if not search_results:
            return f"""I couldn't find specific information about "{query}" in the uploaded documents. 
            
Here's what you can try:
• Upload more TXT documents related to your query
• Try different keywords or phrases
• Check if your documents are properly processed

Would you like to upload a document or try a different search?"""
        
        # Separate high and medium confidence results
        high_confidence = [r for r in search_results if r.get('confidence_tier') == 'high']
        medium_confidence = [r for r in search_results if r.get('confidence_tier') == 'medium']
        
        # Build comprehensive response
        response_parts = []
        
        # Main answer from high confidence results
        if high_confidence:
            response_parts.append(f"**Direct Answer for '{query}':**")
            
            # Synthesize information from top results
            main_content = []
            for result in high_confidence[:2]:
                # Extract key sentences that might contain the answer
                sentences = result['text'].split('.')
                relevant_sentences = [s.strip() for s in sentences if len(s.strip()) > 20][:2]
                main_content.extend(relevant_sentences)
            
            response_parts.append(" ".join(main_content[:3]) + ".")
            response_parts.append("")
        
        # Supporting information
        response_parts.append("**Supporting Information:**")
        
        for i, result in enumerate(search_results[:4], 1):
            confidence_indicator = "🟢" if result['score'] > 0.7 else "🟡" if result['score'] > 0.5 else "🟠"
            
            # Truncate text intelligently at sentence boundaries
            text = result['text']
            if len(text) > 300:
                sentences = text.split('.')
                truncated = ""
                for sentence in sentences:
                    if len(truncated + sentence) < 280:
                        truncated += sentence + "."
                    else:
                        break
                text = truncated if truncated else text[:280] + "..."
            
            response_parts.append(
                f"{i}. {confidence_indicator} **{result['source_document']}** (Score: {result['score']:.2f})\n"
                f"   {text}\n"
            )
        
        # Summary section
        sources = list(set([r['source_document'] for r in search_results]))
        avg_score = sum([r['score'] for r in search_results]) / len(search_results)
        
        response_parts.append("---")
        response_parts.append(f"**Summary:** Found {len(search_results)} relevant passages from {len(sources)} document(s)")
        response_parts.append(f"**Average Confidence:** {avg_score:.2f}")
        response_parts.append(f"**Sources:** {', '.join(sources[:3])}")
        
        if len(sources) > 3:
            response_parts.append(f"   ...and {len(sources) - 3} more")
        
        return "\n".join(response_parts)
    
    def chat(self, user_message: str) -> Dict:
        """Enhanced chat function with better analytics"""
        start_time = time.time()
        
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
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Analyze search quality
        high_confidence_count = len([r for r in search_results if r.get('confidence_tier') == 'high'])
        medium_confidence_count = len([r for r in search_results if r.get('confidence_tier') == 'medium'])
        avg_score = sum([r['score'] for r in search_results]) / len(search_results) if search_results else 0
        
        # Add bot response to history with analytics
        self.chat_history.append({
            'type': 'bot',
            'message': bot_response,
            'timestamp': time.time(),
            'search_results': len(search_results),
            'high_confidence_results': high_confidence_count,
            'medium_confidence_results': medium_confidence_count,
            'average_score': avg_score,
            'response_time': response_time
        })
        
        return {
            'response': bot_response,
            'search_results_count': len(search_results),
            'high_confidence_count': high_confidence_count,
            'medium_confidence_count': medium_confidence_count,
            'average_score': round(avg_score, 3),
            'response_time': round(response_time, 2),
            'sources': list(set([r.get('source_document', 'Unknown') for r in search_results])),
            'search_analytics': {
                'total_results': len(search_results),
                'confidence_distribution': {
                    'high': high_confidence_count,
                    'medium': medium_confidence_count,
                    'low': len(search_results) - high_confidence_count - medium_confidence_count
                },
                'top_scores': [r['score'] for r in search_results[:3]]
            }
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

@app.route('/search', methods=['POST'])
def detailed_search():
    """Detailed search endpoint with full analytics"""
    data = request.get_json()
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        start_time = time.time()
        search_results = chatbot.search_documents(query)
        search_time = time.time() - start_time
        
        # Prepare detailed results
        detailed_results = []
        for result in search_results:
            detailed_results.append({
                'text': result['text'],
                'score': result['score'],
                'confidence_tier': result['confidence_tier'],
                'source_document': result['source_document'],
                'chunk_index': result['chunk_index'],
                'match_type': result.get('match_type', 'direct'),
                'word_count': len(result['text'].split()),
                'char_count': len(result['text'])
            })
        
        return jsonify({
            'query': query,
            'results': detailed_results,
            'total_results': len(search_results),
            'search_time': round(search_time, 3),
            'analytics': {
                'confidence_distribution': {
                    'high': len([r for r in search_results if r.get('confidence_tier') == 'high']),
                    'medium': len([r for r in search_results if r.get('confidence_tier') == 'medium']),
                    'low': len([r for r in search_results if r.get('confidence_tier') == 'low'])
                },
                'average_score': sum([r['score'] for r in search_results]) / len(search_results) if search_results else 0,
                'sources': list(set([r['source_document'] for r in search_results]))
            }
        })
        
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
