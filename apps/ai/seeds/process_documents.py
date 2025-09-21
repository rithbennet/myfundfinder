#!/usr/bin/env python3
"""
Process and vectorize funding documents.
"""

import asyncio
from pathlib import Path
from sqlalchemy.orm import Session
from app.db import get_db_session
from app.models.models import Funding, FundingChunk
from app.services.document_processor import DocumentProcessor
from app.services.embeddings import EmbeddingService


async def process_funding_documents():
    """Process documents for existing funding records."""
    data_dir = Path("data")
    db = next(get_db_session())
    doc_processor = DocumentProcessor()
    embedding_service = EmbeddingService()
    
    try:
        for folder in data_dir.iterdir():
            if not folder.is_dir() or folder.name.startswith('.'):
                continue
            
            print(f"Processing documents for {folder.name}...")
            
            # Find corresponding funding record
            metadata_dir = folder / "metadata"
            json_files = list(metadata_dir.glob("*.json"))
            if not json_files:
                continue
            
            import json
            with open(json_files[0], 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            funding = db.query(Funding).filter(Funding.title == metadata["title"]).first()
            if not funding:
                print(f"  No funding record found, skipping")
                continue
            
            # Check if already processed
            existing_chunks = db.query(FundingChunk).filter(FundingChunk.funding_id == funding.id).count()
            if existing_chunks > 0:
                print(f"  Already processed, skipping")
                continue
            
            # Process documents
            docs_dir = folder / "relevant_docs"
            if not docs_dir.exists():
                continue
            
            for doc_path in docs_dir.iterdir():
                if not doc_path.is_file() or doc_path.name.startswith('.'):
                    continue
                
                print(f"  Processing: {doc_path.name}")
                
                if doc_path.suffix.lower() == '.pdf':
                    # Extract text
                    text = await doc_processor.extract_text_from_pdf(str(doc_path))
                    chunks = doc_processor.chunk_text(text)
                    
                    # Create embeddings
                    for i, chunk in enumerate(chunks):
                        embedding = await embedding_service.create_embedding(chunk)
                        
                        funding_chunk = FundingChunk(
                            funding_id=funding.id,
                            chunk_text=chunk,
                            chunk_index=i,
                            s3_key=f"local/{doc_path.name}",
                            embedding=embedding
                        )
                        db.add(funding_chunk)
                    
                    print(f"    ✓ Created {len(chunks)} chunks")
            
            db.commit()
            print(f"  ✓ Completed {funding.title}")
        
        print("✓ Document processing completed!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(process_funding_documents())
