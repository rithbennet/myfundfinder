from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: str
    name: str

class User(UserBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class CompanyBase(BaseModel):
    company_name: str
    company_id: Optional[str] = None
    sector: Optional[str] = None
    location: Optional[str] = None
    revenue: Optional[float] = None
    employees: Optional[int] = None

class Company(CompanyBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: List[str] = []

class FundingUploadRequest(BaseModel):
    title: str
    description: Optional[str] = None
    sector: Optional[str] = None
    deadline: Optional[datetime] = None
    amount: Optional[float] = None
    eligibility: Optional[str] = None
    required_docs: Optional[str] = None
    agency_id: Optional[int] = None

class FundingUploadResponse(BaseModel):
    funding_id: int
    status: str
    chunks_created: int

class ChatSession(BaseModel):
    id: str
    user_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatMessage(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True
