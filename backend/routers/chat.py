from fastapi import APIRouter
from fastapi import Depends

from core.auth.dependencies import (
    get_current_user,
)

from core.auth.user_context import (
    UserContext,
)

from core.chat.chat_service import (
    ChatService,
)

from core.generation.schemas import (
    ChatQueryRequest,
    ChatQueryResponse,
)

from storage.sql.dependencies import (
    get_sql_store,
)

from storage.sql.sql_store import (
    SQLStore,
)


router = APIRouter(
    prefix="/api/v1/chat",
    tags=["Chat"],
)


@router.post(
    "/query",
    response_model=ChatQueryResponse,
)
async def query(
    payload: ChatQueryRequest,
    sql_store: SQLStore = Depends(get_sql_store),
    current_user: UserContext = Depends(
        get_current_user
    ),
):
    """
    Execute a grounded RAG query.

    Authentication is required.

    The endpoint:

    - Creates or reuses a chat session
    - Retrieves authorized knowledge
    - Generates a grounded response
    - Stores conversation history
    - Records observability metrics
    """

    service = ChatService(sql_store)

    return await service.query(
        message=payload.message,
        session_id=payload.session_id,
        current_user=current_user,
    )