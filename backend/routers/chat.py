from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1/chat",
    tags=["Chat"]
)


@router.get("/")
async def chat_stub():
    return {"message": "Chat router active"}