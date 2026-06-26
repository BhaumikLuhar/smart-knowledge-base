from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from routers.admin import router as admin_router
from routers.auth import router as auth_router
from routers.chat import router as chat_router
from routers.documents import router as documents_router
from routers.user import router as user_router

from core.config import settings
from core.database import create_db_pool, close_db_pool

from core.retrieval.embedder import Embedder
from core.retrieval.cross_encoder_reranker import CrossEncoderReranker
from storage.vector.vector_store import VectorStore

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup
    """
    app.state.db_pool = await create_db_pool()
    print("✅ PostgreSQL connection pool initialized")

    #
    # Day 6
    # Preload embedding model
    #
    Embedder.get_instance()
    print("✅ Embedder initialized")

    #
    # Day 6
    # Preload Chroma
    #
    VectorStore.get_instance()
    print("✅ Chroma initialized")

    #
    # Day 12
    # Preload CrossEncoder reranker
    #
    if settings.RERANKER_TYPE == "cross_encoder":
        CrossEncoderReranker.get_instance()
        print("✅ CrossEncoder reranker initialized")

    yield

    """
    Shutdown
    """
    await close_db_pool(app.state.db_pool)
    print("✅ PostgreSQL connection pool closed")


app=FastAPI(
    title="smart-knowledge-bank",
    version="1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "1.0"
    }

app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(user_router)