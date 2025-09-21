#!/usr/bin/env python3
"""
Process documents and create embeddings for existing funding records.
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add app to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from db import SessionLocal
from models.models import Funding, FundingChunk
from services.document_processor import DocumentProcessor
from services.embeddings import EmbeddingService

async def main():
    data_dir = Path("data")
    db = SessionLocal()
    doc_processor = DocumentProcessor()
    embedding_service = EmbeddingService()
    
    try:
        fundings = db.query(Funding).all()
        print(f"Processing documents for {len(fundings)} funding programs...")
        
        for funding in fundings:
            print(f"\nProcessing: {funding.title}")
            
            # Check if already processed
            existing_chunks = db.query(FundingChunk).filter(FundingChunk.funding_id == funding.id).count()
            if existing_chunks > 0:
                print(f"  Already has {existing_chunks} chunks, skipping")
                continue
            
            # Find corresponding folder
            folder_name = None
            for folder in data_dir.iterdir():
                if folder.is_dir() and not folder.name.startswith('.'):
                    # Check if this folder contains this funding
                    metadata_dir = folder / "metadata"
                    if metadata_dir.exists():
                        json_files = list(metadata_dir.glob("*.json"))
                        if json_files:
                            import json
                            with open(json_files[0], 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            if data["title"] == funding.title:
                                folder_name = folder
                                break
            
            if not folder_name:
                print(f"  No data folder found, skipping")
                continue
            
            # Process documents
            docs_dir = folder_name / "relevant_docs"
            if not docs_dir.exists():
                print(f"  No documents folder found, skipping")
                continue
            
            doc_count = 0
            chunk_count = 0
            
            for doc_path in docs_dir.iterdir():
                if not doc_path.is_file() or doc_path.name.startswith('.'):
                    continue
                
                print(f"  Processing: {doc_path.name}")
                
                if doc_path.suffix.lower() == '.pdf':
                    try:
                        # Extract text
                        text = await doc_processor.extract_text_from_pdf(str(doc_path))
                        if not text.strip():
                            print(f"    No text extracted, skipping")
                            continue
                        
                        # Create chunks
                        chunks = doc_processor.chunk_text(text)
                        print(f"    Created {len(chunks)} chunks")
                        
                        # Create embeddings and save chunks
                        for i, chunk in enumerate(chunks):
                            embedding = await embedding_service.create_embedding(chunk)
                            
                            now = datetime.utcnow()
                            funding_chunk = FundingChunk(
                                funding_id=funding.id,
                                chunk_text=chunk,
                                chunk_index=i,
                                s3_key=f"local/{doc_path.name}",
                                embedding=embedding,
                                created_at=now,
                                updated_at=now
                            )
                            db.add(funding_chunk)
                            chunk_count += 1
                        
                        doc_count += 1
                        
                    except Exception as e:
                        print(f"    Error processing {doc_path.name}: {e}")
                        continue
            
            if chunk_count > 0:
                db.commit()
                print(f"  ✓ Processed {doc_count} documents, created {chunk_count} chunks")
            else:
                print(f"  No chunks created")
        
        print(f"\n🎉 Document processing completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
