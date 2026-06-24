from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError, ExpiredSignatureError

from fastapi import HTTPException

from core.config import settings

def create_token(user_id: str, email: str, role: str, department_id: str | None)-> str:
    """
    Create a JWT token for the user.
    """

    expire= datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)

    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "department_id": str(department_id) if department_id is not None else None,
        "exp": expire
    }

    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    return token


def verify_token(token: str)-> dict:
    """
    Verify the JWT token and return the payload.
    """

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

        return payload
    
    except ExpiredSignatureError:

        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )

    except JWTError:
        
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )