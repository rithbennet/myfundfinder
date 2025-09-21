#!/usr/bin/env python3
"""
Test script for enhanced RAG system with Bedrock embeddings
"""

import os
import sys
from dotenv import load_dotenv
from bedrock_rag_adapter import BedrockRAGAdapter

# Load environment variables
load_dotenv()

def test_bedrock_connection():
    """Test Bedrock connection and embedding generation"""
    print("🔍 Testing Bedrock connection...")
    
    try:
        rag_adapter = BedrockRAGAdapter(
            mongo_uri=os.getenv("MONGO_URI", "mongodb://localhost:27017/sme_rag_db"),
            db_name="sme_rag_db",
            collection_name="test_documents",
            embedding_method="bedrock",
            model_name="amazon.titan-embed-text-v1",
            aws_region="us-east-1"
        )
        
        # Test embedding generation
        test_text = "This is a test document about artificial intelligence and machine learning."
        embedding = rag_adapter.generate_embedding(test_text)
        
        print(f"✅ Bedrock connection successful!")
        print(f"📊 Embedding dimension: {len(embedding)}")
        print(f"🔢 Sample embedding values: {embedding[:5]}...")
        
        return rag_adapter
        
    except Exception as e:
        print(f"❌ Bedrock connection failed: {e}")
        return None

def upload_sample_documents(rag_adapter):
    """Upload sample documents for testing"""
    print("\n📄 Uploading sample documents...")
    
    sample_docs = [
        {
            "text": """
            Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines 
            that can perform tasks that typically require human intelligence. These tasks include learning, 
            reasoning, problem-solving, perception, and language understanding. AI systems can be categorized 
            into narrow AI, which is designed for specific tasks, and general AI, which would have human-like 
            cognitive abilities across various domains.
            """,
            "metadata": {
                "source_file": "ai_basics.txt",
                "topic": "artificial_intelligence",
                "category": "technology"
            }
        },
        {
            "text": """
            Machine Learning (ML) is a subset of artificial intelligence that enables computers to learn and 
            improve from experience without being explicitly programmed. ML algorithms build mathematical 
            models based on training data to make predictions or decisions. Common types include supervised 
            learning, unsupervised learning, and reinforcement learning. Applications range from image 
            recognition to natural language processing.
            """,
            "metadata": {
                "source_file": "ml_overview.txt",
                "topic": "machine_learning",
                "category": "technology"
            }
        },
        {
            "text": """
            Natural Language Processing (NLP) is a field of AI that focuses on the interaction between 
            computers and human language. It involves developing algorithms and models that can understand, 
            interpret, and generate human language in a valuable way. NLP applications include chatbots, 
            language translation, sentiment analysis, and text summarization. Modern NLP relies heavily 
            on deep learning and transformer architectures.
            """,
            "metadata": {
                "source_file": "nlp_guide.txt",
                "topic": "natural_language_processing",
                "category": "technology"
            }
        },
        {
            "text": """
            Cloud computing is the delivery of computing services including servers, storage, databases, 
            networking, software, analytics, and intelligence over the Internet. It offers faster innovation, 
            flexible resources, and economies of scale. Major cloud service models include Infrastructure 
            as a Service (IaaS), Platform as a Service (PaaS), and Software as a Service (SaaS). 
            Leading providers include Amazon Web Services, Microsoft Azure, and Google Cloud Platform.
            """,
            "metadata": {
                "source_file": "cloud_computing.txt",
                "topic": "cloud_computing",
                "category": "technology"
            }
        },
        {
            "text": """
            Data Science is an interdisciplinary field that uses scientific methods, processes, algorithms, 
            and systems to extract knowledge and insights from structured and unstructured data. It combines 
            statistics, mathematics, programming, and domain expertise to analyze complex data sets. 
            Data scientists use tools like Python, R, SQL, and various machine learning libraries to 
            uncover patterns and make data-driven decisions.
            """,
            "metadata": {
                "source_file": "data_science.txt",
                "topic": "data_science",
                "category": "technology"
            }
        }
    ]
    
    document_ids = []
    for i, doc in enumerate(sample_docs):
        try:
            doc_id = rag_adapter.store_document(
                text=doc["text"].strip(),
                metadata=doc["metadata"]
            )
            document_ids.append(doc_id)
            print(f"✅ Uploaded document {i+1}: {doc['metadata']['source_file']}")
        except Exception as e:
            print(f"❌ Failed to upload document {i+1}: {e}")
    
    print(f"\n📊 Successfully uploaded {len(document_ids)} documents")
    return document_ids

def test_search_functionality(rag_adapter):
    """Test the enhanced search functionality"""
    print("\n🔍 Testing search functionality...")
    
    test_queries = [
        "What is artificial intelligence?",
        "machine learning algorithms",
        "cloud computing services",
        "NLP applications",
        "data science tools"
    ]
    
    for query in test_queries:
        print(f"\n🔎 Query: '{query}'")
        try:
            results = rag_adapter.similarity_search(
                query=query,
                limit=3,
                min_score=0.2
            )
            
            print(f"📊 Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. Score: {result.score:.3f} | Source: {result.metadata.get('source_file', 'Unknown')}")
                print(f"     Text preview: {result.text[:100]}...")
                
        except Exception as e:
            print(f"❌ Search failed: {e}")

def test_rag_response(rag_adapter):
    """Test RAG response generation"""
    print("\n🤖 Testing RAG response generation...")
    
    test_query = "How does machine learning work and what are its applications?"
    
    try:
        rag_response = rag_adapter.generate_rag_response(
            query=test_query,
            context_limit=3,
            min_score=0.2
        )
        
        print(f"🔎 Query: {test_query}")
        print(f"📊 Found {rag_response['num_results']} relevant documents")
        print(f"📄 Context length: {len(rag_response['context_text'])} characters")
        print(f"\n📝 Context preview:")
        print(rag_response['context_text'][:500] + "..." if len(rag_response['context_text']) > 500 else rag_response['context_text'])
        
    except Exception as e:
        print(f"❌ RAG response generation failed: {e}")

def main():
    """Main test function"""
    print("🚀 Enhanced RAG System Test with Bedrock Embeddings")
    print("=" * 60)
    
    # Test Bedrock connection
    rag_adapter = test_bedrock_connection()
    if not rag_adapter:
        print("❌ Cannot proceed without Bedrock connection")
        sys.exit(1)
    
    # Upload sample documents
    document_ids = upload_sample_documents(rag_adapter)
    
    # Test search functionality
    test_search_functionality(rag_adapter)
    
    # Test RAG response generation
    test_rag_response(rag_adapter)
    
    # Get collection stats
    print("\n📊 Collection Statistics:")
    stats = rag_adapter.get_collection_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n✅ All tests completed!")
    print("🌐 You can now start the chatbot with: python chatbot_app.py")

if __name__ == "__main__":
    main()
