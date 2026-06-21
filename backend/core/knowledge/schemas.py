from pydantic import BaseModel, Field, ConfigDict

class DocumentMetadata(BaseModel):
    """
    Structured metadata stored inside
    documents.metadata JSONB.
    """
    model_config = ConfigDict(
        extra="forbid"
    )

    description: str = ""

    tags: list[str] = Field(default_factory=list)

    author: str = ""

    effective_date: str = ""

    expiry_date: str= ""

    custom: dict = Field(default_factory=dict)


class CreateDepartmentRequest(BaseModel):
    name: str
    display_name: str
    description: str | None = None


class UpdateDocumentRequest(BaseModel):
    department_id: str
    visibility: str
    metadata: DocumentMetadata


class CreatePermissionRequest(BaseModel):
    role: str
    department_id: str
    can_access_department_id: str