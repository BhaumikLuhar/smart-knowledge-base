from chromadb import PersistentClient
from chromadb.config import Settings as ChromaSettings

from core.config import settings


class VectorStore:
    """
    Singleton Chroma wrapper.

    Handles:
    - saving embeddings
    - querying embeddings
    - deleting document vectors

    Uses persistent Chroma storage.
    """

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    

    def __init__(self):
        if(hasattr(self, "collection")):
            return
        
        print(
            f"Initializing Chroma DB at: "
            f"{settings.CHROMA_PATH}"
        )

        self.client = PersistentClient(
            path=settings.CHROMA_PATH,
            settings=ChromaSettings(
                anonymized_telemetry=False
            )
        )

        self.collection = (
            self.client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION,
                metadata={"hnsw:space": "cosine"}
            )
        )

        print(
            f"Chroma collection ready: "
            f"{settings.CHROMA_COLLECTION}"
        )


    def save(
            self,
            ids: list[str],
            embeddings: list[list[float]],
            documents: list[str],
            metadatas: list[dict]
    ):
        """
        Save vectors into Chroma.

        Chroma recommends batching.
        """

        if not ids:
            return 
        
        batch_size=500

        for i in range(0,len(ids), batch_size):
            self.collection.add(
                ids=ids[i:i+batch_size],
                embeddings=embeddings[i:i+batch_size],
                documents=documents[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size]
            )


    def query(
            self,
            query_embedding: list[float],
            top_k: int,
            where: dict | None = None
    )-> dict:
        """
        Vector search.
        """

        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )
    

    def delete_by_document(self, document_id: str):
        """
        Future hard-delete support.
        """


        self.collection.delete(
            where={"document_id": document_id}
        )

    
    def count(self) -> int:
        """
        Useful for testing.
        """

        return self.collection.count()