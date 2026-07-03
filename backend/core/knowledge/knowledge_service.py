from pathlib import Path

from fastapi import BackgroundTasks, HTTPException, UploadFile
from core.knowledge.ingestion_service import (
    ingest_document
)
from core.knowledge.file_service import FileService
from storage.sql.sql_store import SQLStore

import time

from core.observability.collector import (
    ObservabilityCollector,
)

class KnowledgeService:
    """
    Handles document registration.

    Day 3:
    Upload -> Save File -> Register Document

    Day 5:
    Ingestion pipeline will be added.
    """

    def __init__(self, sql_store: SQLStore):
        self.sql_store = sql_store
        self.metrics = ObservabilityCollector(
            sql_store
        )
    
    

    async def create_document(
            self,
            upload_file: UploadFile,
            department_id: str,
            visibility: str,
            uploaded_by_user_id: str | None,
            background_tasks: BackgroundTasks,
            metadata: dict | None = None
    )-> dict:
        """
        Save file and register document.
        """
        start = time.perf_counter()
        try:
            metadata = metadata or {}

            departments= await self.sql_store.query(
                "departments",
                {"id": department_id}
            )

            if not departments:
                raise HTTPException(
                    status_code=404,
                    detail="Department not found"
                )
            
            department=departments[0]

            department_name=department["name"]

            file_path=await FileService.save_file(upload_file, department_name)

            document = await self.sql_store.save(
                "documents",
                {
                    "name": Path(
                        upload_file.filename
                    ).stem,

                    "original_filename":
                        upload_file.filename,

                    "file_path":
                        file_path,

                    "file_type":
                        Path(
                            upload_file.filename
                        ).suffix.lower().replace(".", ""),

                    "department_id":
                        department_id,

                    "visibility":
                        visibility,

                    "uploaded_by":
                        uploaded_by_user_id,

                    "metadata":
                        metadata,

                }
            )

            #
            # Audit log
            #
            await self.sql_store.save(
                "audit_logs",
                {
                    "user_id": uploaded_by_user_id,
                    "action": "document_uploaded",
                    "resource_type": "document",
                    "resource_id": str(document["id"]),
                    "details": {
                        "document_name": document["name"],
                        "original_filename": document["original_filename"],
                        "department_id": department_id,
                        "visibility": visibility,
                    },
                },
            )

            background_tasks.add_task(
                ingest_document,
                document["id"],
                self.sql_store
            )

            latency = (
                time.perf_counter() - start
            ) * 1000

            await self.metrics.record_success(
                endpoint="/api/v1/admin/documents",
                user_id=uploaded_by_user_id,
                latency=latency,
            )
            return document
        
        except Exception as e:
            latency = (
                time.perf_counter() - start
            ) * 1000

            await self.metrics.record_failure(
                endpoint="/api/v1/admin/documents",
                user_id=uploaded_by_user_id,
                latency=latency,
                error_message=str(e),
            )

            raise