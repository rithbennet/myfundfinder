from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import boto3
import jwt
from ..db import get_db
from ..models.models import User, UserCompany

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import boto3
import jwt
from ..db import get_db
from ..models.models import User, UserCompany

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Verify JWT token and return current user"""
    try:
        token = credentials.credentials
        
        # Verify with AWS Cognito
        client = boto3.client('cognito-idp', region_name='us-east-1')
        
        try:
            response = client.get_user(AccessToken=token)
            
            # Extract user ID from Cognito response
            user_id = None
            email = None
            for attr in response['UserAttributes']:
                if attr['Name'] == 'sub':
                    user_id = attr['Value']
                elif attr['Name'] == 'email':
                    email = attr['Value']
            
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            # Get user from database
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found in database")
            
            return user
            
        except client.exceptions.NotAuthorizedException:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        except Exception as e:
            print(f"JWT verification error: {e}")
            raise HTTPException(status_code=401, detail="Token verification failed")
            
    except Exception as e:
        print(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

async def verify_company_access(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> bool:
    """Verify user has access to company"""
    access = db.query(UserCompany).filter(
        UserCompany.user_id == current_user.id,
        UserCompany.company_id == company_id
    ).first()
    
    if not access:
        raise HTTPException(status_code=403, detail="Access denied to company")
    
    return True
