#!/usr/bin/env python3
"""
Test Bedrock embedding service.
"""

import sys
import asyncio
from pathlib import Path

# Add app to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from services.embeddings import EmbeddingService

async def main():
    try:
        embedding_service = EmbeddingService()
        print("Testing embedding service...")
        
        test_text = "This is a test for grant funding in Malaysia"
        embedding = await embedding_service.generate_embedding(test_text)
        
        print(f"✓ Embedding generated successfully!")
        print(f"  Text: {test_text}")
        print(f"  Embedding length: {len(embedding)}")
        print(f"  First 5 values: {embedding[:5]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
