import boto3
import json
import uuid
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from ..models.models import ChatSession, ChatMessage, FundingChunk, Company, Funding
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
        self.model_id = "amazon.nova-pro-v1:0"
    
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
    
    def get_conversation_context(self, session_id: str) -> dict:
        """Extract context from recent conversation messages"""
        # Get last 10 messages from this session
        recent_messages = self.db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at.desc()).limit(10).all()
        
        context = {
            "shown_grants": [],
            "last_query_type": None,
            "available_grants": []
        }
        
        # Parse messages for grant context
        for message in recent_messages:
            if message.role == "assistant":
                content = message.content.lower()
                
                # Look for grant mentions in assistant responses
                grant_patterns = [
                    "digital content grant (dcg) – prime grant",
                    "digital content grant (dcg) – mini grant", 
                    "digital content grant (dcg) – marketing",
                    "sme automation and digitalisation facility",
                    "malaysia digital x-port grant",
                    "green technology financing scheme"
                ]
                
                for pattern in grant_patterns:
                    if pattern in content:
                        # Extract clean grant name
                        if "prime" in pattern:
                            context["available_grants"].append("Digital Content Grant (DCG) – Prime Grant")
                        elif "mini" in pattern:
                            context["available_grants"].append("Digital Content Grant (DCG) – Mini Grant")
                        elif "marketing" in pattern:
                            context["available_grants"].append("Digital Content Grant (DCG) – Marketing & Commercialisation Grant")
                        elif "automation" in pattern:
                            context["available_grants"].append("SME Automation and Digitalisation Facility")
                        elif "x-port" in pattern:
                            context["available_grants"].append("Malaysia Digital X-Port Grant")
                        elif "green technology" in pattern:
                            context["available_grants"].append("Green Technology Financing Scheme")
                
                # Also look for numbered lists like "1. Grant Name"
                lines = message.content.split('\n')
                for line in lines:
                    if any(char.isdigit() and '. ' in line for char in line[:5]):
                        # Extract grant name from numbered list
                        if 'dcg' in line.lower() and 'prime' in line.lower():
                            context["available_grants"].append("Digital Content Grant (DCG) – Prime Grant")
                        elif 'dcg' in line.lower() and 'mini' in line.lower():
                            context["available_grants"].append("Digital Content Grant (DCG) – Mini Grant")
                        elif 'dcg' in line.lower() and 'marketing' in line.lower():
                            context["available_grants"].append("Digital Content Grant (DCG) – Marketing & Commercialisation Grant")
                        elif 'sme automation' in line.lower() or 'adf' in line.lower():
                            context["available_grants"].append("SME Automation and Digitalisation Facility")
        
        # Remove duplicates while preserving order
        context["available_grants"] = list(dict.fromkeys(context["available_grants"]))
        
        print(f"📋 Conversation context: {context}")
        return context
    
    def detect_specific_grant_request(self, query: str, context: dict) -> str:
        """Detect if user is asking about a specific grant from previous context"""
        query_lower = query.lower()
        
        # Check for specific grant names in query
        specific_grants = {
            "sme automation": "SME Automation and Digitalisation Facility",
            "adf": "SME Automation and Digitalisation Facility",
            "automation facility": "SME Automation and Digitalisation Facility",
            "digitalisation facility": "SME Automation and Digitalisation Facility",
            "dcg prime": "Digital Content Grant (DCG) – Prime Grant",
            "prime grant": "Digital Content Grant (DCG) – Prime Grant",
            "prime": "Digital Content Grant (DCG) – Prime Grant",
            "dcg mini": "Digital Content Grant (DCG) – Mini Grant", 
            "mini grant": "Digital Content Grant (DCG) – Mini Grant",
            "mini": "Digital Content Grant (DCG) – Mini Grant",
            "dcg marketing": "Digital Content Grant (DCG) – Marketing & Commercialisation Grant",
            "marketing grant": "Digital Content Grant (DCG) – Marketing & Commercialisation Grant",
            "marketing": "Digital Content Grant (DCG) – Marketing & Commercialisation Grant",
            "commercialisation": "Digital Content Grant (DCG) – Marketing & Commercialisation Grant",
            "x-port": "Malaysia Digital X-Port Grant",
            "mdxg": "Malaysia Digital X-Port Grant",
            "green technology": "Green Technology Financing Scheme"
        }
        
        # Check for multiple grants in one query
        found_grants = []
        for keyword, grant_name in specific_grants.items():
            if keyword in query_lower:
                found_grants.append(grant_name)
                print(f"🎯 Detected specific grant: '{keyword}' → {grant_name}")
        
        # If multiple grants found, return the first one for now
        # TODO: Could be enhanced to handle multiple grants
        if found_grants:
            if len(found_grants) > 1:
                print(f"📝 Multiple grants detected: {found_grants}, showing first one")
            return found_grants[0]
        
        # Check for positional references like "first one", "second grant"
        if any(phrase in query_lower for phrase in ["first", "1st", "number 1"]):
            if context["available_grants"]:
                return context["available_grants"][0]
        elif any(phrase in query_lower for phrase in ["second", "2nd", "number 2"]):
            if len(context["available_grants"]) > 1:
                return context["available_grants"][1]
        
        # Check for "more details", "tell me more" patterns
        if any(phrase in query_lower for phrase in ["more details", "tell me more", "more info", "know more"]):
            # If only one grant was shown, assume they want details about it
            if len(context["available_grants"]) == 1:
                return context["available_grants"][0]
        
        return None
    
    async def get_chunks_by_intent(self, query: str, session_id: str, eligible_grant_ids: List[int]) -> List[FundingChunk]:
        """Get chunks based on user intent - overview or detailed"""
        
        # Get conversation context
        context = self.get_conversation_context(session_id)
        
        # Check if user wants details about a specific grant
        specific_grant = self.detect_specific_grant_request(query, context)
        
        if specific_grant:
            print(f"🎯 User wants details about: {specific_grant}")
            
            # Get ALL chunks for this specific grant
            grant = self.db.query(Funding).filter(
                Funding.title.ilike(f"%{specific_grant}%")
            ).first()
            
            if grant:
                chunks = self.db.query(FundingChunk).filter(
                    FundingChunk.funding_id == grant.id
                ).all()
                
                print(f"📚 Retrieved {len(chunks)} detailed chunks for {grant.title}")
                return chunks
        
        # Default: Get diverse overview (1 chunk per grant)
        print(f"📋 Providing overview of {len(eligible_grant_ids)} grants")
        return await self.get_diverse_chunks(eligible_grant_ids)
    
    async def get_diverse_chunks(self, eligible_funding_ids: List[int]) -> List[FundingChunk]:
        """Get one chunk per grant for overview"""
        if not eligible_funding_ids:
            chunks = self.db.query(FundingChunk).limit(10).all()
            return chunks
        
        selected_chunks = []
        seen_grants = set()
        
        for grant_id in eligible_funding_ids:
            chunk = self.db.query(FundingChunk).filter(
                FundingChunk.funding_id == grant_id
            ).first()
            
            if chunk and chunk.funding_id not in seen_grants:
                selected_chunks.append(chunk)
                seen_grants.add(chunk.funding_id)
                
                if len(selected_chunks) >= 5:
                    break
        
        return selected_chunks
    
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
        
        # Build context from chunks - include grant details
        if chunks:
            context_parts = []
            seen_grants = set()
            
            for chunk in chunks:
                grant_id = chunk.funding.id
                if grant_id not in seen_grants:
                    seen_grants.add(grant_id)
                    grant_info = f"""
Grant: {chunk.funding.title}
Sector: {chunk.funding.sector or 'General'}
Amount: RM{chunk.funding.amount:,.0f} (max)
Eligibility: {chunk.funding.eligibility or 'See requirements'}
Description: {chunk.funding.description or 'No description available'}
Content: {chunk.chunk_text[:500]}...
"""
                    context_parts.append(grant_info)
            
            context = "\n" + "="*50 + "\n".join(context_parts)
        else:
            context = "No specific grants found in database for this query."

        prompt = f"""You are MyFundFinder, a Malaysian SME funding assistant.

CRITICAL: You MUST use the grant information provided below. DO NOT say "no grants found" if grants are listed.

Company: {company.company_name} ({company.sector} sector, {company.employees} employees)
User Query: {query}

AVAILABLE GRANTS:
{context}

INSTRUCTIONS:
1. If grants are listed above, recommend the most relevant ones
2. Explain eligibility and application process briefly
3. If showing multiple grants, END with: "Would you like more details about any specific grant?"
4. If showing detailed info for one grant, provide comprehensive details
5. Be specific about grant names, amounts, and requirements
6. Focus on Malaysian context only

RESPONSE STYLE:
- For overviews: List grants with key details, then ask for preferences
- For details: Provide comprehensive information about the specific grant"""

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
