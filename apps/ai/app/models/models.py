from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from .base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    onboarded = Column(Boolean, default=False)
    createdAt = Column(DateTime, nullable=False)
    updatedAt = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False)  # SQLAlchemy added
    updated_at = Column(DateTime, nullable=False)  # SQLAlchemy added
    
    companies = relationship("UserCompany", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(String, primary_key=True)
    company_name = Column(String, nullable=False)
    company_id = Column(String, unique=True)
    sector = Column(String)
    location = Column(String)
    revenue = Column(Float)
    employees = Column(Integer)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    users = relationship("UserCompany", back_populates="company")

class UserCompany(Base):
    __tablename__ = "user_companies"
    
    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), primary_key=True)
    role = Column(String)
    
    user = relationship("User", back_populates="companies")
    company = relationship("Company", back_populates="users")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True)
    userId = Column(String, nullable=False)  # Use the actual DB column name
    createdAt = Column(DateTime, nullable=False)
    updatedAt = Column(DateTime, nullable=False)
    messages = Column(ARRAY(JSONB))  # JSONB array type
    
    # SQLAlchemy added columns (nullable)
    user_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    user = relationship("User", back_populates="chat_sessions", foreign_keys=[user_id])
    chat_messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    tokens = Column(Integer)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    session = relationship("ChatSession", back_populates="chat_messages")

class Agency(Base):
    __tablename__ = "agencies"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    contact = Column(String)
    description = Column(Text)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    fundings = relationship("Funding", back_populates="agency")

class Funding(Base):
    __tablename__ = "fundings"
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    sector = Column(String)
    deadline = Column(DateTime)
    amount = Column(Float)
    eligibility = Column(Text)
    required_docs = Column(Text)
    agency_id = Column(Integer, ForeignKey("agencies.id"))
    s3_keys = Column(ARRAY(String))  # Changed to array for multiple files
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    agency = relationship("Agency", back_populates="fundings")
    chunks = relationship("FundingChunk", back_populates="funding")

class FundingChunk(Base):
    __tablename__ = "funding_chunks"
    
    id = Column(Integer, primary_key=True)
    funding_id = Column(Integer, ForeignKey("fundings.id"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Vector(1024))  # Titan V2 embeddings are 1024 dimensions
    page_no = Column(Integer)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    funding = relationship("Funding", back_populates="chunks")
