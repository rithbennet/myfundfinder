from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import sqlalchemy
import json
import sys
import os
from pathlib import Path

# Add the app directory to the path for imports
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

from db import engine
from bedrock_service import BedrockService
from document_processor import DocumentProcessor

app = FastAPI(title="MyFundFinder AI API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
bedrock_service = BedrockService()
document_processor = DocumentProcessor()

def validate_file_security(file_bytes: bytes, filename: str) -> bool:
    """Validate file using both extension and magic numbers for security"""
    filename_lower = filename.lower()
    
    # Check file extension
    allowed_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.docx', '.txt'}
    if not any(filename_lower.endswith(ext) for ext in allowed_extensions):
        return False
    
    # Magic number validation for common file types
    if len(file_bytes) < 4:
        return False
        
    magic_numbers = {
        b'\x25\x50\x44\x46': ['.pdf'],  # PDF
        b'\x89\x50\x4E\x47': ['.png'],  # PNG
        b'\xFF\xD8\xFF': ['.jpg', '.jpeg'],  # JPEG
        b'\x47\x49\x46\x38': ['.gif'],  # GIF
        b'\x50\x4B\x03\x04': ['.docx'],  # DOCX (ZIP-based)
        b'\x42\x4D': ['.bmp'],  # BMP
    }
    
    # Check if file starts with valid magic number
    for magic, extensions in magic_numbers.items():
        if file_bytes.startswith(magic):
            return any(filename_lower.endswith(ext) for ext in extensions)
    
    # For text files, check if content is valid UTF-8
    if filename_lower.endswith('.txt'):
        try:
            file_bytes.decode('utf-8')
            return True
        except UnicodeDecodeError:
            return False
    
    # TIFF has different magic numbers
    if filename_lower.endswith('.tiff') or filename_lower.endswith('.tif'):
        return file_bytes.startswith(b'II*\x00') or file_bytes.startswith(b'MM\x00*')
    
    return False

# Pydantic models
class CompanyProfile(BaseModel):
    sector: str
    size: str
    region: Optional[str] = None
    keywords: Optional[str] = None

class FundQuery(BaseModel):
    query: str
    company_profile: Optional[CompanyProfile] = None

class ChatRequest(BaseModel):
    message: str
    company_profile: Optional[CompanyProfile] = None

@app.get("/health")
def health():
    return {"status": "ok", "service": "MyFundFinder AI API"}

@app.get("/grants-test")
def test_grants():
    with engine.connect() as conn:
        # Run simple query test
        result = conn.execute(sqlalchemy.text("SELECT 1+1 AS calc"))
    return {"db_result": [dict(row._mapping) for row in result]}