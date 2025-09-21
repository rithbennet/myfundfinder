#!/usr/bin/env python3
"""
Test the simple RAG system
"""

from simple_bedrock_rag import SimpleBedrockRAG

def test_simple_rag():
    print("🚀 Testing Simple Bedrock RAG (No MongoDB)")
    
    # Initialize
    rag = SimpleBedrockRAG("sme-rag-documents-1758382778")
    
    # Test document
    test_doc = """
    Hiring criteria for software engineers typically include:
    
    1. Technical Skills: Proficiency in programming languages like Python, Java, JavaScript
    2. Problem-solving abilities and algorithmic thinking
    3. Experience with databases, APIs, and cloud platforms
    4. Understanding of software development lifecycle
    5. Communication skills and teamwork
    6. Bachelor's degree in Computer Science or related field (preferred)
    7. 2-5 years of relevant experience for mid-level positions
    
    The interview process usually involves coding challenges, system design questions, 
    and behavioral interviews to assess both technical competency and cultural fit.
    """
    
    print("📄 Storing test document...")
    doc_key = rag.store_document_with_embedding(test_doc, "hiring_criteria.txt")
    print(f"✅ Stored: {doc_key}")
    
    # Test search
    print("\n🔍 Testing search...")
    queries = [
        "hiring criteria",
        "software engineer requirements", 
        "technical skills needed",
        "interview process"
    ]
    
    for query in queries:
        print(f"\n🔎 Query: '{query}'")
        results = rag.search_documents(query, limit=3)
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. Score: {result['score']:.3f}")
            print(f"     Preview: {result['text'][:100]}...")

if __name__ == "__main__":
    test_simple_rag()
