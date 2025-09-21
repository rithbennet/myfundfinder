#!/usr/bin/env python3
"""
Simple clean and reseed script without embeddings
"""

import os
import json
from sqlalchemy import create_engine, text
from app.db import get_db
from app.models.models import Funding, FundingChunk
from app.services.document_processor import DocumentProcessor
from datetime import datetime

def clean_all_data():
    """Remove all funding and funding_chunks data"""
    print("🧹 Cleaning existing data...")
    
    db = next(get_db())
    
    try:
        deleted_chunks = db.query(FundingChunk).delete()
        print(f"   Deleted {deleted_chunks} funding chunks")
        
        deleted_fundings = db.query(Funding).delete()
        print(f"   Deleted {deleted_fundings} fundings")
        
        db.execute(text("ALTER SEQUENCE fundings_id_seq RESTART WITH 1"))
        db.execute(text("ALTER SEQUENCE funding_chunks_id_seq RESTART WITH 1"))
        
        db.commit()
        print("✅ Data cleaned successfully")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error cleaning data: {e}")
        raise
    finally:
        db.close()

def reseed_from_data_folders():
    """Reseed funding data from data folders"""
    print("🌱 Processing data folders...")
    
    db = next(get_db())
    
    try:
        processor = DocumentProcessor()
        data_dir = "data"
        
        folders = [f for f in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, f)) and not f.startswith('.')]
        print(f"📁 Found {len(folders)} data folders: {folders}")
        
        for folder_name in folders:
            folder_path = os.path.join(data_dir, folder_name)
            metadata_dir = os.path.join(folder_path, "metadata")
            pdf_dir = os.path.join(folder_path, "relevant_docs")
            
            print(f"\n📖 Processing folder: {folder_name}")
            
            # Read metadata
            metadata_file = None
            if os.path.exists(metadata_dir):
                json_files = [f for f in os.listdir(metadata_dir) if f.endswith('.json')]
                if json_files:
                    metadata_file = os.path.join(metadata_dir, json_files[0])
            
            if not metadata_file:
                print(f"   ⚠️ No metadata JSON found")
                continue
            
            with open(metadata_file, 'r') as f:
                grant_info = json.load(f)
            
            print(f"   📄 Loaded: {grant_info['title']}")
            
            # Find PDF
            pdf_file = None
            if os.path.exists(pdf_dir):
                pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
                if pdf_files:
                    pdf_file = os.path.join(pdf_dir, pdf_files[0])
            
            if not pdf_file:
                print(f"   ⚠️ No PDF found")
                continue
            
            try:
                # Create funding
                funding = Funding(
                    title=grant_info['title'],
                    description=grant_info['description'],
                    sector=grant_info['sector'],
                    amount=grant_info['amount'],
                    eligibility=grant_info['eligibility'],
                    required_docs=grant_info['requiredDocs'],
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.add(funding)
                db.commit()
                db.refresh(funding)
                
                print(f"   ✅ Created funding ID: {funding.id}")
                
                # Process PDF
                with open(pdf_file, 'rb') as f:
                    pdf_content = f.read()
                
                text = processor.extract_text_from_pdf(pdf_content)
                chunks = processor.chunk_text(text)
                
                # Create chunks (without embeddings for now)
                chunk_count = 0
                for i, chunk_text in enumerate(chunks):
                    if len(chunk_text.strip()) > 50:
                        chunk = FundingChunk(
                            funding_id=funding.id,
                            chunk_text=chunk_text,
                            page_no=i+1,
                            created_at=datetime.now(),
                            updated_at=datetime.now()
                        )
                        db.add(chunk)
                        chunk_count += 1
                
                db.commit()
                print(f"   📝 Created {chunk_count} chunks")
                
            except Exception as e:
                db.rollback()
                print(f"   ❌ Error: {e}")
                continue
        
    except Exception as e:
        print(f"❌ Error processing: {e}")
        raise
    finally:
        db.close()

def main():
    print("🚀 Starting simple reseed...")
    clean_all_data()
    reseed_from_data_folders()
    
    # Summary
    db = next(get_db())
    try:
        total_fundings = db.query(Funding).count()
        total_chunks = db.query(FundingChunk).count()
        
        print(f"\n📊 Summary:")
        print(f"   Total fundings: {total_fundings}")
        print(f"   Total chunks: {total_chunks}")
        
        fundings = db.query(Funding).all()
        print(f"\n📋 Created fundings:")
        for funding in fundings:
            print(f"   {funding.id}. {funding.title}")
    finally:
        db.close()
    
    print("✅ Reseed completed!")

if __name__ == "__main__":
    main()
