from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from ..models.models import Funding, Company
import json

class GrantFilterService:
    def __init__(self, db: Session):
        self.db = db
    
    def extract_keywords_from_query(self, query: str) -> Dict[str, List[str]]:
        """Extract and categorize keywords from user query"""
        query_lower = query.lower()
        
        keywords = {
            "grant_types": [],
            "sectors": [],
            "purposes": [],
            "amounts": [],
            "specific_grants": []
        }
        
        # Specific grant names
        if any(word in query_lower for word in ['sme automation', 'adf', 'automation facility']):
            keywords["specific_grants"].append("SME Automation and Digitalisation Facility")
        
        if any(word in query_lower for word in ['digital content', 'dcg']):
            keywords["specific_grants"].append("Digital Content Grant")
            
        if any(word in query_lower for word in ['prime grant', 'dcg prime', 'prime']):
            keywords["specific_grants"].append("Digital Content Grant (DCG) – Prime Grant")
            
        if any(word in query_lower for word in ['mini grant', 'dcg mini', 'mini']):
            keywords["specific_grants"].append("Digital Content Grant (DCG) – Mini Grant")
            
        if any(word in query_lower for word in ['marketing grant', 'dcg marketing', 'commercialisation']):
            keywords["specific_grants"].append("Digital Content Grant (DCG) – Marketing & Commercialisation Grant")
        
        if any(word in query_lower for word in ['x-port', 'xport', 'mdxg']):
            keywords["specific_grants"].append("Malaysia Digital X-Port Grant")
        
        # Sectors
        if any(word in query_lower for word in ['green', 'environment', 'sustainability', 'renewable', 'clean']):
            keywords["sectors"].extend(["green", "environment", "sustainability"])
        
        if any(word in query_lower for word in ['technology', 'digital', 'tech', 'automation']):
            keywords["sectors"].extend(["technology", "digital", "automation"])
        
        if any(word in query_lower for word in ['manufacturing', 'production', 'factory']):
            keywords["sectors"].append("manufacturing")
        
        # Purposes
        if any(word in query_lower for word in ['export', 'international', 'global', 'overseas']):
            keywords["purposes"].append("export")
        
        if any(word in query_lower for word in ['marketing', 'commercialisation', 'promotion']):
            keywords["purposes"].append("marketing")
        
        # Remove duplicates
        for key in keywords:
            keywords[key] = list(set(keywords[key]))
        
        print(f"🔍 Extracted keywords: {keywords}")
        return keywords
    
    def filter_grants_by_keywords(self, keywords: Dict[str, List[str]]) -> List[int]:
        """Filter grants based on extracted keywords"""
        base_query = self.db.query(Funding).filter(
            or_(
                Funding.deadline.is_(None),
                Funding.deadline > datetime.now()
            )
        )
        
        conditions = []
        
        # Specific grant name matching (highest priority)
        for grant_name in keywords.get("specific_grants", []):
            if "SME Automation" in grant_name:
                conditions.append(Funding.title.ilike('%SME Automation%'))
            elif "Digital Content" in grant_name:
                conditions.append(Funding.title.ilike('%Digital Content%'))
            elif "X-Port" in grant_name:
                conditions.append(Funding.title.ilike('%X-Port%'))
        
        # Sector matching
        for sector in keywords.get("sectors", []):
            if sector in ["green", "environment", "sustainability"]:
                conditions.extend([
                    Funding.title.ilike('%Green%'),
                    Funding.description.ilike('%green%'),
                    Funding.description.ilike('%environment%')
                ])
            elif sector in ["technology", "digital", "automation"]:
                conditions.extend([
                    Funding.title.ilike('%Digital%'),
                    Funding.title.ilike('%Technology%'),
                    Funding.title.ilike('%Automation%')
                ])
            elif sector == "manufacturing":
                conditions.extend([
                    Funding.sector.ilike('%Manufacturing%'),
                    Funding.title.ilike('%Manufacturing%')
                ])
        
        # Purpose matching
        for purpose in keywords.get("purposes", []):
            if purpose == "export":
                conditions.extend([
                    Funding.title.ilike('%Export%'),
                    Funding.title.ilike('%X-Port%'),
                    Funding.description.ilike('%export%')
                ])
            elif purpose == "marketing":
                conditions.extend([
                    Funding.title.ilike('%Marketing%'),
                    Funding.description.ilike('%marketing%')
                ])
        
        if conditions:
            grants = base_query.filter(or_(*conditions)).all()
        else:
            grants = base_query.all()
        
        print(f"🎯 Found {len(grants)} grants matching keywords")
        for grant in grants[:3]:
            print(f"   - {grant.title}")
        
        return [grant.id for grant in grants]
    
    def filter_grants_by_query(self, query: str) -> List[int]:
        """Main filtering function - extract keywords then filter"""
        # Step 1: Extract keywords from query
        keywords = self.extract_keywords_from_query(query)
        
        # Step 2: Filter grants based on keywords
        grant_ids = self.filter_grants_by_keywords(keywords)
        
        return grant_ids
    
    def filter_grants(self, company: Company) -> List[int]:
        """Filter grants based on company profile - DEPRECATED"""
        return self.filter_grants_by_query("")
