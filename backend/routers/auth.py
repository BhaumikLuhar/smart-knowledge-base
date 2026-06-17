from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Auth"]
)


@router.get("/")
async def auth_stub():
    return {"message": "Auth router active"}