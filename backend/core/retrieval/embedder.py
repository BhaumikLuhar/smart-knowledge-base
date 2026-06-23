from sentence_transformers import SentenceTransformer

class Embedder:
    """
    Singleton wrapper around BAAI/bge-small-en-v1.5.

    Why singleton?

    Loading the model takes several seconds and
    ~130MB memory.

    We load it once at startup and reuse it
    throughout the application.
    """


    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    

    def __init__(self):
        if(hasattr(self, "model")):
            return
        
        print(
            "Loading embedding model: "
            "BAAI/bge-small-en-v1.5 ..."
        )

        self.model = SentenceTransformer(
            "BAAI/bge-small-en-v1.5"
        )

        self.dimension = 384

        print(
            "Embedding model loaded "
            f"(dimension={self.dimension})"
        )

    
    def embed(self, texts:list[str])->list[list[float]]:
        """
        Generate embeddings for document chunks.
        """

        if not texts:
            return []
        
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True
        )

        return embeddings.tolist()
    

    def embed_query(
        self,
        query: str
    ) -> list[float]:
        """
        Generate embedding for retrieval query.

        BGE models recommend a query prefix.
        """

        prefixed_query = (
            "Represent this sentence "
            "for searching relevant passages: "
            f"{query}"
        )

        embedding = self.model.encode(
            [prefixed_query],
            normalize_embeddings=True
        )

        return embedding[0].tolist()