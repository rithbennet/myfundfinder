#!/usr/bin/env python3
"""
Process documents and create embeddings for existing funding records.
"""

import sys
import asyncio
import PyPDF2
import io
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
        """Extract text from PDF file path"""
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
        """Split text into chunks"""
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

async def main():
    data_dir = Path("data")
    db = SessionLocal()
    doc_processor = SimpleDocProcessor()
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
                        
                        # Create embeddings and save chunks
                        for i, chunk in enumerate(chunks):
                            embedding = await embedding_service.generate_embedding(chunk)
                            
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
                        
                    except Exception as e:
                        print(f"    Error processing {doc_path.name}: {e}")
                        continue
            
            if chunk_count > 0:
                db.commit()
                print(f"  ✓ Created {chunk_count} chunks")
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
