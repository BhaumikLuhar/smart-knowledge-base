from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials

from storage.sql.dependencies import (
    get_sql_store
)

from storage.sql.sql_store import (
    SQLStore
)

from core.auth.jwt_service import (
    verify_token
)

from core.auth.user_context import (
    UserContext
)


bearer_scheme = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), sql_store: SQLStore = Depends(get_sql_store)) -> UserContext:
    """
    FastAPI dependency to get the current user from the JWT token.
    """

    payload = verify_token(credentials.credentials)

    users = await sql_store.query(
        "users",
        {
            "id": payload.get("sub")
        }
    )

    if not users:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )
    
    user = users[0]

    if not user.get("is_active"):
        raise HTTPException(
            status_code=403,
            detail="User account disabled"
        )
    

    return UserContext(
        id=str(user["id"]),
        email=user["email"],
        role=user["role"],
        department_id=str(user["department_id"]) if user.get("department_id") else None,
        is_active=user["is_active"]
    )


async def require_admin(current_user: UserContext = Depends(get_current_user)) -> UserContext:
    """
    FastAPI dependency to require the current user to be an admin.
    """

    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    return current_user