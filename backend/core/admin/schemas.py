from datetime import datetime

from pydantic import BaseModel, Field


class AuditLogEntry(BaseModel):
    """
    One audit log entry returned to the admin dashboard.
    """

    id: str

    user_id: str | None = None

    user_email: str | None = None

    action: str

    resource_type: str | None = None

    resource_id: str | None = None

    details: dict = Field(default_factory=dict)

    ip_address: str | None = None

    created_at: datetime


class AuditLogResponse(BaseModel):
    """
    Paginated audit log response.
    """

    total: int

    limit: int

    offset: int

    items: list[AuditLogEntry]



class RecentQuerySummary(BaseModel):
    user: str
    query: str
    timestamp: datetime
    confidence: str


class DashboardSummaryResponse(BaseModel):
    total_queries_today: int
    average_latency_ms: int
    active_users: int
    documents_ready: int
    recent_queries: list[RecentQuerySummary]



class SystemConfigResponse(BaseModel):
    chunk_size: int
    chunk_overlap: int
    candidate_top_k: int
    final_top_k: int
    max_sessions: int