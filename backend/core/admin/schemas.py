from datetime import datetime

from pydantic import BaseModel, Field

from evaluation.schemas import EvaluationReport


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


class DepartmentQueryBreakdown(BaseModel):
    """
    Query volume grouped by department.
    """

    department: str

    query_count: int

    percentage: float


class HourlyQueryBucket(BaseModel):
    """
    Number of chat queries for each hour
    of the current day.
    """

    hour: int

    query_count: int


class DashboardSummaryResponse(BaseModel):
    """
    Complete dashboard summary returned to
    the admin observability dashboard.
    """

    #
    # Usage metrics
    #
    total_queries_today: int

    today_errors: int

    average_latency_ms: int

    average_tokens: int

    #
    # Knowledge Base
    #
    total_documents: int

    documents_ready: int

    #
    # User activity
    #
    active_users: int

    permission_denials_today: int

    #
    # Retrieval quality
    #
    retrieval_precision_avg: float

    #
    # Dashboard visualizations
    #
    department_breakdown: list[
        DepartmentQueryBreakdown
    ] = Field(default_factory=list)

    hourly_query_volume: list[
        HourlyQueryBucket
    ] = Field(default_factory=list)

    #
    # Recent activity
    #
    recent_queries: list[
        RecentQuerySummary
    ] = Field(default_factory=list)



class SystemConfigResponse(BaseModel):
    chunk_size: int
    chunk_overlap: int
    candidate_top_k: int
    final_top_k: int
    max_sessions: int




class EvaluationRunResponse(BaseModel):

    job_id: str

    status: str


class EvaluationResultsResponse(BaseModel):

    status: str

    results: EvaluationReport | None