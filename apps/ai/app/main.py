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
        return {"db_result": [dict(row) for row in result]}

@app.post("/ai/analyze-company")
async def analyze_company(company_profile: CompanyProfile):
    """Analyze company profile and provide funding recommendations"""
    try:
        analysis = bedrock_service.analyze_company_for_funding(company_profile.dict())
        return {
            "analysis": analysis,
            "company_profile": company_profile.dict()
        }
    except Exception as e:
        # Log the actual error for debugging but don't expose it to users
        print(f"AI analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="AI analysis service temporarily unavailable")

@app.post("/ai/search-funds")
async def search_funds(fund_query: FundQuery):
    """Search for funds using AI-powered semantic search"""
    try:
        # Generate embeddings for the search query
        query_embedding = bedrock_service.generate_embeddings(fund_query.query)
        
        if not query_embedding:
            raise HTTPException(status_code=500, detail="Failed to generate embeddings for query")
        
        # TODO: Get fund embeddings from database
        # For now, return a placeholder response
        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text("SELECT * FROM grants LIMIT 5"))
            funds = [dict(row) for row in result]
        
        # Generate AI explanation for each fund
        if fund_query.company_profile:
            for fund in funds:
                fund['ai_explanation'] = bedrock_service.generate_fund_explanation(
                    fund, fund_query.company_profile.dict()
                )
        
        return {
            "query": fund_query.query,
            "funds": funds,
            "embedding_length": len(query_embedding)
        }
    except Exception as e:
        # Log the actual error for debugging but don't expose it to users
        print(f"Fund search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Fund search service temporarily unavailable")

@app.post("/ai/chat")
async def chat_with_ai(chat_request: ChatRequest):
    """Chat with AI assistant about funding opportunities"""
    try:
        system_prompt = "You are a helpful funding advisor assistant for small and medium enterprises."
        
        if chat_request.company_profile:
            system_prompt += f"""
            The user's company profile:
            - Sector: {chat_request.company_profile.sector}
            - Size: {chat_request.company_profile.size}
            - Region: {chat_request.company_profile.region or 'Not specified'}
            - Focus Areas: {chat_request.company_profile.keywords or 'Not specified'}
            
            Tailor your responses to their specific business context.
            """
        
        response = bedrock_service.chat_with_nova_pro(chat_request.message, system_prompt)
        
        return {
            "message": chat_request.message,
            "response": response,
            "timestamp": sqlalchemy.func.now()
        }
    except Exception as e:
        # Log the actual error for debugging but don't expose it to users
        print(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Chat service temporarily unavailable")

@app.post("/ai/generate-embeddings")
async def generate_embeddings(text: str):
    """Generate embeddings for given text (utility endpoint)"""
    try:
        embeddings = bedrock_service.generate_embeddings(text)
        return {
            "text": text,
            "embeddings": embeddings,
            "embedding_length": len(embeddings)
        }
    except Exception as e:
        # Log the actual error for debugging but don't expose it to users
        print(f"Embedding generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Embedding generation service temporarily unavailable")

@app.post("/nlp/extract-company-info")
async def extract_company_info(request: Dict[str, str]):
    """Extract company information from business text using Nova Pro NLP"""
    try:
        business_text = request.get("text", "")
        if not business_text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Use Nova Pro to extract company information
        company_info = bedrock_service.extract_company_info_from_text(business_text)
        
        return {
            "input_text": business_text[:200] + "..." if len(business_text) > 200 else business_text,
            "extracted_info": company_info,
            "processing_success": True
        }
    except Exception as e:
        # Log the actual error for debugging but don't expose it to users
        print(f"NLP extraction error: {str(e)}")
        raise HTTPException(status_code=500, detail="NLP extraction service temporarily unavailable")

@app.post("/nlp/test-nova-pro")
async def test_nova_pro():
    """Test Nova Pro connection and basic functionality"""
    try:
        test_text = "TechStartup Inc is a small technology company based in California focusing on AI solutions for healthcare. We have 15 employees and need funding for product development."
        
        response = bedrock_service.chat_with_nova_pro("Extract the company name from this text: " + test_text)
        
        return {
            "test_successful": True,
            "test_input": test_text,
            "nova_pro_response": response
        }
    except Exception as e:
        return {
            "test_successful": False,
            "error": str(e)
        }

# Document Upload Endpoints
@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    analysis_type: str = Form("general")
):
    """
    Upload and analyze documents (PDF, Word, images, text files)
    
    Parameters:
    - file: Document file to upload
    - analysis_type: Type of analysis ("general", "company_info", "funding")
    """
    try:
        # Validate filename
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Validate file type and security
        allowed_extensions = {'.pdf', '.docx', '.txt', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
        file_extension = '.' + file.filename.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Supported: {', '.join(allowed_extensions)}"
            )
        
        # Check file size (10MB limit)
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
        
        # Security: Validate file using magic numbers
        if not validate_file_security(file_content, file.filename):
            raise HTTPException(
                status_code=400, 
                detail="File validation failed. File content doesn't match its extension."
            )
        
        # Process document
        result = document_processor.process_document(
            file_bytes=file_content,
            filename=file.filename,
            analysis_type=analysis_type
        )
        
        if not result.get("processing_success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Document processing failed"))
        
        return {
            "success": True,
            "filename": result["filename"],
            "file_size": result["file_size"],
            "text_length": result["full_text_length"],
            "analysis_type": result["analysis_type"],
            "extracted_text_preview": result["extracted_text_preview"],
            "analysis": result["analysis_result"],
            "message": f"Document '{file.filename}' processed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Log the actual error for debugging but don't expose it to users
        print(f"Document upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="Document upload service temporarily unavailable")

@app.post("/documents/analyze-text")
async def analyze_text_content(request: Dict[str, str]):
    """
    Analyze text content directly without file upload
    
    Parameters:
    - text: Text content to analyze
    - analysis_type: Type of analysis ("general", "company_info", "funding")
    """
    try:
        text_content = request.get("text", "")
        analysis_type = request.get("analysis_type", "general")
        
        if not text_content.strip():
            raise HTTPException(status_code=400, detail="Text content is required")
        
        # Analyze content
        analysis_result = document_processor.analyze_document_content(text_content, analysis_type)
        
        return {
            "success": True,
            "text_length": len(text_content),
            "analysis_type": analysis_type,
            "text_preview": text_content[:200] + "..." if len(text_content) > 200 else text_content,
            "analysis": analysis_result,
            "message": "Text analyzed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text analysis failed: {str(e)}")

@app.get("/documents/supported-formats")
async def get_supported_formats():
    """Get list of supported document formats"""
    return {
        "supported_formats": {
            "pdf": "Portable Document Format",
            "docx": "Microsoft Word Document",
            "txt": "Plain Text File",
            "png": "Portable Network Graphics (with OCR)",
            "jpg": "JPEG Image (with OCR)",
            "jpeg": "JPEG Image (with OCR)",
            "gif": "Graphics Interchange Format (with OCR)",
            "bmp": "Bitmap Image (with OCR)",
            "tiff": "Tagged Image File Format (with OCR)"
        },
        "max_file_size": "10MB",
        "analysis_types": {
            "general": "General document analysis and summary",
            "company_info": "Extract company information from document",
            "funding": "Extract company info and provide funding recommendations"
        }
    }