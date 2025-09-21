from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db import get_db
from ..models.models import User, Funding, FundingChunk
from ..schemas.schemas import FundingUploadResponse
from ..routers.auth import get_current_user
from ..services.document_processor import DocumentProcessor
from ..services.embeddings import EmbeddingService
from ..services.s3_service import S3Service

router = APIRouter(prefix="/admin/funding", tags=["funding"])

@router.post("/upload", response_model=FundingUploadResponse)
async def upload_funding(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    sector: Optional[str] = Form(None),
    deadline: Optional[str] = Form(None),
    amount: Optional[float] = Form(None),
    eligibility: Optional[str] = Form(None),
    required_docs: Optional[str] = Form(None),
    agency_id: Optional[int] = Form(None),
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload funding documents and create embeddings"""
    
    # Create funding record
    funding = Funding(
        title=title,
        description=description,
        sector=sector,
        amount=amount,
        eligibility=eligibility,
        required_docs=required_docs,
        agency_id=agency_id
    )
    db.add(funding)
    db.commit()
    db.refresh(funding)
    
    # Initialize services
    doc_processor = DocumentProcessor()
    embedding_service = EmbeddingService()
    s3_service = S3Service()
    
    chunks_created = 0
    
    for file in files:
        # Upload to S3
        s3_key = f"fundings/{funding.id}/{file.filename}"
        await s3_service.upload_file(file, s3_key)
        
        # Update funding with S3 key (store first file's key)
        if not funding.s3_key:
            funding.s3_key = s3_key
            db.commit()
        
        # Extract text from PDF
        content = await file.read()
        text = doc_processor.extract_text_from_pdf(content)
        
        # Chunk text
        chunks = doc_processor.chunk_text(text)
        
        # Generate embeddings and save chunks
        for i, chunk_text in enumerate(chunks):
            embedding = await embedding_service.generate_embedding(chunk_text)
            
            chunk = FundingChunk(
                funding_id=funding.id,
                chunk_text=chunk_text,
                embedding=embedding,
                page_no=i + 1
            )
            db.add(chunk)
            chunks_created += 1
    
    db.commit()
    
    return FundingUploadResponse(
        funding_id=funding.id,
        status="success",
        chunks_created=chunks_created
    )
