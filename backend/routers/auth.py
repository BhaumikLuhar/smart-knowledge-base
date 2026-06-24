from fastapi import APIRouter
from fastapi import Depends

from storage.sql.dependencies import (
    get_sql_store
)

from storage.sql.sql_store import (
    SQLStore
)

from core.auth.schemas import (
    LoginRequest,
    LoginResponse
)

from core.auth.auth_service import (
    AuthService
)

from core.auth.dependencies import (
    get_current_user
)

from core.auth.user_context import (
    UserContext
)
router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Auth"]
)


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    sql_store: SQLStore = Depends(get_sql_store)
):
    service = AuthService(sql_store)

    return await service.login(
        email=payload.email,
        password=payload.password
    )


@router.post("/logout")
async def logout(
    current_user: UserContext = Depends(get_current_user),
    sql_store: SQLStore = Depends(get_sql_store)
):
    service = AuthService(sql_store)

    return await service.logout(
        current_user.id
    )


@router.get("/me")
async def me(
    current_user: UserContext = Depends(get_current_user),
    sql_store: SQLStore = Depends(get_sql_store)
):
    service = AuthService(sql_store)

    return await service.get_profile(
        current_user.id
    )