import boto3
import json
import uuid
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from ..models.models import ChatSession, ChatMessage, Company
from .grant_tools import GrantTools
import os

class ToolBasedChatService:
    def __init__(self, db: Session):
        self.db = db
        self.bedrock = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        self.grant_tools = GrantTools(db)
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
                user_id=user_id,
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
            tokens=len(content.split()),
            created_at=now,
            updated_at=now
        )
        self.db.add(message)
        self.db.commit()
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """Get recent conversation history for context"""
        messages = self.db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
        
        # Reverse to get chronological order
        messages.reverse()
        
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages
        ]
    
    async def generate_response_with_tools(self, query: str, company: Company, session_id: str) -> str:
        """Generate response using tools and conversation context"""
        
        print(f"🤖 LLM Tool Calling Process Started")
        print(f"📝 Query: '{query}'")
        
        # Get conversation history
        conversation_history = self.get_conversation_history(session_id)
        print(f"💬 Conversation History: {len(conversation_history)} messages")
        
        # Build conversation context for LLM
        conversation_context = ""
        if conversation_history:
            conversation_context = "\n".join([
                f"{msg['role'].title()}: {msg['content']}"
                for msg in conversation_history[-6:]  # Last 6 messages
            ])
            print(f"📋 Context: {conversation_context[:200]}...")
        
        # Simple tool usage detection and execution
        query_lower = query.lower()
        print(f"🔍 Analyzing query for tool selection...")
        
        # Two-stage approach: Metadata first, then detailed chunks
        if any(phrase in query_lower for phrase in ['what grants', 'available grants', 'all grants', 'list grants', 'grants for']):
            print(f"🛠️ Tool Selected: get_all_available_grants() [METADATA ONLY]")
            grants = self.grant_tools.get_all_available_grants()
            tool_result = f"Available grants (metadata): {json.dumps(grants, indent=2)}"
            print(f"📊 Tool Result: Found {len(grants)} grants (metadata only)")
            
        elif any(phrase in query_lower for phrase in ['tell me more', 'more details', 'details about', 'more about', 'explain']):
            # Stage 2: User wants detailed info - NOW use RAG chunks
            print(f"🛠️ Tool Selected: get_grant_by_name() [WITH RAG CHUNKS - STAGE 2]")
            
            # Extract grant name from query or conversation context
            grant_name = query_lower.replace('tell me more', '').replace('more details', '').replace('details about', '').replace('more about', '').replace('explain', '').strip()
            
            # If no specific grant mentioned, check conversation history for last mentioned grants
            if not grant_name or len(grant_name) < 3:
                # Look for grants mentioned in recent conversation
                for msg in reversed(conversation_history[-3:]):
                    if msg["role"] == "assistant":
                        content = msg["content"].lower()
                        if "dcg" in content and "prime" in content:
                            grant_name = "dcg prime"
                            break
                        elif "dcg" in content and "mini" in content:
                            grant_name = "dcg mini"
                            break
                        elif "adf" in content or "automation" in content:
                            grant_name = "adf"
                            break
            
            grant_details = self.grant_tools.get_grant_by_name(grant_name)
            tool_result = f"Detailed grant information with RAG content: {json.dumps(grant_details, indent=2)}"
            print(f"📊 Tool Result: Retrieved '{grant_name}' with {grant_details.get('total_chunks', 0)} RAG chunks")
            
        elif any(word in query_lower for word in ['rm', 'ringgit', 'million', 'thousand']) or any(char.isdigit() for char in query):
            print(f"🛠️ Tool Selected: search_by_amount() [METADATA ONLY]")
            grants = self.grant_tools.search_by_amount(min_amount=50000)
            tool_result = f"Grants by amount (metadata): {json.dumps(grants, indent=2)}"
            print(f"📊 Tool Result: Found {len(grants)} grants by amount (metadata only)")
            
        elif len(query.split()) <= 3 and any(word in query_lower for word in ['sure', 'yes', 'ok', 'okay', 'continue']):
            print(f"🛠️ Tool Selected: None (conversational response)")
            tool_result = "No tool needed - conversational response"
            print(f"💭 Conversational Response: Using context only")
            
        else:
            # Stage 1: General search - METADATA ONLY for recommendations
            print(f"🛠️ Tool Selected: search_grants() [METADATA ONLY - STAGE 1]")
            grants = self.grant_tools.search_grants(query, limit=5)
            tool_result = f"Grant recommendations (metadata): {json.dumps(grants, indent=2)}"
            print(f"📊 Tool Result: Found {len(grants)} grant recommendations (metadata only)")
        
        # Build prompt for LLM
        prompt = f"""You are MyFundFinder, a Malaysian SME funding assistant with natural conversation abilities.

Company: {company.company_name} ({company.sector} sector, {company.employees} employees)

Recent Conversation:
{conversation_context}

Current Query: {query}

Tool Results:
{tool_result}

INSTRUCTIONS:
- Use conversation context to understand follow-ups like "Sure", "What about the other one?"
- STAGE 1 (Recommendations): When showing grant metadata, provide overview and ask "Would you like more details about any specific grant?"
- STAGE 2 (Details): When user asks for "more details" or "tell me more", provide comprehensive information from RAG content
- Handle conversational responses naturally (e.g., "Sure" means continue the conversation)
- Always be helpful and conversational
- Focus on Malaysian SME funding only
- For general queries, show grant summaries first, then offer detailed information

RESPONSE STYLE:
- Overview queries: Show grant summaries + ask which one they want details about
- Detail queries: Provide comprehensive information from document content
- Conversational: Continue naturally based on context

Respond naturally and conversationally based on the query and conversation context."""

        print(f"🎯 Sending to LLM...")
        print(f"📤 Prompt length: {len(prompt)} characters")

        try:
            # Nova Pro uses messages format
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
            
            body = json.dumps({
                "messages": messages,
                "inferenceConfig": {
                    "maxTokens": 1000,
                    "temperature": 0.7
                }
            })
            
            print(f"🚀 Invoking Nova Pro: {self.model_id}")
            
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=body,
                contentType='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            llm_response = response_body['output']['message']['content'][0]['text']
            
            print(f"✅ Nova Pro Response received: {len(llm_response)} characters")
            print(f"📝 Response preview: {llm_response[:200]}...")
            
            return llm_response
            
        except Exception as e:
            print(f"❌ LLM Error: {str(e)}")
            return f"I apologize, but I'm having trouble accessing the grant information right now. Please try again later. Error: {str(e)}"
