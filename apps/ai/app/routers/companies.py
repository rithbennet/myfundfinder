from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..db import get_db
from ..models.models import User, Company, UserCompany
from ..schemas.schemas import Company as CompanySchema
from ..routers.auth import get_current_user

router = APIRouter(prefix="/companies", tags=["companies"])

@router.get("/", response_model=List[CompanySchema])
async def get_user_companies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get companies accessible to current user"""
    companies = db.query(Company).join(UserCompany).filter(
        UserCompany.user_id == current_user.id
    ).all()
    
    return companies
