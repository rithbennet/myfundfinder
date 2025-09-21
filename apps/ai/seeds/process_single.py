#!/usr/bin/env python3
"""
Process documents for a single funding program.
Usage: python3 process_single.py "Digital Content Grant (DCG) – Prime Grant"
"""

import sys
import asyncio
import PyPDF2
from pathlib import Path
from datetime import datetime
from typing import List

# Add app to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from db import SessionLocal
from models.models import Funding, FundingChunk
from services.embeddings import EmbeddingService

class SimpleDocProcessor:
    def __init__(self):
        self.chunk_size = 500
    
    def extract_text_from_pdf_file(self, file_path: str) -> str:
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def chunk_text(self, text: str) -> List[str]:
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            estimated_tokens = len((current_chunk + sentence).split()) * 1.3
            
            if estimated_tokens > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += sentence + ". "
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks

async def process_funding(funding_title: str):
    """Process documents for a specific funding program."""
    data_dir = Path("data")
    db = SessionLocal()
    doc_processor = SimpleDocProcessor()
    embedding_service = EmbeddingService()
    
    try:
        # Find funding record
        funding = db.query(Funding).filter(Funding.title == funding_title).first()
        if not funding:
            print(f"❌ Funding '{funding_title}' not found in database")
            return
        
        print(f"Processing: {funding.title}")
        
        # Check if already processed
        existing_chunks = db.query(FundingChunk).filter(FundingChunk.funding_id == funding.id).count()
        if existing_chunks > 0:
            print(f"  Already has {existing_chunks} chunks, skipping")
            return
        
        # Find corresponding folder
        folder_name = None
        for folder in data_dir.iterdir():
            if folder.is_dir() and not folder.name.startswith('.'):
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
            print(f"  No data folder found")
            return
        
        # Process documents
        docs_dir = folder_name / "relevant_docs"
        if not docs_dir.exists():
            print(f"  No documents folder found")
            return
        
        chunk_count = 0
        
        for doc_path in docs_dir.iterdir():
            if not doc_path.is_file() or doc_path.name.startswith('.'):
                continue
            
            print(f"  Processing: {doc_path.name}")
            
            if doc_path.suffix.lower() == '.pdf':
                try:
                    # Extract text
                    text = doc_processor.extract_text_from_pdf_file(str(doc_path))
                    if not text.strip():
                        print(f"    No text extracted, skipping")
                        continue
                    
                    # Create chunks
                    chunks = doc_processor.chunk_text(text)
                    print(f"    Created {len(chunks)} chunks")
                    
                    # Process chunks
                    for i, chunk in enumerate(chunks):
                        try:
                            embedding = await embedding_service.generate_embedding(chunk)
                            
                            now = datetime.utcnow()
                            funding_chunk = FundingChunk(
                                funding_id=funding.id,
                                chunk_text=chunk,
                                page_no=i,  # Use page_no instead of chunk_index
                                embedding=embedding,
                                created_at=now,
                                updated_at=now
                            )
                            db.add(funding_chunk)
                            chunk_count += 1
                            
                            if chunk_count % 5 == 0:
                                db.commit()
                                print(f"    Saved {chunk_count} chunks...")
                                
                        except Exception as e:
                            print(f"    Error processing chunk {i}: {e}")
                            continue
                    
                except Exception as e:
                    print(f"    Error processing {doc_path.name}: {e}")
                    continue
        
        if chunk_count > 0:
            db.commit()
            print(f"  ✓ Created {chunk_count} chunks total")
        else:
            print(f"  No chunks created")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

async def main():
    if len(sys.argv) != 2:
        print("Usage: python3 process_single.py \"Funding Title\"")
        print("\nAvailable funding programs:")
        
        db = SessionLocal()
        try:
            fundings = db.query(Funding).all()
            for funding in fundings:
                existing_chunks = db.query(FundingChunk).filter(FundingChunk.funding_id == funding.id).count()
                status = f"({existing_chunks} chunks)" if existing_chunks > 0 else "(not processed)"
                print(f"  - {funding.title} {status}")
        finally:
            db.close()
        return
    
    funding_title = sys.argv[1]
    await process_funding(funding_title)

if __name__ == "__main__":
    asyncio.run(main())
