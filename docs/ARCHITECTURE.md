# Smart Knowledge Bank Architecture

## Overview

Smart Knowledge Bank is a Retrieval-Augmented Knowledge Management platform that allows organizations to upload, process, store, and retrieve internal knowledge documents.

Week 1 establishes the ingestion and retrieval foundation:

* Document upload
* Department organization
* Metadata management
* Document chunking
* Embedding generation
* Vector storage
* Semantic search
* Administrative knowledge base management

---

# High-Level Architecture

```text
┌─────────────────────┐
│      Next.js        │
│      Frontend       │
└──────────┬──────────┘
           │ HTTP
           ▼
┌─────────────────────┐
│      FastAPI        │
│      API Layer      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Knowledge Layer   │
│ Business Services   │
└──────────┬──────────┘
           │
           ├───────────────┐
           │               │
           ▼               ▼
┌─────────────────┐  ┌─────────────────┐
│   SQL Store     │  │  Vector Store   │
│  PostgreSQL     │  │     Chroma      │
└─────────────────┘  └─────────────────┘
```

The application follows a layered architecture where business services never communicate directly with PostgreSQL or Chroma.

All database access is routed through SQLStore.

All vector database access is routed through VectorStore.

---

# Backend Structure

```text
backend/
│
├── core/
│   ├── auth/
│   ├── generation/
│   ├── knowledge/
│   ├── retrieval/
│   ├── permissions/
│   ├── observability/
│   ├── config.py
│   └── database.py
│
├── routers/
│   ├── admin.py
│   ├── auth.py
│   ├── chat.py
│   └── documents.py
│
├── storage/
│   ├── files/
│   ├── sql/
│   ├── vector/
│   └── vector_db/
│
└── scripts/
```

---

# Frontend Structure

```text
frontend/
│
├── app/
│   ├── dashboard/
│   ├── knowledge-base/
│   ├── chat/
│   ├── users/
│   └── settings/
│
├── components/
│   ├── knowledge/
│   ├── ui/
│   └── sidebar.tsx
│
├── services/
├── types/
└── lib/
```

---

# Knowledge Layer

The Knowledge Layer contains all business logic.

Current services:

### KnowledgeService

Responsibilities:

* Validate uploads
* Register documents
* Create document records
* Start ingestion workflow

---

### DepartmentService

Responsibilities:

* Department management
* Department document queries
* Metadata updates
* Soft delete operations

---

### PermissionService

Responsibilities:

* Create permission rules
* Validate department access mappings

---

### FileService

Responsibilities:

* File validation
* Extension validation
* File size validation
* Disk storage
* Filename sanitization

---

# Storage Layer

## SQLStore

Central PostgreSQL abstraction.

Responsibilities:

* Save records
* Query records
* Update records
* Delete records
* Bulk chunk insertion
* Execute raw reporting queries

Application services do not import asyncpg directly.

---

## VectorStore

Central Chroma abstraction.

Responsibilities:

* Save embeddings
* Query embeddings
* Delete vectors
* Count vectors

Application services do not import chromadb directly.

---

# Document Ingestion Pipeline

The ingestion pipeline runs asynchronously through FastAPI BackgroundTasks.

Flow:

1. Admin uploads document
2. FileService saves file to disk
3. Document row created in PostgreSQL
4. Background ingestion task starts
5. Document status changes to processing
6. Appropriate loader parses document text
7. Chunker generates overlapping chunks
8. Chunks inserted into PostgreSQL
9. Embedder generates vector embeddings
10. VectorStore saves embeddings into Chroma
11. Chunk embedding references updated
12. Audit log entry created
13. Document status changes to ready

Failure path:

```text
processing
    ↓
exception
    ↓
failed
```

Failure details are stored in:

```text
documents.metadata.ingestion_error
```

---

# Loader Architecture

Loaders are registered through a central registry.

Current loaders:

* PDF Loader
* DOCX Loader
* TXT Loader
* Markdown Loader

Selection occurs automatically through file extension matching.

---

# Chunking Strategy

Current chunking configuration:

```text
Chunk Size: 800 characters
Overlap: 100 characters
```

Process:

