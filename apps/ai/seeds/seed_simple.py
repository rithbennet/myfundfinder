#!/usr/bin/env python3
"""
Simple database seeding script for funding data.
"""

import json
import os
from pathlib import Path
from sqlalchemy.orm import Session
from app.db import get_db_session
from app.models.models import Agency, Funding


def seed_funding_metadata():
    """Seed funding metadata from JSON files."""
    data_dir = Path("data")
    db = next(get_db_session())
    
    try:
        # Create default agency
        agency = db.query(Agency).filter(Agency.name == "MDEC").first()
        if not agency:
            agency = Agency(
                name="MDEC",
                description="Malaysia Digital Economy Corporation",
                website="https://mdec.my"
            )
            db.add(agency)
            db.flush()
        
        # Process each funding folder
        for folder in data_dir.iterdir():
            if not folder.is_dir() or folder.name.startswith('.'):
                continue
                
            print(f"Processing {folder.name}...")
            
            # Find metadata JSON
            metadata_dir = folder / "metadata"
            json_files = list(metadata_dir.glob("*.json"))
            
            if not json_files:
                print(f"  No metadata found, skipping")
                continue
            
            # Load metadata
            with open(json_files[0], 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Check if funding already exists
            existing = db.query(Funding).filter(Funding.title == metadata["title"]).first()
            if existing:
                print(f"  Funding already exists, skipping")
                continue
            
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
            print(f"  ✓ Added: {funding.title}")
        
        db.commit()
        print("✓ Metadata seeding completed!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_funding_metadata()
