from pydantic import BaseModel, Field
from datetime import datetime

class Citation(BaseModel):
    """
    Citation returned with a generated answer.
    """

    document_name: str

    page_numbers: list[int] = Field(
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

    confidence: float

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

    confidence: float

    tokens_used: int

    fallback: bool

    model_used: str | None = None


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