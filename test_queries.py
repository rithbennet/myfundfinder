#!/usr/bin/env python3
"""
Test queries on processed documents
"""

from dynamodb_rag import DynamoDBRAG

def test_queries():
    rag = DynamoDBRAG("sme-rag-documents-1758382778")
    
    queries = [
        "What are the hiring criteria for software engineers?",
        "What technical skills are required?",
        "What is the remote work policy?",
        "What benefits does the company offer?",
        "What is the interview process?",
        "eligibility criteria"
    ]
    
    print("🔍 Testing queries on processed documents:")
    print("=" * 60)
    
    for query in queries:
        print(f"\n🔎 Query: '{query}'")
        results = rag.search_documents(query, limit=3)
        
        if results:
            for i, result in enumerate(results, 1):
                score_emoji = "🟢" if result['score'] > 0.5 else "🟡" if result['score'] > 0.3 else "🟠"
                print(f"  {i}. {score_emoji} Score: {result['score']:.3f} | {result['filename']}")
                print(f"     {result['text'][:150]}...")
        else:
            print("  ❌ No results found")

if __name__ == "__main__":
    test_queries()
