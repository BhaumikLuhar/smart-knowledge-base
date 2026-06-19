from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    UploadFile
)

from core.knowledge.admin_auth import (
    verify_admin_token
)
from core.knowledge.knowledge_service import (
    KnowledgeService
)
from storage.sql.dependencies import (
    get_sql_store
)
from storage.sql.sql_store import SQLStore

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"]
)

@router.post("/documents", dependencies=[Depends(verify_admin_token)])
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    department_id: str = Form(...),
    visibility: str = Form("department"),
    description: str | None = Form(None),
    sql_store: SQLStore = Depends(get_sql_store)
):
    
    service = KnowledgeService(sql_store)

    document= await service.create_document(
        upload_file=file,
        department_id=department_id,
        visibility=visibility,
        uploaded_by_user_id=None,  # Admin upload, no user ID
        background_tasks=background_tasks,
        metadata={
            "description": description
        }
    )

    return {
        "id": document["id"],
        "name": document["name"],
        "status": document["status"],
        "department_id":
            document["department_id"],
        "created_at":
            document["created_at"]
    }


@router.get("/documents", dependencies=[Depends(verify_admin_token)])
async def list_documents(
    sql_store: SQLStore = Depends(get_sql_store)
):
    
    documents = await sql_store.execute_raw(
        """
        SELECT d.*,
        dep.name AS department_name,
        dep.display_name AS department_display_name
        FROM documents d
        LEFT JOIN departments dep
            ON dep.id = d.department_id
        ORDER BY d.created_at DESC
        """
    )

    return documents


@router.get(
    "/documents/{document_id}",
    dependencies=[
        Depends(verify_admin_token)
    ]
)
async def get_document(
    document_id: str,
    sql_store: SQLStore = Depends(
        get_sql_store
    )
):
    result = await sql_store.execute_raw(
        """
        SELECT
            d.*,
            dep.name AS department_name,
            dep.display_name
                AS department_display_name
        FROM documents d
        LEFT JOIN departments dep
            ON dep.id = d.department_id
        WHERE d.id = $1
        """,
        (document_id,)
    )

    if not result:
        return {
            "detail":
            "Document not found"
        }

    return result[0]