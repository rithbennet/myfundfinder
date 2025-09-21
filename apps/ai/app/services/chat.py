import boto3
import json
import uuid
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from ..models.models import ChatSession, ChatMessage, FundingChunk, Company
from .embeddings import EmbeddingService
import os

class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.bedrock = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        self.embedding_service = EmbeddingService()
        self.model_id = "meta.llama3-70b-instruct-v1:0"
    
    def get_or_create_session(self, user_id: str) -> ChatSession:
        """Get or create chat session for user"""
        session = self.db.query(ChatSession).filter(
            ChatSession.userId == user_id
        ).order_by(ChatSession.created_at.desc()).first()
        
        if not session:
            now = datetime.utcnow()
            session = ChatSession(
                id=str(uuid.uuid4()),
                userId=user_id,
                user_id=user_id,  # Also set the FK field
                createdAt=now,
                updatedAt=now,
                created_at=now,
                updated_at=now
            )
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
        
        return session
    
    def save_message(self, session_id: str, role: str, content: str):
        """Save chat message to database"""
        now = datetime.utcnow()
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            tokens=len(content.split()),  # Simple token estimation
            created_at=now,
            updated_at=now
        )
        self.db.add(message)
        self.db.commit()
    
    async def vector_search(self, query: str, eligible_funding_ids: List[int]) -> List[FundingChunk]:
        """Perform vector similarity search using pgvector"""
        if not eligible_funding_ids:
            print("⚠️ No eligible funding IDs provided")
            return []
        
        try:
            # Generate embedding for the query
            query_embedding = await self.embedding_service.generate_embedding(query)
            
            # Convert to string format for SQL
            embedding_str = str(query_embedding)
            
            # Perform vector similarity search with cosine distance
            sql_query = text("""
                SELECT fc.*, f.title, f.sector
                FROM funding_chunks fc
                JOIN fundings f ON fc.funding_id = f.id
                WHERE fc.funding_id = ANY(:funding_ids)
                ORDER BY fc.embedding <=> :query_embedding::vector
                LIMIT 5
            """)
            
            result = self.db.execute(sql_query, {
                'funding_ids': eligible_funding_ids,
                'query_embedding': embedding_str
            })
            
            chunks = []
            for row in result:
                chunk = self.db.query(FundingChunk).filter(FundingChunk.id == row.id).first()
                if chunk:
                    chunks.append(chunk)
            
            print(f"📊 Vector search: found {len(chunks)} relevant chunks from {len(eligible_funding_ids)} eligible grants")
            if chunks:
                print(f"🎯 Top result: {chunks[0].funding.title} (Sector: {chunks[0].funding.sector})")
            
            return chunks
            
        except Exception as e:
            print(f"❌ Vector search error: {e}")
            # Fallback to simple text search
            chunks = self.db.query(FundingChunk).filter(
                FundingChunk.funding_id.in_(eligible_funding_ids)
            ).limit(5).all()
            
            print(f"📊 Fallback search: found {len(chunks)} chunks")
            return chunks
    
    def _check_guardrails(self, query: str) -> tuple[bool, str]:
        """Check if query is about funding/grants. Return (is_valid, response)"""
        query_lower = query.lower()
        
        # Blocked topics (high priority)
        blocked_keywords = [
            'weather', 'recipe', 'movie', 'music', 'sports', 'game', 'joke',
            'personal', 'relationship', 'health', 'medical', 'politics', 'religion',
            'entertainment', 'celebrity', 'travel', 'food', 'shopping', 'capital of',
            'geography', 'history', 'science', 'math', 'homework'
        ]
        
        # Check for blocked topics first
        if any(keyword in query_lower for keyword in blocked_keywords):
            return False, "I'm a specialized assistant for Malaysian SME funding and grants. Please ask me about grants, funding schemes, business loans, or government support programs for SMEs."
        
        # Funding-related keywords
        funding_keywords = [
            'grant', 'funding', 'loan', 'finance', 'money', 'capital', 'investment',
            'subsidy', 'scheme', 'program', 'support', 'assistance', 'aid',
            'sme', 'startup', 'business', 'company', 'entrepreneur', 'digital',
            'transformation', 'technology', 'innovation', 'mdec', 'government',
            'application', 'eligibility', 'document', 'requirement', 'malaysia'
        ]
        
        # Check if query contains funding keywords
        has_funding_keywords = any(keyword in query_lower for keyword in funding_keywords)
        
        if not has_funding_keywords:
            return False, "I'm a specialized assistant for Malaysian SME funding and grants. Please ask me about grants, funding schemes, business loans, or government support programs for SMEs."
        
        return True, ""

    async def generate_response(self, query: str, chunks: List[FundingChunk], company: Company) -> str:
        """Generate LLM response using Bedrock Llama with guardrails"""
        
        # Check guardrails first
        is_valid, guardrail_response = self._check_guardrails(query)
        if not is_valid:
            return guardrail_response
        
        # Build context from chunks
        context = "\n\n".join([
            f"Grant: {chunk.funding.title}\nContent: {chunk.chunk_text}"
            for chunk in chunks
        ])
        
        prompt = f"""You are MyFundFinder, a specialized AI assistant for Malaysian SME funding and grants. You ONLY provide advice about:
- Government grants and funding schemes
- Business loans and financing options  
- SME support programs
- Application processes and eligibility
- Required documents and deadlines

STRICT RULES:
- NEVER discuss topics outside of funding/grants/business finance
- If asked about other topics, redirect to funding advice
- Always stay professional and helpful
- Focus on Malaysian context

Company Profile:
- Name: {company.company_name}
- Sector: {company.sector}
- Location: {company.location}
- Employees: {company.employees}
- Revenue: RM{company.revenue}

User Query: {query}

Available Grant Information:
{context}

Provide specific, actionable funding advice for this Malaysian SME."""

        try:
            # Format prompt for Llama 3
            formatted_prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
            
            body = json.dumps({
                "prompt": formatted_prompt,
                "max_gen_len": 1000,
                "temperature": 0.7
            })
            
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=body,
                contentType='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['generation']
            
        except Exception as e:
            return f"I apologize, but I'm having trouble generating a response right now. Please try again later. Error: {str(e)}"
