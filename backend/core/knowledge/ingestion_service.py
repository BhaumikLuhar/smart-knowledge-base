from importlib import metadata
import json
import logging
from pathlib import Path
from core.knowledge.chunker import chunk_text
from core.knowledge.loaders.factory import get_loader
from storage.sql.sql_store import SQLStore

logger = logging.getLogger(__name__)


async def ingest_document(
    document_id: str,
    sql_store: SQLStore
):
    """
    Day 5 ingestion pipeline.

    Flow:
        pending
            ↓
        processing
            ↓
        parse
            ↓
        chunk
            ↓
        save chunks
            ↓
        ready
    """

    try:

        #
        # STEP 1
        # Fetch document
        #
        documents = await sql_store.query(
            "documents",
            {
                "id": document_id
            }
        )

        if not documents:
            logger.error(
                f"Document not found: {document_id}"
            )
            return

        document = documents[0]

        #
        # STEP 2
        # processing
        #
        await sql_store.update(
            "documents",
            document_id,
            {
                "status": "processing",
                "updated_at": "NOW()"
            }
        )

        #
        # STEP 3
        # load text
        #

        file_path = Path(
            document["file_path"]
        )

        if not file_path.is_absolute():
            file_path = (
                Path.cwd().parent
                / file_path
            )

        loader = get_loader(
            str(file_path)
        )

        text = loader.load(
            str(file_path)
        )

        #
        # STEP 4
        # validate text
        #
        if not text or len(text.strip()) < 50:

            error_message = (
                "Document produced no "
                "extractable text "
                "(possibly image-only PDF)"
            )

            metadata = (
                document.get("metadata")
                or {}
            )

            metadata[
                "ingestion_error"
            ] = error_message

            await sql_store.update(
                "documents",
                document_id,
                {
                    "status": "failed",
                    "metadata": metadata,
                    "updated_at": "NOW()"
                }
            )

            logger.warning(
                error_message
            )

            return

        #
        # STEP 5
        # chunking
        #
        chunks = chunk_text(
            text=text,
            doc_id=document_id,
            dept_id=document[
                "department_id"
            ],
            visibility=document[
                "visibility"
            ]
        )

        #
        # STEP 6
        # bulk insert
        #
        inserted_count = (
            await sql_store.bulk_insert_chunks(
                chunks
            )
        )

        logger.info(
            f"Inserted "
            f"{inserted_count} chunks "
            f"for document "
            f"{document_id}"
        )

        #
        # STEP 7
        # audit log
        #
        await sql_store.save(
            "audit_logs",
            {
                "user_id":
                    document.get(
                        "uploaded_by"
                    ),
                "action":
                    "document_ingested",
                "resource_type":
                    "document",
                "resource_id":
                    document_id,
                "details":
                {
                    "chunk_count":
                        inserted_count,
                    "page_count":
                        getattr(
                            loader,
                            "page_count",
                            None
                        )
                }
            }
        )

        #
        # STEP 8
        # mark ready
        #
        await sql_store.update(
            "documents",
            document_id,
            {
                "status": "ready",
                "page_count":
                    getattr(
                        loader,
                        "page_count",
                        None
                    ),
                "updated_at":
                    "NOW()"
            }
        )

        logger.info(
            f"Document ready: "
            f"{document_id}"
        )

    except Exception as e:

        logger.exception(
            f"Ingestion failed "
            f"for {document_id}"
        )

        try:

            documents = (
                await sql_store.query(
                    "documents",
                    {
                        "id":
                            document_id
                    }
                )
            )

            if documents:

                metadata = (
                    documents[0].get(
                        "metadata"
                    )
                    or {}
                )

                metadata = metadata if isinstance(metadata, dict) else {}
                metadata["ingestion_error"] = str(e)

                await sql_store.update(
                    "documents",
                    document_id,
                    {
                        "status":
                            "failed",
                        "metadata":
                            metadata,
                        "updated_at":
                            "NOW()"
                    }
                )

        except Exception:

            logger.exception(
                "Failed updating "
                "document status"
            )