1. Split document into sentences
2. Build chunks until size threshold reached
3. Preserve overlap between chunks
4. Store metadata with each chunk

Stored metadata:

```text
document_id
department_id
visibility
chunk_index
page_number
```

---

# Embedding Architecture

Embedding Model:

```text
BAAI/bge-small-en-v1.5
```

Vector Dimension:

```text
384
```

Implementation:

Singleton pattern.

Benefits:

* Model loaded once
* Reduced memory usage
* Faster inference

Query embeddings use BGE query prefixing:

```text
Represent this sentence for searching relevant passages:
```

---

# Retrieval Architecture

Current retrieval process:

1. User query received
2. Query embedded
3. Chroma vector search executed
4. Department metadata filter applied
5. Top matching chunks returned

Current metadata filters:

```python
{
    "department_id": "<department-id>"
}
```

Future permission enforcement will expand these filters.

---

# Database Schema

## departments

```text
id
name
display_name
description
created_at
```

---

## users

```text
id
email
hashed_password
full_name
role
department_id
created_at
```

---

## documents

```text
id
name
original_filename
file_path
file_type
department_id
visibility
version
status
page_count
uploaded_by
metadata
created_at
updated_at
```

---

## chunks

```text
id
document_id
text
chunk_index
page_number
embedding_ref
department_id
visibility
created_at
```

---

## permissions

```text
id
role
department_id
can_access_department_id
```

---

## sessions

```text
id
user_id
token
expires_at
```

---

## audit_logs

```text
id
user_id
action
resource_type
resource_id
details
ip_address
created_at
```

---

## metrics

```text
id
metric_name
metric_value
created_at
```

---

# Extension Points

## Loader Registry

New document types can be added without modifying ingestion logic.

Example:

```python
register_loader(".xlsx", ExcelLoader())
```

---

## Vector Store Interface

The application communicates only with VectorStore.

Future vector databases can replace Chroma without changing business services.

Potential replacements:

* Pinecone
* Weaviate
* Qdrant
* pgvector

---

# Security Boundaries

Current architecture enforces:

```text
Knowledge Layer
    ↓
Storage Layer
    ↓
Database
```

Forbidden:

```text
core/knowledge → asyncpg
core/knowledge → chromadb

core/retrieval → asyncpg
core/retrieval → chromadb
```

All persistence operations must pass through storage abstractions.

---

# Current Week 1 Capabilities

Implemented:

* Department management
* Document upload
* Metadata storage
* Background ingestion
* Loader registry
* Chunk generation
* PostgreSQL chunk storage
* Embedding generation
* Chroma persistence
* Semantic search
* Department-level filtering
* Administrative knowledge base UI
* Status polling
* Audit logging

Week 2 will introduce:

* Authentication
* Permission-aware retrieval
* Access control enforcement
* User session management
* Protected chat retrieval




## Retrieval Pipeline

The Retrieval Pipeline provides a centralized orchestration layer for knowledge retrieval.

```text
User Query
      │
      ▼
Hybrid Retriever
      │
      ▼
Permission Filter
      │
      ▼
Reranker (Day 12)
      │
      ▼
Top-K Selection
      │
      ▼
Audit Logging
      │
      ▼
Retrieved Context
```


---

## Generation Layer

Day 13 introduces the generation layer responsible for producing grounded responses from authorized retrieval results.

```text
Client
│
▼
Chat Router
│
▼
ChatService
│
├───────────────┐
▼               ▼
SessionService  RetrievalPipeline
│
▼
Generator
│
┌───────────────┴───────────────┐
▼                               ▼
Citation Builder            LLM Provider
│
▼
Groq Provider
```

### Responsibilities

#### ChatService

Coordinates the complete RAG request lifecycle:

- Session management
- Message persistence
- Retrieval execution
- Response generation
- Metrics recording

#### SessionService

Manages conversation sessions and validates ownership.

#### Generator

Builds grounded prompts, invokes the LLM provider, computes response confidence, and returns structured responses.

#### Citation Builder

Aggregates document citations and removes duplicate document references.

#### LLM Provider

Defines the provider abstraction.

**Current implementation:**

- Groq (OpenAI-compatible API)

Future providers can be added without changing the generation pipeline.