from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..db import get_db
from ..models.models import User, Company, ChatSession, ChatMessage, Funding, FundingChunk
from ..schemas.schemas import ChatRequest, ChatResponse, ChatSession as ChatSessionSchema, ChatMessage as ChatMessageSchema
from ..routers.auth import get_current_user, verify_company_access
from ..services.chat import ChatService
from ..services.embeddings import EmbeddingService
from ..services.grant_filter import GrantFilterService

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Main chat endpoint for grant recommendations"""
    # Get user's company from UserCompany relationship
    user_company = db.query(UserCompany).filter(
        UserCompany.user_id == current_user.id
    ).first()
    
    if not user_company:
        raise HTTPException(status_code=404, detail="No company associated with user")
    
    # Get company details
    company = db.query(Company).filter(Company.id == user_company.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    print(f"🏢 User {current_user.email} querying for company: {company.company_name} (Sector: {company.sector})")
    
    # Initialize services
    chat_service = ChatService(db)
    embedding_service = EmbeddingService()
    grant_filter = GrantFilterService(db)
    
    # Create or get chat session
    session = chat_service.get_or_create_session(current_user.id)
    
    # Save user message
    chat_service.save_message(session.id, "user", request.message)
    
    # Filter eligible grants based on company profile
    eligible_grants = grant_filter.filter_grants(company)
    print(f"📋 Found {len(eligible_grants)} eligible grants for {company.sector} sector")
    
    # Vector search for relevant chunks
    relevant_chunks = await chat_service.vector_search(request.message, eligible_grants)
    
    # Generate response using LLM
    response = await chat_service.generate_response(
        request.message, 
        relevant_chunks, 
        company
    )
    
    # Save assistant response
    chat_service.save_message(session.id, "assistant", response)
    
    return ChatResponse(
        response=response,
        session_id=session.id,
        sources=[chunk.funding.title for chunk in relevant_chunks]
    )

@router.get("/sessions", response_model=List[ChatSessionSchema])
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's chat sessions"""
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.created_at.desc()).limit(20).all()
    
    return sessions

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageSchema])
async def get_session_messages(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages for a specific chat session"""
    # Verify session belongs to user
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    return messages
