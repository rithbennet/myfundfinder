import jwt
import os
from typing import Dict, Any

def verify_jwt_token(token: str) -> Dict[str, Any]:
    """Verify JWT token and return payload"""
    try:
        # For Cognito JWT verification
        secret = os.getenv('JWT_SECRET', 'your-secret-key')
        algorithm = os.getenv('JWT_ALGORITHM', 'HS256')
        
        payload = jwt.decode(token, secret, algorithms=[algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")
