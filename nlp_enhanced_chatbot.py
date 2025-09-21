#!/usr/bin/env python3
"""
NLP Enhanced RAG Chatbot using Bedrock Claude for natural responses
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import boto3
import json
import time
from typing import List, Dict
from werkzeug.utils import secure_filename
from dynamodb_rag import DynamoDBRAG

app = Flask(__name__)
CORS(app)

class NLPEnhancedChatbot:
    def __init__(self):
        self.bucket_name = "sme-rag-documents-1758382778"
        self.rag = DynamoDBRAG(self.bucket_name)
        self.bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.chat_history = []
    
    def generate_natural_response(self, query: str, context_docs: List[Dict]) -> str:
        """Generate natural response using available Bedrock models"""
        if not context_docs:
            return f"I don't have specific information about '{query}' in the uploaded documents. Could you try different keywords or upload relevant documents?"
        
        # Prepare context from retrieved documents
        context_text = ""
        sources = []
        for i, doc in enumerate(context_docs[:3], 1):
            source = doc['filename'].split('_chunk_')[0]
            sources.append(source)
            context_text += f"\nSource {i} ({source}):\n{doc['text'][:400]}...\n"
        
        # Try different models in order of preference
        models_to_try = [
            "amazon.titan-text-express-v1",
            "amazon.titan-text-lite-v1",
            "ai21.j2-mid-v1"
        ]
        
        for model_id in models_to_try:
            try:
                if "titan" in model_id:
                    return self._generate_with_titan(query, context_text, sources, model_id)
                elif "ai21" in model_id:
                    return self._generate_with_ai21(query, context_text, sources, model_id)
            except Exception as e:
                print(f"Model {model_id} failed: {e}")
                continue
        
        # If all models fail, use enhanced fallback
        return self._enhanced_fallback_response(query, context_docs)
    
    def _generate_with_titan(self, query: str, context: str, sources: List[str], model_id: str) -> str:
        """Generate response using Titan model"""
        prompt = f"""Answer the following question based only on the provided context. Be conversational and helpful.

Question: {query}

Context:
{context}

Instructions:
- Answer directly and naturally
- Use bullet points for lists or criteria
- Mention which source the information comes from
- If the context doesn't fully answer the question, say so

