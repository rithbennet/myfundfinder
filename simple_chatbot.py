#!/usr/bin/env python3
"""
Simple RAG Chatbot without MongoDB - uses S3 for storage
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import boto3
import json
import os
import re
from typing import List, Dict
import time
from werkzeug.utils import secure_filename
from simple_bedrock_rag import SimpleBedrockRAG

app = Flask(__name__)
CORS(app)

class SimpleRAGChatbot:
    def __init__(self):
        self.bucket_name = "sme-rag-documents-1758382778"
        self.rag = SimpleBedrockRAG(self.bucket_name)
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
            # Store original document
            self.rag.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=f"documents/{filename}",
                Body=file_content.encode('utf-8'),
                ContentType='text/plain'
            )
            
            # Create chunks and store with embeddings
            chunks = self.chunk_text(file_content)
            stored_chunks = []
            
            for i, chunk in enumerate(chunks):
                chunk_filename = f"{filename}_chunk_{i}"
                doc_key = self.rag.store_document_with_embedding(chunk, chunk_filename)
                stored_chunks.append(doc_key)
            
            return {
                'success': True,
                'message': f"Uploaded '{filename}' with {len(chunks)} chunks",
                'chunks_count': len(chunks)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Error: {str(e)}"
            }
    
    def search_and_respond(self, query: str) -> Dict:
        """Search documents and generate response"""
        try:
            # Search for relevant documents
            results = self.rag.search_documents(query, limit=5)
            
            if not results:
                return {
                    'response': f"No relevant information found for '{query}'. Try uploading documents or using different keywords.",
                    'results_count': 0,
                    'sources': []
                }
            
            # Generate response
            response_parts = [f"**Answer for '{query}':**\n"]
            
            # Add top results
            for i, result in enumerate(results[:3], 1):
                score_indicator = "🟢" if result['score'] > 0.7 else "🟡" if result['score'] > 0.5 else "🟠"
                
                # Get relevant excerpt
                text = result['text']
                if len(text) > 300:
                    # Find sentences containing query words
                    query_words = query.lower().split()
                    sentences = text.split('.')
                    
                    relevant_sentences = []
                    for sentence in sentences:
                        if any(word in sentence.lower() for word in query_words):
                            relevant_sentences.append(sentence.strip())
                    
                    if relevant_sentences:
                        text = '. '.join(relevant_sentences[:2]) + '.'
                    else:
                        text = text[:300] + '...'
                
                response_parts.append(
                    f"{i}. {score_indicator} **{result['filename']}** (Score: {result['score']:.2f})\n"
                    f"   {text}\n"
                )
            
            # Add summary
            sources = list(set([r['filename'].split('_chunk_')[0] for r in results]))
            avg_score = sum([r['score'] for r in results]) / len(results)
            
            response_parts.append("---")
            response_parts.append(f"**Found {len(results)} matches from {len(sources)} document(s)**")
            response_parts.append(f"**Average confidence: {avg_score:.2f}**")
            
            return {
                'response': '\n'.join(response_parts),
                'results_count': len(results),
                'sources': sources,
                'average_score': avg_score
            }
            
        except Exception as e:
            return {
                'response': f"Search error: {str(e)}",
                'results_count': 0,
                'sources': []
            }

# Initialize chatbot
chatbot = SimpleRAGChatbot()

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

@app.route('/status', methods=['GET'])
def status():
    try:
        # Count embedded documents
        response = chatbot.rag.s3_client.list_objects_v2(
            Bucket=chatbot.bucket_name,
            Prefix="embeddings/"
        )
        
        embedded_docs = len([obj for obj in response.get('Contents', []) if obj['Key'].endswith('.json')])
        
        # Count original documents
        docs_response = chatbot.rag.s3_client.list_objects_v2(
            Bucket=chatbot.bucket_name,
            Prefix="documents/"
        )
        
        original_docs = len([obj for obj in docs_response.get('Contents', []) if not obj['Key'].endswith('/')])
        
        return jsonify({
            'status': 'healthy',
            'bucket': chatbot.bucket_name,
            'embedded_documents': embedded_docs,
            'original_documents': original_docs,
            'embedding_model': 'amazon.titan-embed-text-v1',
            'chat_messages': len(chatbot.chat_history)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error', 
            'error': str(e),
            'embedded_documents': 0,
            'original_documents': 0,
            'chat_messages': 0
        }), 500

@app.route('/documents', methods=['GET'])
def list_documents():
    """List all documents"""
    try:
        # List original documents
        response = chatbot.rag.s3_client.list_objects_v2(
            Bucket=chatbot.bucket_name,
            Prefix="documents/"
        )
        
        documents = []
        if 'Contents' in response:
            for obj in response['Contents']:
                if not obj['Key'].endswith('/'):  # Skip folders
                    filename = obj['Key'].replace('documents/', '')
                    documents.append({
                        'name': filename,
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'key': obj['Key']
                    })
        
        return jsonify({
            'documents': documents,
            'count': len(documents)
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'documents': []}), 500

if __name__ == '__main__':
    print("🚀 Starting Simple RAG Chatbot (No MongoDB)")
    print("📁 Bucket:", chatbot.bucket_name)
    print("🌐 Open: http://localhost:9000")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=9000)
