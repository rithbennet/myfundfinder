#!/usr/bin/env python3
"""
Database seeding script for funding data.
Processes metadata JSON files and relevant documents from the data folder.
"""

import json
import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any

from sqlalchemy.orm import Session
from app.db import get_db_session
from app.models.models import Agency, Funding, FundingChunk
from app.services.document_processor import DocumentProcessor
from app.services.s3_service import S3Service
from app.services.embeddings import EmbeddingService


class DatabaseSeeder:
    def __init__(self):
        self.data_dir = Path("data")
        self.doc_processor = DocumentProcessor()
        self.s3_service = S3Service()
        self.embedding_service = EmbeddingService()
        
    def get_funding_folders(self) -> List[Path]:
        """Get all funding folders from data directory."""
        return [f for f in self.data_dir.iterdir() if f.is_dir() and not f.name.startswith('.')]
    
    def load_metadata(self, folder_path: Path) -> Dict[str, Any]:
        """Load metadata JSON from folder."""
        metadata_dir = folder_path / "metadata"
        json_files = list(metadata_dir.glob("*.json"))
        
        if not json_files:
            raise FileNotFoundError(f"No metadata JSON found in {metadata_dir}")
        
        with open(json_files[0], 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_relevant_docs(self, folder_path: Path) -> List[Path]:
        """Get all relevant documents from folder."""
        docs_dir = folder_path / "relevant_docs"
        if not docs_dir.exists():
            return []
        
        return [f for f in docs_dir.iterdir() if f.is_file() and not f.name.startswith('.')]
    
    async def process_funding(self, folder_path: Path, db: Session) -> None:
        """Process a single funding folder."""
        print(f"Processing {folder_path.name}...")
        
        # Load metadata
        metadata = self.load_metadata(folder_path)
        
        # Create or get agency (using a default agency for now)
        agency = db.query(Agency).filter(Agency.name == "MDEC").first()
        if not agency:
            agency = Agency(
                name="MDEC",
                description="Malaysia Digital Economy Corporation",
                website="https://mdec.my"
            )
            db.add(agency)
            db.flush()
        
        # Create funding record
        funding = Funding(
            title=metadata["title"],
            description=metadata["description"],
            sector=metadata["sector"],
            deadline=metadata.get("deadline"),
            amount=metadata["amount"],
            eligibility=metadata["eligibility"],
            required_docs=metadata["requiredDocs"],
            agency_id=agency.id
        )
        db.add(funding)
        db.flush()
        
        # Process documents
        docs = self.get_relevant_docs(folder_path)
        s3_keys = []
        
        for doc_path in docs:
            print(f"  Processing document: {doc_path.name}")
            
            # Upload to S3
            s3_key = f"funding/{funding.id}/{doc_path.name}"
            await self.s3_service.upload_file(str(doc_path), s3_key)
            s3_keys.append(s3_key)
            
            # Extract text and create chunks
            if doc_path.suffix.lower() == '.pdf':
                text = await self.doc_processor.extract_text_from_pdf(str(doc_path))
                chunks = self.doc_processor.chunk_text(text)
                
                # Create embeddings and funding chunks
                for i, chunk in enumerate(chunks):
                    embedding = await self.embedding_service.create_embedding(chunk)
                    
                    funding_chunk = FundingChunk(
                        funding_id=funding.id,
                        chunk_text=chunk,
                        chunk_index=i,
                        s3_key=s3_key,
                        embedding=embedding
                    )
                    db.add(funding_chunk)
        
        # Update funding with S3 keys
        funding.s3_keys = s3_keys
        db.commit()
        print(f"  ✓ Completed {funding.title}")
    
    async def seed_database(self) -> None:
        """Main seeding function."""
        print("Starting database seeding...")
        
        db = next(get_db_session())
        try:
            funding_folders = self.get_funding_folders()
            print(f"Found {len(funding_folders)} funding programs to process")
            
            for folder in funding_folders:
                try:
                    await self.process_funding(folder, db)
                except Exception as e:
                    print(f"Error processing {folder.name}: {e}")
                    db.rollback()
                    continue
            
            print("✓ Database seeding completed successfully!")
            
        except Exception as e:
            print(f"Seeding failed: {e}")
            db.rollback()
            raise
        finally:
            db.close()


async def main():
    seeder = DatabaseSeeder()
    await seeder.seed_database()


if __name__ == "__main__":
    asyncio.run(main())
