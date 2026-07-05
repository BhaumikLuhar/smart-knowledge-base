from fastapi import APIRouter
from fastapi import Depends
from uuid import UUID

from core.auth.dependencies import (
    get_current_user,
)

from core.auth.user_context import (
    UserContext,
)

from core.chat.chat_service import (
    ChatService,
)

from core.chat.session_service import (
    SessionService,
)

from core.generation.schemas import (
    ChatQueryRequest,
    ChatQueryResponse,
    PlannerRequest,
    PlannerResponse,
    SessionListResponse,
    SessionMessagesResponse,
    CreateSessionResponse,
)

from agents.planner.planner_service import PlannerService

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


@router.post(
    "/plan",
    response_model=PlannerResponse,
)
async def plan(
    payload: PlannerRequest,
    current_user: UserContext = Depends(
        get_current_user
    ),
):
    """
    Execute only the Planner agent.

    Useful for debugging and verifying
    planning decisions independently
    from retrieval and generation.
    """

    service = PlannerService()

    state = await service.plan(
        query=payload.message,
        user_context=current_user,
    )

    return PlannerResponse(
        strategy=state["retrieval_strategy"],
        queries=state["search_queries"],
        trace=state["trace"],
    )


@router.post(
    "/sessions",
    response_model=CreateSessionResponse,
)
async def create_session(
    sql_store: SQLStore = Depends(
        get_sql_store,
    ),
    current_user: UserContext = Depends(
        get_current_user,
    ),
):
    """
    Create a new empty chat session.

    Used by the frontend "New Chat" button.
    """

    service = SessionService(sql_store)

    session = await service.create_session(
        current_user.id,
    )

    return CreateSessionResponse(
        id=session["id"],
        created_at=session["created_at"],
        last_active=session["last_active"],
    )



@router.get(
    "/sessions",
    response_model=SessionListResponse,
)
async def list_sessions(
    sql_store: SQLStore = Depends(
        get_sql_store,
    ),
    current_user: UserContext = Depends(
        get_current_user,
    ),
):
    """
    Return all sessions belonging
    to the authenticated user.
    """

    service = SessionService(sql_store)

    sessions = await service.list_sessions(
        current_user.id,
    )

    return SessionListResponse(
        sessions=sessions,
    )



@router.get(
    "/sessions/{session_id}/messages",
    response_model=SessionMessagesResponse,
)
async def get_session_messages(
    session_id: str,
    sql_store: SQLStore = Depends(
        get_sql_store,
    ),
    current_user: UserContext = Depends(
        get_current_user,
    ),
):
    """
    Return the complete conversation
    history for one chat session.
    """

    service = SessionService(sql_store)

    messages = await service.get_session_messages(
        session_id=session_id,
        user_id=current_user.id,
    )

    return SessionMessagesResponse(
        session_id=UUID(session_id),
        messages=messages,
    )