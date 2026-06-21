import re
from fastapi import HTTPException
from storage.sql.sql_store import SQLStore

class DepartmentService:

    def __init__(self, sql_store: SQLStore):
        self.sql_store = sql_store

    
    async def list_departments(self)->list[dict]:
        """
        Return all departments
        with document counts.
        """

        query = """
        SELECT 
            d.*,
            COUNT(doc.id) AS document_count
        FROM departments d
        LEFT JOIN documents doc
            ON doc.department_id = d.id
        GROUP BY d.id
        ORDER BY d.display_name;
        """

        return await self.sql_store.execute_raw(query)
    

    async def get_department(self, department_id: str)-> dict:
        """
        Get department by id.
        """

        departments = await self.sql_store.query(
            "departments",
            {"id": department_id}
        )

        if not departments:
            raise HTTPException(
                status_code=404,
                detail="Department not found"
            )

        return departments[0]
    

    async def create_department(self, name: str, display_name: str, description: str | None=None)->dict:
        """
        Department names must be:

        engineering
        human_resources
        finance

        lowercase only.
        """

        if not re.match(r"^[a-z0-9_]+$",name):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Department name must contain "
                    "only lowercase letters, "
                    "numbers and underscores."
                )
            )
        
        existing = await self.sql_store.query(
            "departments",
            {
                "name": name
            }
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Department already exists"
            )
        
        return await self.sql_store.save(
            "departments",
            {
                "name": name,
                "display_name": display_name,
                "description": description
            }
        )
    

    async def update_document_metadata(self, document_id: str, metadata: dict, visibility: str)->dict:
        """
        Update metadata JSONB
        and visibility.
        """

        return await self.sql_store.update(
            "documents",
            document_id,
            {
                "metadata": metadata,
                "visibility": visibility,
                "updated_at": "NOW()"
            }
        )


    async def update_document(
        self,
        document_id: str,
        department_id: str,
        visibility: str,
        metadata: dict
    ) -> dict:

        document = await self.sql_store.query(
            "documents",
            {"id": document_id}
        )

        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )

        department = await self.sql_store.query(
            "departments",
            {"id": department_id}
        )

        if not department:
            raise HTTPException(
                status_code=404,
                detail="Department not found"
            )

        return await self.sql_store.update(
            "documents",
            document_id,
            {
                "department_id": department_id,
                "visibility": visibility,
                "metadata": metadata,
                "updated_at": "NOW()"
            }
        )
    

    async def soft_delete_document(
        self,
        document_id: str
    ) -> dict:

        document = await self.sql_store.query(
            "documents",
            {"id": document_id}
        )

        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )

        return await self.sql_store.update(
            "documents",
            document_id,
            {
                "status": "deleted",
                "updated_at": "NOW()"
            }
        )