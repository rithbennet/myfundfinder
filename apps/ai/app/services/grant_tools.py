from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from ..models.models import Funding, FundingChunk
from datetime import datetime

class GrantTools:
    def __init__(self, db: Session):
        self.db = db
    
    def search_grants(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for grants based on query keywords.
        LLM can call this tool to find relevant grants.
        """
        query_lower = query.lower()
        
        # Build search conditions
        conditions = []
        
        # Search in title and description
        conditions.extend([
            Funding.title.ilike(f"%{query}%"),
            Funding.description.ilike(f"%{query}%"),
            Funding.sector.ilike(f"%{query}%")
        ])
        
        # Add specific keyword searches
        keywords = query_lower.split()
        for keyword in keywords:
            if len(keyword) > 2:  # Skip short words
                conditions.extend([
                    Funding.title.ilike(f"%{keyword}%"),
                    Funding.description.ilike(f"%{keyword}%")
                ])
        
        # Execute search
        grants = self.db.query(Funding).filter(
            and_(
                or_(
                    Funding.deadline.is_(None),
                    Funding.deadline > datetime.now()
                ),
                or_(*conditions)
            )
        ).limit(limit).all()
        
        # Return structured data for LLM
        results = []
        for grant in grants:
            results.append({
                "id": grant.id,
                "title": grant.title,
                "description": grant.description,
                "sector": grant.sector,
                "amount": grant.amount,
                "eligibility": grant.eligibility,
                "required_docs": grant.required_docs
            })
        
        return results
    
    def get_grant_details_with_chunks(self, grant_id: int) -> Dict[str, Any]:
        """
        Get detailed grant information including RAG chunks from PDFs.
        This provides the actual document content, not just metadata.
        """
        grant = self.db.query(Funding).filter(Funding.id == grant_id).first()
        
        if not grant:
            return {"error": "Grant not found"}
        
        # Get all chunks for this grant (RAG content)
        chunks = self.db.query(FundingChunk).filter(
            FundingChunk.funding_id == grant_id
        ).all()
        
        result = {
            "id": grant.id,
            "title": grant.title,
            "description": grant.description,
            "sector": grant.sector,
            "amount": grant.amount,
            "eligibility": grant.eligibility,
            "required_docs": grant.required_docs,
            "deadline": grant.deadline.isoformat() if grant.deadline else None,
            "detailed_content": [
                {
                    "text": chunk.chunk_text,
                    "page": chunk.page_no
                }
                for chunk in chunks
            ],
            "total_chunks": len(chunks)
        }
        
        return result
    
    def search_grants_with_chunks(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Search grants and include RAG chunks for detailed content.
        Returns fewer grants but with full PDF content.
        """
        query_lower = query.lower()
        
        # Build search conditions
        conditions = []
        conditions.extend([
            Funding.title.ilike(f"%{query}%"),
            Funding.description.ilike(f"%{query}%"),
            Funding.sector.ilike(f"%{query}%")
        ])
        
        # Add specific keyword searches
        keywords = query_lower.split()
        for keyword in keywords:
            if len(keyword) > 2:
                conditions.extend([
                    Funding.title.ilike(f"%{keyword}%"),
                    Funding.description.ilike(f"%{keyword}%")
                ])
        
        # Execute search
        grants = self.db.query(Funding).filter(
            and_(
                or_(
                    Funding.deadline.is_(None),
                    Funding.deadline > datetime.now()
                ),
                or_(*conditions)
            )
        ).limit(limit).all()
        
        # Get detailed info with chunks for each grant
        results = []
        for grant in grants:
            grant_details = self.get_grant_details_with_chunks(grant.id)
            results.append(grant_details)
        
        return results
    
    def get_grant_by_name(self, grant_name: str) -> Dict[str, Any]:
        """
        Get specific grant by name/keyword with full RAG content.
        Useful when user asks about specific grants like "ADF", "DCG Prime", etc.
        """
        name_lower = grant_name.lower()
        
        # Map common names to search terms
        search_terms = {
            "adf": "SME Automation and Digitalisation Facility",
            "sme automation": "SME Automation and Digitalisation Facility",
            "dcg prime": "Digital Content Grant (DCG) – Prime Grant",
            "prime grant": "Digital Content Grant (DCG) – Prime Grant",
            "dcg mini": "Digital Content Grant (DCG) – Mini Grant",
            "mini grant": "Digital Content Grant (DCG) – Mini Grant",
            "dcg marketing": "Digital Content Grant (DCG) – Marketing",
            "marketing grant": "Digital Content Grant (DCG) – Marketing",
            "x-port": "Malaysia Digital X-Port Grant",
            "mdxg": "Malaysia Digital X-Port Grant"
        }
        
        # Get search term
        search_term = search_terms.get(name_lower, grant_name)
        
        # Find the grant
        grant = self.db.query(Funding).filter(
            Funding.title.ilike(f"%{search_term}%")
        ).first()
        
        if not grant:
            return {"error": f"Grant '{grant_name}' not found"}
        
        # Return with full RAG content
        return self.get_grant_details_with_chunks(grant.id)
    
    def search_by_amount(self, min_amount: float = None, max_amount: float = None) -> List[Dict[str, Any]]:
        """
        Search grants by funding amount range.
        LLM can use this for budget-specific queries.
        """
        query = self.db.query(Funding)
        
        if min_amount:
            query = query.filter(Funding.amount >= min_amount)
        if max_amount:
            query = query.filter(Funding.amount <= max_amount)
        
        grants = query.filter(
            or_(
                Funding.deadline.is_(None),
                Funding.deadline > datetime.now()
            )
        ).all()
        
        return [
            {
                "id": grant.id,
                "title": grant.title,
                "amount": grant.amount,
                "sector": grant.sector,
                "description": grant.description
            }
            for grant in grants
        ]
    
    def get_all_available_grants(self) -> List[Dict[str, Any]]:
        """
        Get overview of all available grants.
        LLM can use this for general "what grants are available" queries.
        """
        grants = self.db.query(Funding).filter(
            or_(
                Funding.deadline.is_(None),
                Funding.deadline > datetime.now()
            )
        ).all()
        
        return [
            {
                "id": grant.id,
                "title": grant.title,
                "sector": grant.sector,
                "amount": grant.amount,
                "description": grant.description[:200] + "..." if len(grant.description) > 200 else grant.description
            }
            for grant in grants
        ]