Answer:"""

        body = json.dumps({
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 400,
                "temperature": 0.3,
                "topP": 0.9
            }
        })
        
        response = self.bedrock_client.invoke_model(
            modelId=model_id,
            body=body,
            contentType='application/json',
            accept='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['results'][0]['outputText'].strip()
    
    def _generate_with_ai21(self, query: str, context: str, sources: List[str], model_id: str) -> str:
        """Generate response using AI21 model"""
        prompt = f"Question: {query}\n\nContext: {context}\n\nAnswer based on the context:"
        
        body = json.dumps({
            "prompt": prompt,
            "maxTokens": 300,
            "temperature": 0.3
        })
        
        response = self.bedrock_client.invoke_model(
            modelId=model_id,
            body=body,
            contentType='application/json',
            accept='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['completions'][0]['data']['text'].strip()
    
    def _enhanced_fallback_response(self, query: str, context_docs: List[Dict]) -> str:
        """Enhanced fallback with better formatting"""
        if not context_docs:
            return f"I couldn't find information about '{query}' in the documents."
        
        # Check if it's a list/criteria query
        is_list_query = any(word in query.lower() for word in 
                          ['criteria', 'requirements', 'list', 'what are', 'skills', 'steps'])
        
        response_parts = []
        
        if is_list_query:
            response_parts.append(f"Here are the {query.lower().replace('what are the ', '').replace('what are ', '')} I found:\n")
        else:
            response_parts.append(f"Based on the documents, here's what I found about '{query}':\n")
        
        for i, doc in enumerate(context_docs[:2], 1):
            source = doc['filename'].split('_chunk_')[0]
            score_indicator = "🟢" if doc['score'] > 0.5 else "🟡"
            
            # Extract and format content
            text = doc['text']
            if is_list_query:
                # Look for list items
                lines = text.split('\n')
                list_items = []
                for line in lines:
                    line = line.strip()
                    if (line.startswith('-') or line.startswith('•') or 
                        line.startswith('*') or (len(line) > 2 and line[0:2].replace('.', '').isdigit())):
                        list_items.append(line)
                
                if list_items:
                    text = '\n'.join(list_items[:8])  # Show up to 8 items
                else:
                    text = text[:300] + "..." if len(text) > 300 else text
            else:
                text = text[:300] + "..." if len(text) > 300 else text
            
            response_parts.append(f"{score_indicator} **From {source}:**")
            response_parts.append(text)
            response_parts.append("")
        
        # Add source summary
        sources = list(set([doc['filename'].split('_chunk_')[0] for doc in context_docs]))
        if len(sources) > 1:
            response_parts.append(f"*Information found in {len(sources)} documents: {', '.join(sources)}*")
        
        return '\n'.join(response_parts)
    
    def _fallback_response(self, query: str, context_docs: List[Dict]) -> str:
        """Fallback structured response if Claude fails"""
        response_parts = [f"Based on the documents, here's what I found about '{query}':\n"]
        
        for i, doc in enumerate(context_docs[:2], 1):
            source = doc['filename'].split('_chunk_')[0]
            score_indicator = "🟢" if doc['score'] > 0.5 else "🟡"
            
            # Extract key information
            text = doc['text'][:300] + "..." if len(doc['text']) > 300 else doc['text']
            
            response_parts.append(f"{score_indicator} **From {source}:**")
            response_parts.append(text)
            response_parts.append("")
        
        return '\n'.join(response_parts)
    
    def search_and_respond(self, query: str) -> Dict:
        """Search and generate natural response using Claude"""
        try:
            start_time = time.time()
            
            # Search for relevant documents
            results = self.rag.search_documents(query, limit=5)
            
            search_time = time.time() - start_time
            
            # Generate natural response using Claude
            response_start = time.time()
            natural_response = self.generate_natural_response(query, results)
            response_time = time.time() - response_start
            
            # Prepare sources info
            sources = list(set([r['filename'].split('_chunk_')[0] for r in results]))
            avg_score = sum([r['score'] for r in results]) / len(results) if results else 0
            
            return {
                'response': natural_response,
                'results_count': len(results),
                'sources': sources,
                'average_score': avg_score,
                'search_time': search_time,
                'generation_time': response_time,
                'total_time': search_time + response_time
            }
            
        except Exception as e:
            return {
                'response': f"I encountered an error while searching: {str(e)}",
                'results_count': 0,
                'sources': [],
                'search_time': 0,
                'generation_time': 0
            }
    
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
            chunks = self._chunk_text(file_content)
            stored_docs = []
            
            for i, chunk in enumerate(chunks):
                chunk_filename = f"{filename}_chunk_{i}" if len(chunks) > 1 else filename
                doc_id = self.rag.store_document(chunk, chunk_filename)
                stored_docs.append(doc_id)
            
            return {
                'success': True,
                'message': f"Successfully uploaded '{filename}' and created {len(chunks)} searchable chunks!",
                'chunks_count': len(chunks)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Upload failed: {str(e)}"
            }
    
    def _chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks

# Initialize chatbot
chatbot = NLPEnhancedChatbot()

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Add to chat history
    chatbot.chat_history.append({
        'type': 'user',
        'message': user_message,
        'timestamp': time.time()
    })
    
    result = chatbot.search_and_respond(user_message)
    
    # Add bot response to history
    chatbot.chat_history.append({
        'type': 'bot',
        'message': result['response'],
        'timestamp': time.time(),
        'metadata': {
            'sources': result.get('sources', []),
            'results_count': result.get('results_count', 0),
            'total_time': result.get('total_time', 0)
        }
    })
    
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
        doc_count = chatbot.rag.get_document_count()
        
        return jsonify({
            'status': 'healthy',
            'bucket': chatbot.bucket_name,
            'total_documents': doc_count,
            'embedding_model': 'amazon.titan-embed-text-v1',
            'nlp_model': 'anthropic.claude-3-haiku-20240307-v1:0',
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

@app.route('/documents', methods=['GET'])
def list_documents():
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
                    'last_updated': doc['timestamp']
                }
            
            grouped[base_name]['chunks'] += 1
            grouped[base_name]['total_words'] += doc.get('word_count', 0)
            grouped[base_name]['last_updated'] = max(grouped[base_name]['last_updated'], doc['timestamp'])
        
        return jsonify({
            'documents': list(grouped.values()),
            'count': len(grouped)
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'documents': []}), 500

if __name__ == '__main__':
    print("🚀 Starting NLP Enhanced RAG Chatbot")
    print("🧠 NLP Model: Claude 3 Haiku")
    print("🔍 Embeddings: Titan")
    print("🗄️ Storage: DynamoDB + S3")
    print("🌐 Open: http://localhost:9000")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=9000)
