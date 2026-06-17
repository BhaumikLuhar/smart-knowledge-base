from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"]
)


@router.get("/")
async def documents_stub():
    return {"message": "Documents router active"}