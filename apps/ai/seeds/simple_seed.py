#!/usr/bin/env python3
"""
Minimal seeding script for funding data.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add app to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from db import SessionLocal
from models.models import Agency, Funding

def main():
    data_dir = Path("data")
    db = SessionLocal()
    
    try:
        # Create MDEC agency
        agency = db.query(Agency).filter(Agency.name == "MDEC").first()
        if not agency:
            now = datetime.utcnow()
            agency = Agency(
                name="MDEC", 
                description="Malaysia Digital Economy Corporation",
                created_at=now,
                updated_at=now
            )
            db.add(agency)
            db.flush()
            print("✓ Created MDEC agency")
        
        count = 0
        for folder in data_dir.iterdir():
            if not folder.is_dir() or folder.name.startswith('.'):
                continue
                
            # Find JSON file in metadata folder
            metadata_dir = folder / "metadata"
            if not metadata_dir.exists():
                continue
                
            json_files = list(metadata_dir.glob("*.json"))
            if not json_files:
                continue
                
            with open(json_files[0], 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if exists
            if db.query(Funding).filter(Funding.title == data["title"]).first():
                print(f"  {data['title']} - already exists")
                continue
            
            # Create funding
            now = datetime.utcnow()
            funding = Funding(
                title=data["title"],
                description=data["description"],
                sector=data["sector"],
                amount=data["amount"],
                eligibility=data["eligibility"],
                required_docs=data["requiredDocs"],
                agency_id=agency.id,
                created_at=now,
                updated_at=now
            )
            db.add(funding)
            count += 1
            print(f"✓ {data['title']}")
        
        db.commit()
        print(f"\n🎉 Added {count} funding programs!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
