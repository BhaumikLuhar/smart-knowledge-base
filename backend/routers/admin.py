from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    UploadFile
)
from core.knowledge.permission_service import (
    PermissionService
)

from core.auth.dependencies import (
    require_admin
)

from core.auth.user_context import (
    UserContext
)

from core.auth.user_service import (
    UserService
)

from core.auth.schemas import (
    CreateUserRequest,
    UpdateUserRequest
)

from core.knowledge.knowledge_service import (
    KnowledgeService
)
from storage.sql.dependencies import (
    get_sql_store
)
from storage.sql.sql_store import SQLStore
from core.knowledge.department_service import (
    DepartmentService
)

from core.knowledge.schemas import (
    CreateDepartmentRequest, UpdateDocumentRequest, CreatePermissionRequest
)

from fastapi import HTTPException

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"]
)

@router.post("/documents")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    department_id: str = Form(...),
    visibility: str = Form("department"),
    description: str | None = Form(None),
    sql_store: SQLStore = Depends(get_sql_store),current_user: UserContext = Depends(
        require_admin
    )
):
    
    service = KnowledgeService(sql_store)

    document= await service.create_document(
        upload_file=file,
        department_id=department_id,
        visibility=visibility,
        uploaded_by_user_id=current_user.id,
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


@router.get("/documents")
async def list_documents(
    sql_store: SQLStore = Depends(get_sql_store),
    current_user: UserContext = Depends(
        require_admin
    )
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
    "/documents/{document_id}"
)
async def get_document(
    document_id: str,
    sql_store: SQLStore = Depends(
        get_sql_store
    ),
    current_user: UserContext = Depends(
        require_admin
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



@router.get(
    "/departments"
)
async def list_departments(
    sql_store: SQLStore = Depends(
        get_sql_store
    ),
    current_user: UserContext = Depends(
        require_admin
    )
):
    service = DepartmentService(sql_store)

    return await service.list_departments()


@router.post(
    "/departments"
)
async def create_department(
    payload: CreateDepartmentRequest,
    sql_store: SQLStore = Depends(
        get_sql_store
    ),
    current_user: UserContext = Depends(
        require_admin
    )
):
    service = DepartmentService(
        sql_store
    )

    department = await service.create_department(
        name=payload.name,
        display_name=payload.display_name,
        description=payload.description
    )

    return department


@router.get(
    "/departments/{department_id}/documents"
)
async def get_department_documents(
    department_id: str,
    sql_store: SQLStore = Depends(
        get_sql_store
    ),
    current_user: UserContext = Depends(
        require_admin
    )
):
    service = DepartmentService(
        sql_store
    )

    await service.get_department(
        department_id
    )

    documents = await sql_store.execute_raw(
        """
        SELECT
            *
        FROM documents
        WHERE department_id = $1
        ORDER BY created_at DESC
        """,
        (department_id,)
    )

    return documents


@router.put(
    "/documents/{document_id}"
)
async def update_document(
    document_id: str,
    payload: UpdateDocumentRequest,
    sql_store: SQLStore = Depends(
        get_sql_store
    ),
    current_user: UserContext = Depends(
        require_admin
    )
):
    service = DepartmentService(
        sql_store
    )

    document = await service.update_document(
        document_id=document_id,
        department_id=payload.department_id,
        visibility=payload.visibility,
        metadata=payload.metadata.model_dump()
    )

    return document


@router.delete(
    "/documents/{document_id}"
)
async def delete_document(
    document_id: str,
    sql_store: SQLStore = Depends(
        get_sql_store
    ),
    current_user: UserContext = Depends(
        require_admin
    )
):
    service = DepartmentService(
        sql_store
    )

    document = await service.soft_delete_document(
        document_id
    )

    return {
        "message": "Document deleted",
        "document": document
    }


@router.post(
    "/permissions"
)
async def create_permission(
    payload: CreatePermissionRequest,
    sql_store: SQLStore = Depends(
        get_sql_store
    ),
    current_user: UserContext = Depends(
        require_admin
    )
):
    service = PermissionService(
        sql_store
    )

    permission = await service.create_permission(
        role=payload.role,
        department_id=payload.department_id,
        can_access_department_id=
            payload.can_access_department_id
    )

    return permission



@router.get("/users")
async def list_users(
    current_user: UserContext = Depends(
        require_admin
    ),
    sql_store: SQLStore = Depends(
        get_sql_store
    )
):

    service = UserService(
        sql_store
    )

    return await service.list_users()



@router.post("/users")
async def create_user(
    payload: CreateUserRequest,
    current_user: UserContext = Depends(
        require_admin
    ),
    sql_store: SQLStore = Depends(
        get_sql_store
    )
):

    service = UserService(
        sql_store
    )

    return await service.create_user(
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
        department_id=payload.department_id,
        role=payload.role
    )



@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    payload: UpdateUserRequest,
    current_user: UserContext = Depends(
        require_admin
    ),
    sql_store: SQLStore = Depends(
        get_sql_store
    )
):

    service = UserService(
        sql_store
    )

    return await service.update_user(
        user_id=user_id,
        role=payload.role,
        department_id=payload.department_id,
        is_active=payload.is_active
    )