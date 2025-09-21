from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from ..models.models import Funding, Company

class GrantFilterService:
    def __init__(self, db: Session):
        self.db = db
    
    def filter_grants(self, company: Company) -> List[int]:
        """Filter grants based on company profile and eligibility"""
        
        # Base query for active grants
        query = self.db.query(Funding).filter(
            or_(
                Funding.deadline.is_(None),
                Funding.deadline > datetime.now()
            )
        )
        
        # Filter by sector if specified
        if company.sector:
            sector_lower = company.sector.lower()
            
            # More specific sector matching
            query = query.filter(
                or_(
                    Funding.sector.is_(None),  # General grants
                    Funding.sector.ilike(f"%{company.sector}%"),  # Exact sector match
                    # Add common sector variations
                    and_(
                        sector_lower == "technology",
                        or_(
                            Funding.sector.ilike("%tech%"),
                            Funding.sector.ilike("%digital%"),
                            Funding.sector.ilike("%IT%"),
                            Funding.sector.ilike("%software%")
                        )
                    ),
                    and_(
                        sector_lower in ["manufacturing", "industrial"],
                        or_(
                            Funding.sector.ilike("%manufacturing%"),
                            Funding.sector.ilike("%industrial%"),
                            Funding.sector.ilike("%production%")
                        )
                    )
                )
            )
        
        # Filter by company size (employees)
        if company.employees:
            # SME definition: typically < 200 employees
            if company.employees < 5:
                size_category = "micro"
            elif company.employees < 30:
                size_category = "small"
            elif company.employees < 200:
                size_category = "medium"
            else:
                size_category = "large"
            
            # Filter grants that don't exclude this company size
            # This would need additional fields in the Funding model
        
        grants = query.all()
        
        print(f"🔍 Grant filtering for {company.company_name}:")
        print(f"   Sector: {company.sector}")
        print(f"   Employees: {company.employees}")
        print(f"   Found {len(grants)} eligible grants")
        
        if grants:
            print(f"   Sample grants: {[g.title[:50] + '...' for g in grants[:3]]}")
        
        return [grant.id for grant in grants]
