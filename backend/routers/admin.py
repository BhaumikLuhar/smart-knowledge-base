from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"],
)


@router.get("/")
async def admin_stub():
    return {"message": "Admin router active"}
