from fastapi import APIRouter
from fastapi import Depends

from core.auth.dependencies import get_current_user
from core.auth.user_context import UserContext

from core.permissions.permission_service import PermissionService

from storage.sql.dependencies import get_sql_store
from storage.sql.sql_store import SQLStore


router = APIRouter(
    prefix="/api/v1/user",
    tags=["User"]
)


@router.get("/permissions")
async def get_user_permissions(
    current_user: UserContext = Depends(get_current_user),
    sql_store: SQLStore = Depends(get_sql_store)
):
    """
    Return the current user's effective permissions.
    """

    permission_service = PermissionService(sql_store)

    allowed_departments = (
        await permission_service.get_allowed_departments(
            current_user
        )
    )

    allowed_visibilities = (
        await permission_service.get_allowed_visibilities(
            current_user
        )
    )

    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role,
            "department_id": current_user.department_id
        },
        "allowed_departments": allowed_departments,
        "allowed_visibilities": allowed_visibilities
    }