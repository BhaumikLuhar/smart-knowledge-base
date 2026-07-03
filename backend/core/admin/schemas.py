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