from fastapi import HTTPException
from storage.sql.sql_store import SQLStore

class PermissionService:

    def __init__(self, sql_store: SQLStore):
        self.sql_store = sql_store


    async def create_permission(self, role: str, department_id: str, can_access_department_id: str)->dict:
        """
        Create permission for a role to access a department.
        """

        valid_roles = [
            "employee",
            "manager",
            "admin"
        ]

        if role not in valid_roles:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Role must be one of "
                    f"{valid_roles}"
                )
            )
        
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
        
        access_department = await self.sql_store.query(
            "departments",
            {
                "id": can_access_department_id
            }
        )

        if not access_department:
            raise HTTPException(
                status_code=404,
                detail="Access department not found"
            )
        
        existing = await self.sql_store.query(
            "permissions",
            {
                "role": role,
                "department_id": department_id,
                "can_access_department_id":
                    can_access_department_id
            }
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Permission rule "
                    "already exists"
                )
            )

        permission = await self.sql_store.save(
            "permissions",
            {
                "role": role,
                "department_id": department_id,
                "can_access_department_id":
                    can_access_department_id
            }
        )

        await self.sql_store.save(
            "audit_logs",
            {
                "action": "permission_rule_changed",
                "resource_type": "permission",
                "resource_id": str(permission["id"]),
                "details": {
                    "role": role,
                    "department_id": department_id,
                    "can_access_department_id":
                        can_access_department_id,
                },
            },
        )

        return permission