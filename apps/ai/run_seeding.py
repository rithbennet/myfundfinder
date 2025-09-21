#!/usr/bin/env python3
"""
Main script to seed database with funding data.
"""

import asyncio
import sys
from seed_simple import seed_funding_metadata
from process_documents import process_funding_documents


async def main():
    """Run complete seeding process."""
    print("=== MyFundFinder Database Seeding ===\n")
    
    try:
        # Step 1: Seed metadata
        print("Step 1: Seeding funding metadata...")
        seed_funding_metadata()
        print()
        
        # Step 2: Process documents
        print("Step 2: Processing and vectorizing documents...")
        await process_funding_documents()
        print()
        
        print("🎉 Database seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
