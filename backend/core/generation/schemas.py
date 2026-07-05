from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal
from uuid import UUID

class Citation(BaseModel):
    """
    Citation returned with a generated answer.
    """

    document_name: str

    page_numbers: list[int] = Field(
        default_factory=list
    )

    section_references: list[str] = Field(
        default_factory=list
    )

    chunk_indexes: list[int] = Field(
        default_factory=list
    )

    department_id: str | None = None

    chunk_excerpt: str


class GeneratorResponse(BaseModel):
    """
    Standard response returned by Generator.
    """

    answer: str

    citations: list[Citation]

    confidence_score: float

    confidence_level: Literal["low", "medium", "high"]

    tokens_used: int

    fallback: bool = False

    model_used: str | None = None


class ChatQueryRequest(BaseModel):
    """
    Incoming chat request.
    """

    message: str = Field(
        min_length=1,
        max_length=5000
    )

    session_id: str | None = None


class ChatQueryResponse(BaseModel):
    """
    Chat endpoint response.
    """

    session_id: str

    answer: str

    citations: list[Citation]

    confidence_score: float

    confidence_level: Literal["low", "medium", "high"]

    tokens_used: int

    fallback: bool

    model_used: str | None = None

    trace: list[dict]


class SessionResponse(BaseModel):

    id: str

    created_at: datetime

    last_active: datetime


class MessageResponse(BaseModel):

    id: str

    role: str

    content: str

    metadata: dict

    created_at: datetime


class PlannerRequest(BaseModel):
    """
    Planner-only request.
    """

    message: str = Field(
        min_length=1,
        max_length=5000,
    )


class PlannerResponse(BaseModel):
    """
    Planner-only response.
    """

    strategy: str

    queries: list[str]

    trace: list[dict]



class SessionListItem(BaseModel):
    """
    Session item displayed in the chat sidebar.
    """

    id: UUID

    created_at: datetime

    last_active: datetime

    last_message_role: str | None = None

    last_message: str | None = None

    last_message_at: datetime | None = None


class SessionListResponse(BaseModel):
    """
    Response returned by GET /chat/sessions.
    """

    sessions: list[SessionListItem]


class SessionMessage(BaseModel):
    """
    Single message inside a chat session.
    """

    id: UUID

    role: str

    content: str

    metadata: dict = Field(
        default_factory=dict
    )

    created_at: datetime


class SessionMessagesResponse(BaseModel):
    """
    Complete conversation history.
    """

    session_id: UUID

    messages: list[SessionMessage]


class CreateSessionResponse(BaseModel):
    """
    Returned when a new chat session is created.
    """

    id: UUID

    created_at: datetime

    last_active: datetime