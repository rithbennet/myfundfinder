import boto3
import json
from typing import List
import os

class EmbeddingService:
    def __init__(self):
        # Use permanent AWS credentials from environment
        self.bedrock = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        self.model_id = "amazon.titan-embed-text-v2:0"
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using Bedrock Titan v2"""
        try:
            body = json.dumps({
                "inputText": text
            })
            
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=body,
                contentType='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['embedding']
            
        except Exception as e:
            print(f"❌ Bedrock embedding error: {e}")
            raise e
