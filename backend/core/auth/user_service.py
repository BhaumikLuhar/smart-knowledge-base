from fastapi import HTTPException

from storage.sql.sql_store import SQLStore

from core.auth.password import hash_password


class UserService:

    def __init__(self, sql_store: SQLStore):
        self.sql_store = sql_store

    
    async def list_users(self)-> list[dict]:
        """
        Return all users.
        """

        return await self.sql_store.execute_raw(
            """
            SELECT
                u.id,
                u.email,
                u.full_name,
                u.role,
                u.is_active,
                u.department_id,
                d.display_name
                    AS department_name,
                u.created_at,
                u.last_login
            FROM users u
            LEFT JOIN departments d
                ON d.id = u.department_id
            ORDER BY u.created_at DESC
            """
        )
    

    async def create_user(
            self,
            email: str,
            password: str,
            full_name: str,
            department_id: str | None,
            role: str
    )->dict:
        
        existing = await self.sql_store.query(
            "users",
            {
                "email": email
            }
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists"
            )
        

        valid_roles = {
            "admin",
            "manager",
            "employee"
        }

        if role not in valid_roles:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Role must be one of "
                    f"{valid_roles}"
                )
            )
        
        if department_id:
            department = await self.sql_store.query(
                "departments",
                {
                    "id": department_id
                }
            )

            if not department:
                raise HTTPException(
                    status_code=404,
                    detail="Department not found"
                )
            
        
        return await self.sql_store.save(
            "users",
            {
                "email": email,
                "hashed_password":
                    hash_password(password),
                "full_name": full_name,
                "department_id":
                    department_id,
                "role": role,
                "is_active": True
            }
        )
    

    async def update_user(
            self,
            user_id: str,
            role: str | None,
            department_id: str | None,
            is_active: bool | None
    )->dict:
        
        users= await self.sql_store.query(
            "users",
            {
                "id": user_id
            }
        )

        if not users:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        updates = {}

        if role is not None:
            updates["role"] = role

        if department_id is not None:
            updates["department_id"] = department_id

        if is_active is not None:
            updates["is_active"] = is_active

        if not updates:
            return users[0]

        return await self.sql_store.update(
            "users",
            user_id,
            updates
        )