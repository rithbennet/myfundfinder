#!/usr/bin/env python3
"""
Improved RAG Chatbot using DynamoDB + S3
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import time
from typing import List, Dict
from werkzeug.utils import secure_filename
from dynamodb_rag import DynamoDBRAG

app = Flask(__name__)
CORS(app)

class ImprovedRAGChatbot:
    def __init__(self):
        self.bucket_name = "sme-rag-documents-1758382778"
        self.rag = DynamoDBRAG(self.bucket_name)
        self.chat_history = []
        
    def chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks
    
    def upload_document(self, file_content: str, filename: str) -> Dict:
        """Upload and process document"""
        try:
            # Store original document in S3
            self.rag.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=f"documents/{filename}",
                Body=file_content.encode('utf-8'),
                ContentType='text/plain'
            )
            
            # Create chunks and store with embeddings
            chunks = self.chunk_text(file_content)
            stored_docs = []
            
            for i, chunk in enumerate(chunks):
                chunk_filename = f"{filename}_chunk_{i}" if len(chunks) > 1 else filename
                doc_id = self.rag.store_document(chunk, chunk_filename)
                stored_docs.append(doc_id)
            
            return {
                'success': True,
                'message': f"Uploaded '{filename}' with {len(chunks)} chunks",
                'chunks_count': len(chunks),
                'document_ids': stored_docs
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Error: {str(e)}"
            }
    
    def search_and_respond(self, query: str) -> Dict:
        """Search documents and generate response"""
        try:
            start_time = time.time()
            
            # Search for relevant documents
            results = self.rag.search_documents(query, limit=6)
            
            search_time = time.time() - start_time
            
            if not results:
                return {
                    'response': f"No relevant information found for '{query}'. Try uploading documents or using different keywords.",
                    'results_count': 0,
                    'sources': [],
                    'search_time': search_time
                }
            
            # Generate enhanced response
            response_parts = [f"**Answer for '{query}':**\n"]
            
            # High confidence results (score > 0.6)
            high_conf = [r for r in results if r['score'] > 0.6]
            medium_conf = [r for r in results if 0.4 <= r['score'] <= 0.6]
            
            if high_conf:
                response_parts.append("**Direct matches:**")
                for i, result in enumerate(high_conf[:2], 1):
                    text = self._extract_relevant_text(result['text'], query)
                    response_parts.append(
                        f"{i}. 🟢 **{result['filename']}** (Score: {result['score']:.2f})\n"
                        f"   {text}\n"
                    )
                response_parts.append("")
            
            if medium_conf:
                response_parts.append("**Related information:**")
                for i, result in enumerate(medium_conf[:2], 1):
                    text = self._extract_relevant_text(result['text'], query)
                    response_parts.append(
                        f"{i}. 🟡 **{result['filename']}** (Score: {result['score']:.2f})\n"
                        f"   {text}\n"
                    )
            
            # Summary
            sources = list(set([r['filename'].split('_chunk_')[0] for r in results]))
            avg_score = sum([r['score'] for r in results]) / len(results)
            
            response_parts.append("---")
            response_parts.append(f"**Summary:** {len(results)} matches from {len(sources)} document(s)")
            response_parts.append(f"**Average confidence:** {avg_score:.2f}")
            response_parts.append(f"**Search time:** {search_time:.2f}s")
            
            return {
                'response': '\n'.join(response_parts),
                'results_count': len(results),
                'sources': sources,
                'average_score': avg_score,
                'search_time': search_time,
                'high_confidence_count': len(high_conf),
                'medium_confidence_count': len(medium_conf)
            }
            
        except Exception as e:
            return {
                'response': f"Search error: {str(e)}",
                'results_count': 0,
                'sources': [],
                'search_time': 0
            }
    
    def _extract_relevant_text(self, text: str, query: str, max_length: int = 300) -> str:
        """Extract most relevant part of text based on query"""
        if len(text) <= max_length:
            return text
        
        # Find sentences containing query words
        query_words = query.lower().split()
        sentences = text.split('.')
        
        relevant_sentences = []
        for sentence in sentences:
            if any(word in sentence.lower() for word in query_words):
                relevant_sentences.append(sentence.strip())
        
        if relevant_sentences:
            result = '. '.join(relevant_sentences[:2])
            if len(result) <= max_length:
                return result + '.'
        
        # Fallback to first part
        return text[:max_length] + '...'

# Initialize chatbot
chatbot = ImprovedRAGChatbot()

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    result = chatbot.search_and_respond(user_message)
    return jsonify(result)

@app.route('/upload', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    filename = secure_filename(file.filename)
    file_content = file.read().decode('utf-8')
    
    result = chatbot.upload_document(file_content, filename)
    return jsonify(result)

@app.route('/documents', methods=['GET'])
def list_documents():
    """List all documents"""
    try:
        documents = chatbot.rag.list_documents()
        
        # Group by original filename
        grouped = {}
        for doc in documents:
            base_name = doc['filename'].split('_chunk_')[0]
            if base_name not in grouped:
                grouped[base_name] = {
                    'name': base_name,
                    'chunks': 0,
                    'total_words': 0,
                    'total_chars': 0,
                    'last_updated': doc['timestamp']
                }
            
            grouped[base_name]['chunks'] += 1
            grouped[base_name]['total_words'] += doc.get('word_count', 0)
            grouped[base_name]['total_chars'] += doc.get('char_count', 0)
            grouped[base_name]['last_updated'] = max(grouped[base_name]['last_updated'], doc['timestamp'])
        
        return jsonify({
            'documents': list(grouped.values()),
            'count': len(grouped)
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'documents': []}), 500

@app.route('/status', methods=['GET'])
def status():
    try:
        doc_count = chatbot.rag.get_document_count()
        
        return jsonify({
            'status': 'healthy',
            'bucket': chatbot.bucket_name,
            'total_documents': doc_count,
            'embedding_model': 'amazon.titan-embed-text-v1',
            'storage': 'DynamoDB + S3',
            'chat_messages': len(chatbot.chat_history)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error', 
            'error': str(e),
            'total_documents': 0,
            'chat_messages': 0
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Improved RAG Chatbot (DynamoDB + S3)")
    print("📁 Bucket:", chatbot.bucket_name)
    print("🗄️ Storage: DynamoDB + S3")
    print("🌐 Open: http://localhost:9000")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=9000)
