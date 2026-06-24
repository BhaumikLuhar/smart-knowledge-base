from datetime import datetime

from fastapi import HTTPException

from storage.sql.sql_store import SQLStore

from core.auth.password import verify_password
from core.auth.jwt_service import create_token


class AuthService:
    def __init__(self, sql_store: SQLStore):
        self.sql_store = sql_store

    
    async def login(self, email: str, password: str)-> dict:

        users= await self.sql_store.query(
            "users",
            {
                "email": email
            }
        )

        if not users:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        user=users[0]

        if not verify_password(password, user["hashed_password"]):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        if not user.get("is_active"):
            raise HTTPException(
                status_code=403,
                detail="User account disabled"
            )
        

        token=create_token(
            user_id=str(user["id"]),
            email=user["email"],
            role=user["role"],
            department_id=str(user["department_id"]) if user.get("department_id") else None
        )

        # update last login timestamp
        await self.sql_store.update(
            "users",
            str(user["id"]),
            {
                "last_login": datetime.utcnow()
            }
        )

        #audit log
        await self.sql_store.save(
            "audit_logs",
            {
                "user_id": str(user["id"]),
                "action": "login",
                "resource_type": "auth",
                "details": {
                    "email": user["email"]
                }
            }
        )


        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": str(user["id"]),
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
                "department_id": (
                    str(user["department_id"])
                    if user["department_id"]
                    else None
                )
            }
        }
    

    async def logout(self, user_id: str)-> dict:
        """
        Logout user by updating last_logout timestamp.
        """

        await self.sql_store.save(
            "audit_logs",
            {
                "user_id": user_id,
                "action": "logout",
                "resource_type": "auth"
            }
        )

        return {
            "message": "logged out"
        }
    

    async def get_profile(self, user_id: str)->dict:
        """
        Get user profile.
        """

        result = await self.sql_store.execute_raw(
            """
            SELECT
                u.id,
                u.email,
                u.full_name,
                u.role,
                u.department_id,
                u.is_active,
                d.display_name AS department_name
            FROM users u
            LEFT JOIN departments d
                ON d.id = u.department_id
            WHERE u.id = $1
            """,
            (
                user_id,
            )
        )

        if not result:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        return result[0]