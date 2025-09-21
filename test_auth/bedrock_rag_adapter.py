"""
Enhanced RAG Adapter with AWS Bedrock integration for embeddings
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB
import pymongo
from pymongo import MongoClient
from bson import ObjectId

# AWS Bedrock
try:
    import boto3
    from botocore.exceptions import ClientError
    BEDROCK_AVAILABLE = True
except ImportError:
    BEDROCK_AVAILABLE = False
    print("Warning: boto3 not available. Install with: pip install boto3")

# Other embedding options
try:
    from huggingface_hub import InferenceClient
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    ST_AVAILABLE = True
except ImportError:
    ST_AVAILABLE = False

@dataclass
class SearchResult:
    """Data class for search results"""
    text: str
    score: float
    metadata: Dict[str, Any]
    doc_id: str

class BedrockRAGAdapter:
    """
    Enhanced RAG adapter with AWS Bedrock support for embeddings
    """
    
    def __init__(
        self,
        mongo_uri: str,
        db_name: str,
        collection_name: str,
        embedding_method: str = "bedrock",
        model_name: str = "amazon.titan-embed-text-v1",
        aws_region: str = "us-east-1",
        hf_token: Optional[str] = None,
        openai_api_key: Optional[str] = None
    ):
        # MongoDB setup
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        
        # Configuration
        self.embedding_method = embedding_method
        self.model_name = model_name
        self.aws_region = aws_region
        self.hf_token = hf_token
        self.openai_api_key = openai_api_key
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize embedding model
        self._initialize_embedding_model()
        
        # Create index for vector search
        self._ensure_embedding_index()
    
    def _initialize_embedding_model(self):
        """Initialize the embedding model based on the chosen method"""
        if self.embedding_method == "bedrock":
            if not BEDROCK_AVAILABLE:
                raise ImportError("boto3 not available. Install with: pip install boto3")
            
            try:
                self.bedrock_client = boto3.client(
                    service_name='bedrock-runtime',
                    region_name=self.aws_region
                )
                self.logger.info(f"Initialized AWS Bedrock client with model: {self.model_name}")
            except Exception as e:
                self.logger.error(f"Failed to initialize Bedrock client: {e}")
                raise
        
        elif self.embedding_method == "huggingface_hub":
            if not HF_AVAILABLE:
                raise ImportError("huggingface_hub not available. Install with: pip install huggingface_hub")
            self.hf_client = InferenceClient(model=self.model_name, token=self.hf_token)
            self.logger.info(f"Initialized Hugging Face client with model: {self.model_name}")
        
        elif self.embedding_method == "local":
            if not ST_AVAILABLE:
                raise ImportError("sentence_transformers not available. Install with: pip install sentence-transformers")
            self.local_model = SentenceTransformer(self.model_name)
            self.logger.info(f"Loaded local model: {self.model_name}")
        
        elif self.embedding_method == "openai":
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
                self.logger.info("Initialized OpenAI client")
            except ImportError:
                raise ImportError("openai not available. Install with: pip install openai")
    
    def _ensure_embedding_index(self):
        """Create index for embedding field to improve search performance"""
        try:
            indexes = self.collection.list_indexes()
            embedding_index_exists = any(
                'embedding' in idx.get('key', {}) for idx in indexes
            )
            
            if not embedding_index_exists:
                self.collection.create_index([("embedding", "2dsphere")])
                self.logger.info("Created embedding index")
        except Exception as e:
            self.logger.warning(f"Could not create embedding index: {e}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for given text using the configured method"""
        try:
            if self.embedding_method == "bedrock":
                return self._generate_bedrock_embedding(text)
            
            elif self.embedding_method == "huggingface_hub":
                embedding = self.hf_client.feature_extraction(text)
                if hasattr(embedding, 'tolist'):
                    return embedding.tolist()
                elif isinstance(embedding, list):
                    return embedding
                else:
                    return list(embedding)
            
            elif self.embedding_method == "local":
                embedding = self.local_model.encode([text])
                return embedding[0].tolist()
            
            elif self.embedding_method == "openai":
                response = self.openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=text
                )
                return response.data[0].embedding
            
        except Exception as e:
            self.logger.error(f"Error generating embedding: {e}")
            raise
    
    def _generate_bedrock_embedding(self, text: str) -> List[float]:
        """Generate embedding using AWS Bedrock"""
        try:
            if self.model_name == "amazon.titan-embed-text-v1":
                body = json.dumps({
                    "inputText": text
                })
                
                response = self.bedrock_client.invoke_model(
                    modelId=self.model_name,
                    body=body,
                    contentType='application/json',
                    accept='application/json'
                )
                
                response_body = json.loads(response['body'].read())
                return response_body['embedding']
            
            elif "cohere.embed" in self.model_name:
                body = json.dumps({
                    "texts": [text],
                    "input_type": "search_document"
                })
                
                response = self.bedrock_client.invoke_model(
                    modelId=self.model_name,
                    body=body,
                    contentType='application/json',
                    accept='application/json'
                )
                
                response_body = json.loads(response['body'].read())
                return response_body['embeddings'][0]
            
            else:
                raise ValueError(f"Unsupported Bedrock model: {self.model_name}")
                
        except ClientError as e:
            self.logger.error(f"Bedrock API error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error generating Bedrock embedding: {e}")
            raise
    
    def store_document(
        self, 
        text: str, 
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> str:
        """Store document with its embedding in MongoDB"""
        try:
            embedding = self.generate_embedding(text)
            
            doc = {
                "text": text,
                "embedding": embedding,
                "metadata": metadata or {},
                "model_name": self.model_name,
                "embedding_method": self.embedding_method,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            if doc_id:
                doc["_id"] = doc_id
            
            result = self.collection.insert_one(doc)
            return str(result.inserted_id)
                
        except Exception as e:
            self.logger.error(f"Error storing document: {e}")
            raise
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def similarity_search(
        self, 
        query: str, 
        limit: int = 5,
        min_score: float = 0.3,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Find similar documents using cosine similarity"""
        try:
            query_embedding = self.generate_embedding(query)
            
            # Build MongoDB filter
            mongo_filter = {}
            if filter_metadata:
                for key, value in filter_metadata.items():
                    mongo_filter[f"metadata.{key}"] = value
            
            # Get all documents (or filtered subset)
            documents = list(self.collection.find(mongo_filter))
            
            # Calculate similarities
            results = []
            for doc in documents:
                if 'embedding' in doc and doc['embedding']:
                    similarity = self.cosine_similarity(query_embedding, doc['embedding'])
                    
                    if similarity >= min_score:
                        results.append(SearchResult(
                            text=doc.get('text', ''),
                            score=similarity,
                            metadata=doc.get('metadata', {}),
                            doc_id=str(doc['_id'])
                        ))
            
            # Sort by similarity score (descending) and limit results
            results.sort(key=lambda x: x.score, reverse=True)
            return results[:limit]
            
        except Exception as e:
            self.logger.error(f"Error in similarity search: {e}")
            raise
    
    def generate_rag_response(
        self,
        query: str,
        context_limit: int = 3,
        min_score: float = 0.3
    ) -> Dict[str, Any]:
        """Generate a RAG response by finding relevant documents"""
        try:
            search_results = self.similarity_search(
                query=query,
                limit=context_limit,
                min_score=min_score
            )
            
            context_docs = []
            for result in search_results:
                context_docs.append({
                    "text": result.text,
                    "score": result.score,
                    "metadata": result.metadata
                })
            
            context_text = "\n\n".join([doc["text"] for doc in context_docs])
            
            return {
                "query": query,
                "context_documents": context_docs,
                "context_text": context_text,
                "num_results": len(search_results),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating RAG response: {e}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the document collection"""
        try:
            total_docs = self.collection.count_documents({})
            
            # Sample a few documents to check embedding dimensions
            sample_doc = self.collection.find_one({"embedding": {"$exists": True}})
            embedding_dim = len(sample_doc["embedding"]) if sample_doc and "embedding" in sample_doc else 0
            
            return {
                "total_documents": total_docs,
                "embedding_dimension": embedding_dim,
                "embedding_method": self.embedding_method,
                "model_name": self.model_name
            }
        except Exception as e:
            self.logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}