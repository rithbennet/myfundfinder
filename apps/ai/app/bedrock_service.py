import boto3
import json
import numpy as np
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class BedrockService:
    def __init__(self):
        self.bedrock_runtime = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        self.model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
        self.embeddings_model_id = os.getenv('BEDROCK_EMBEDDINGS_MODEL_ID', 'amazon.titan-embed-text-v1')

    def generate_embeddings(self, text: str) -> List[float]:
        """Generate embeddings for text using Bedrock Titan embeddings"""
        try:
            body = json.dumps({
                "inputText": text
            })
            
            response = self.bedrock_runtime.invoke_model(
                modelId=self.embeddings_model_id,
                body=body,
                contentType='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['embedding']
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return []

    def chat_with_nova_pro(self, prompt: str, system_prompt: str = "") -> str:
        """Chat with Nova Pro model for text analysis"""
        try:
            messages = [
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ]
            
            # Add system message if provided
            if system_prompt:
                messages.insert(0, {
                    "role": "user", 
                    "content": [{"text": f"System: {system_prompt}"}]
                })
            
            body = {
                "messages": messages,
                "inferenceConfig": {
                    "maxTokens": 512,
                    "temperature": 0.7,
                    "topP": 0.9
                }
            }
            
            response = self.bedrock_runtime.converse(
                modelId="amazon.nova-pro-v1:0",
                messages=messages,
                inferenceConfig=body["inferenceConfig"]
            )
            
            # Extract text from Nova Pro response
            return response['output']['message']['content'][0]['text']
        except Exception as e:
            print(f"Error with Nova Pro: {e}")
            return "I'm sorry, I couldn't process your request at the moment."

    def extract_company_info_from_text(self, business_text: str) -> dict:
        """Extract structured company information using Nova Pro NLP"""
        
        system_prompt = "You are an expert at extracting business information from text. Return only valid JSON."
        
        user_prompt = f"""
        Extract company information from this business text and return ONLY a valid JSON object:

        {{
            "company_name": "name or null",
            "sector": "business sector or null", 
            "company_size": "startup/small/medium or null",
            "location": "city/region or null",
            "description": "brief description or null",
            "keywords": "relevant keywords, comma-separated or null",
            "employees": "number of employees or null",
            "funding_needs": "funding requirements mentioned or null"
        }}

        Business text: {business_text}
        
        Return ONLY the JSON object, no other text.
        """
        
        response = self.chat_with_nova_pro(user_prompt, system_prompt)
        
        try:
            # Clean and parse JSON response
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:-3]
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:-3]
            
            import json
            return json.loads(cleaned_response)
        except Exception as e:
            print(f"Error parsing company info: {e}")
            return {"error": "Failed to extract company information"}

    def analyze_company_for_funding(self, company_profile: Dict[str, Any]) -> str:
        """Analyze company profile and suggest funding strategies"""
        system_prompt = """You are an expert funding advisor for small and medium enterprises (SMEs). 
        Your role is to analyze company profiles and provide specific, actionable funding recommendations.
        Focus on government grants, corporate funding, and private investment opportunities that match the company's sector, size, and needs."""
        
        user_prompt = f"""
        Please analyze this company profile and provide funding recommendations:
        
        Company Details:
        - Sector: {company_profile.get('sector', 'Not specified')}
        - Company Size: {company_profile.get('size', 'Not specified')}
        - Region: {company_profile.get('region', 'Not specified')}
        - Keywords/Focus Areas: {company_profile.get('keywords', 'Not specified')}
        
        Please provide:
        1. Top 3 types of funding that would be most suitable
        2. Specific government grants they should look for
        3. Corporate funding programs that might match
        4. Timeline recommendations for applications
        5. Key preparation steps they should take
        
        Keep recommendations specific and actionable.
        """
        
        return self.chat_with_nova_pro(user_prompt, system_prompt)

    def find_similar_funds(self, query_embedding: List[float], fund_embeddings: List[Dict]) -> List[Dict]:
        """Find funds similar to a query using cosine similarity"""
        if not query_embedding or not fund_embeddings:
            return []
        
        similarities = []
        query_vector = np.array(query_embedding)
        
        for fund in fund_embeddings:
            fund_vector = np.array(fund['embedding'])
            
            # Calculate cosine similarity
            cosine_sim = np.dot(query_vector, fund_vector) / (
                np.linalg.norm(query_vector) * np.linalg.norm(fund_vector)
            )
            
            similarities.append({
                'fund': fund,
                'similarity': float(cosine_sim)
            })
        
        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:10]  # Return top 10 matches

    def generate_fund_explanation(self, fund_details: Dict[str, Any], company_profile: Dict[str, Any]) -> str:
        """Generate personalized explanation of why a fund matches a company"""
        prompt = f"""
        Explain why this funding opportunity is a good match for this company:
        
        Fund Details:
        - Title: {fund_details.get('title', '')}
        - Description: {fund_details.get('description', '')}
        - Sector: {fund_details.get('sector', '')}
        - Deadline: {fund_details.get('deadline', '')}
        
        Company Profile:
        - Sector: {company_profile.get('sector', '')}
        - Size: {company_profile.get('size', '')}
        - Region: {company_profile.get('region', '')}
        - Focus Areas: {company_profile.get('keywords', '')}
        
        Provide a brief, personalized explanation (2-3 sentences) of:
        1. Why this fund is relevant to their business
        2. What specific aspects make them a good candidate
        3. Any tips for a successful application
        """
        
        return self.chat_with_nova_pro(prompt)