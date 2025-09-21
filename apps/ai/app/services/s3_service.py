import boto3
from fastapi import UploadFile
import os

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'myfundfinder-documents')
    
    async def upload_file(self, file: UploadFile, s3_key: str) -> str:
        """Upload file to S3 and return the key"""
        try:
            content = await file.read()
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=content,
                ContentType=file.content_type
            )
            
            return s3_key
        except Exception as e:
            raise Exception(f"Failed to upload file to S3: {str(e)}")
    
    def get_file_url(self, s3_key: str) -> str:
        """Generate presigned URL for file access"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=3600  # 1 hour
            )
            return url
        except Exception as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")
