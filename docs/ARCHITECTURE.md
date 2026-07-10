# Smart Knowledge Bank Architecture

## Overview

Smart Knowledge Bank is a department-aware, Retrieval-Augmented knowledge intelligence platform that allows organizations to upload, process, store, and retrieve internal knowledge documents through a permission-aware, multi-agent workflow.

The system has evolved from a Week 1 ingestion/retrieval foundation into a full multi-agent AI platform. See [Architectural Evolution](#architectural-evolution) at the end of this document for the complete progression.

---

# Architectural Principles

The Smart Knowledge Bank is designed around several core software engineering principles.

- **Separation of Concerns** – Business logic, retrieval, storage, and presentation are isolated into independent layers.
- **Defense in Depth** – Multiple authorization layers prevent unauthorized information from reaching the language model.
- **Open for Extension** – Registry-based architecture allows new components to be added without modifying existing implementations.
- **Provider Abstraction** – Storage systems, language models, and retrieval components are abstracted behind interfaces to support future replacements.
- **Explainability First** – Every response includes supporting evidence, citations, confidence metrics, and reasoning traces.
- **Performance-Oriented Design** – Multi-level caching, asynchronous execution, and fine-grained profiling minimize latency while preserving retrieval quality.

---

# High-Level Architecture

```text
                                      Smart Knowledge Bank

┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    Next.js Frontend                                         │
│                                                                                             │
│ Login │ Dashboard │ Knowledge Base │ Chat │ Users │ Audit Logs │ Settings                   │
└───────────────────────────────────────┬─────────────────────────────────────────────────────┘
                                        │
                                  REST API (/api/v1)
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                      FastAPI Backend                                        │
└───────────────────────────────────────┬─────────────────────────────────────────────────────┘
                                        │
                ┌───────────────────────┼───────────────────────────┐
                │                       │                           │
                ▼                       ▼                           ▼
        Authentication            Admin Services              Chat Service
                │                       │                           │
                └───────────────────────┼───────────────────────────┘
                                        │
                                        ▼
                             Conversation Processing Layer
                                        │
                        Session Memory + Query Resolver
                                        │
                                        ▼
                           LangGraph Multi-Agent Workflow
                                        │
          ┌─────────────────────────────┼─────────────────────────────┐
          ▼                             ▼                             ▼
   Planner Agent                 Research Agent               Response Agent
          │                             │                             │
          └─────────────────────────────┼─────────────────────────────┘
                                        ▼
                             Permission-Aware Retrieval Pipeline
                                        │
     Pipeline Cache → Hybrid Search → Permission Filter → Reranker → Quality Gate
                                        │
                                        ▼
                   PostgreSQL + Chroma Vector Database + File Storage
                                        │
                                        ▼
                                 Groq Language Model
                                        │
                                        ▼
                Grounded Response + Citations + Confidence + Reasoning Trace
```

This diagram mirrors the canonical System Architecture diagram in `README.md`.

The application follows a layered architecture where business services never communicate directly with PostgreSQL or Chroma.

All database access is routed through SQLStore.

All vector database access is routed through VectorStore.

---

# Request Lifecycle

The end-to-end path of a single chat request through every architectural layer:

```text
User
  │
  ▼
JWT Authentication
  │
  ▼
Router
  │
  ▼
Service
  │
  ▼
Conversation Layer
  │
  ▼
Planner
  │
  ▼
Research
  │
  ▼
Retrieval
  │
  ▼
Generator
  │
  ▼
Persistence
  │
  ▼
Frontend
```

---

# Backend Structure

```text
backend/
│
├── core/
│   ├── auth/
│   ├── cache/
│   ├── conversation/
│   ├── evaluation/
│   ├── generation/
│   ├── knowledge/
│   ├── memory/
│   ├── observability/
│   ├── permissions/
│   ├── profiling/
│   ├── retrieval/
│   ├── config.py
│   └── database.py
│
├── agents/
│   ├── planner_agent.py
│   ├── research_agent.py
│   ├── response_agent.py
│   ├── registry.py
│   └── workflow.py
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
│   ├── audit/
│   └── settings/
│
├── components/
│   ├── knowledge/
│   ├── ui/
│   └── sidebar.tsx
│
├── contexts/
├── hooks/
├── services/
├── types/
└── lib/
```

---

# Conversation Layer

The Conversation Layer prepares user input before agent execution.

Components:

- SessionService
- Session Memory
- Query Resolver

Responsibilities:

- Load recent messages
- Maintain conversational context
- Rewrite follow-up questions
- Produce resolved retrieval query

---

# Agent Workflow

The complete chat workflow combines conversational memory, LangGraph orchestration, permission-aware retrieval, and grounded response generation.

```text
Client
   │
   ▼
Chat UI
   │
   ▼
Chat Router
   │
   ▼
ChatService
   │
   ▼
SessionService
(load history)
   │
   ▼
Conversation Resolver
(resolve retrieval query)
   │
   ▼
run_agent_pipeline()
   │
   ▼
Planner Agent
   │
   ▼
Research Agent
   │
   ▼
Response Agent
   │
   ▼
Generator
   │
   ▼
Groq Provider
   │
   ▼
Citation Builder
   │
   ▼
Confidence Layer
   │
   ▼
Reasoning Trace
   │
   ▼
Structured Response
```

Shared `AgentState` contains:

- original query
- resolved query
- conversation history
- retrieval strategy
- search queries
- retrieved chunks
- citations
- confidence score
- confidence level
- reasoning trace

### Agent Responsibilities

#### Planner Agent

- Analyzes the request
- Determines retrieval strategy
- Generates optimized search queries

#### Research Agent

- Executes permission-aware retrieval
- Aggregates and deduplicates retrieved chunks
- Preserves retrieval trace

#### Response Agent

- Generates grounded responses
- Builds citations
- Computes confidence
- Records execution trace

### Parallel Research Execution

Planner-generated search queries execute retrieval simultaneously before results are merged and deduplicated.

```text
            Planner
               │
               ▼
      ┌────────┬────────┬────────┐
      ▼        ▼        ▼
   Query 1   Query 2   Query 3
      │        │        │
      └────────┴────────┴────────┘
                 │
                 ▼
        Merge + Deduplicate
```

---

# Retrieval Architecture

The Research Agent delegates to a centralized Retrieval Pipeline that resolves queries into authorized, reranked context.

```text
User Query
      │
      ▼
Pipeline Cache
      │
      ▼
Hybrid Retrieval
      │
      ▼
Chroma Metadata Filter
      │
      ▼
Application Permission Validation
      │
      ▼
Cross-Encoder Reranker
      │
      ▼
Retrieval Quality Gate
      │
      ▼
Generator
```

Hybrid retrieval combines both search strategies using a fixed weighting:

```text
Vector Search (70%) + BM25 Search (30%)
```

Reranking is performed using:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

Current metadata filters:

```python
{
    "department_id": "<department-id>"
}
```

Current metadata filtering enforces both:

- Department permissions
- Document visibility

before retrieval. Application-level permission validation provides a second authorization layer before reranking, and the resulting audit log entry provides a third.

### RetrievalPipeline Responsibilities

- Hybrid retrieval
- Metadata filtering
- Secondary permission validation
- Cross-encoder reranking
- Retrieval quality validation
- Audit logging

The pipeline guarantees that only authorized and sufficiently relevant context reaches the Generator.

---

# Generation Layer

Responsible for producing grounded, permission-aware responses from authorized retrieval results.

```text
Authorized Retrieval Context
              │
              ▼
          Generator
              │
    ┌─────────┴─────────┐
    ▼                   ▼
Citation Builder    LLM Provider
                          │
                          ▼
                   Groq Provider
```

### ChatService

Coordinates the complete RAG request lifecycle.

Responsibilities:

- Session management
- Message persistence
- Retrieval execution
- Response generation
- Metrics recording

### SessionService

Manages conversation sessions and validates ownership.

### Generator

Transforms authorized retrieval context into grounded natural language responses.

Responsibilities:

- Build prompts
- Invoke the configured LLM provider
- Compute response confidence
- Generate citations
- Return structured responses
- Return a fallback response when no authorized or relevant context exists

The Generator never invokes the LLM when retrieval returns no usable context.

### Citation Builder

Aggregates citations by document, removes duplicate references, and preserves page and chunk metadata.

### LLM Provider

Defines the provider abstraction.

Current implementation:

- Groq (OpenAI-compatible API)

Future providers can be added without changing the generation pipeline.

---

# Knowledge Layer

The Knowledge Layer contains all business logic.

### KnowledgeService

Responsibilities:

- Validate uploads
- Register documents
- Create document records
- Start ingestion workflow

### DepartmentService

Responsibilities:

- Department management
- Department document queries
- Metadata updates
- Soft delete operations

### PermissionService

Responsibilities:

- Create permission rules
- Validate department access mappings

### FileService

Responsibilities:

- File validation
- Extension validation
- File size validation
- Disk storage
- Filename sanitization

---

# Storage Layer

## SQLStore

Central PostgreSQL abstraction.

Responsibilities:

- Save records
- Query records
- Update records
- Delete records
- Bulk chunk insertion
- Execute raw reporting queries

Application services do not import asyncpg directly.

## VectorStore

Central Chroma abstraction.

Responsibilities:

- Save embeddings
- Query embeddings
- Delete vectors
- Count vectors

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

- PDF Loader
- DOCX Loader
- TXT Loader
- Markdown Loader

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

- Model loaded once
- Reduced memory usage
- Faster inference

Query embeddings use BGE query prefixing:

```text
Represent this sentence for searching relevant passages:
```

---

# Performance Optimization Layer

Additional Optimizations:

- Permission filter cache
- Department lookup cache
- Cached Chroma filter generation
- Cached public department lookup
- Singleton embedding model
- Singleton reranker

---

## Cache Architecture

```text
                 Cache Layer

          Pipeline Cache
          BM25 Cache
          Permission Cache
          Department Cache
          Public Department Cache

                     │
                     ▼

            Retrieval Pipeline
```

Request flow through the cache layer:

```text
                 User Query
                      │
                      ▼
          Pipeline Response Cache
             │             │
      Cache Hit        Cache Miss
             │             │
             ▼             ▼
        Return Response   Agent Workflow
                              │
                              ▼
                     Parallel Research
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
       Vector Retrieval                 BM25 Retrieval
                                              │
                                              ▼
                                        BM25 Cache
```

Implemented cache layers:

- Pipeline response cache
- BM25 index cache
- Cached public department lookup
- Cached permission metadata

> **Note:** Cache invalidation occurs whenever indexed knowledge changes.

---

## Parallel Persistence

Independent database writes execute concurrently after a response is generated.

```text
        Assistant Response
                │
                ▼
 ┌──────────────┬──────────────┬──────────────┬──────────────┐
 ▼              ▼              ▼              ▼
User Msg   Assistant Msg    Metrics      Audit Log
```

This reduces response latency while preserving existing persistence behavior.

---

## Performance Profiling

A lightweight profiler measures execution time throughout the request lifecycle.

Measured stages include:

- Session lookup
- Planner execution
- Hybrid retrieval
- Query embedding
- Chroma search
- Permission filtering
- CrossEncoder reranking
- Retrieval audit logging
- Generator execution
- Parallel persistence
- Complete workflow

The profiler reports:

- Total execution time
- Average execution time
- Minimum execution time
- Maximum execution time
- Invocation count

> **Note:** Profiling is diagnostic only and does not affect application behavior.

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

> **Note:** Version information is currently maintained in the `documents.version` field. A dedicated `document_versions` table is planned for Phase 2.

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

## permissions

```text
id
role
department_id
can_access_department_id
```

## sessions

```text
id
user_id
token
expires_at
```

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

## metrics

```text
id
metric_name
metric_value
created_at
```

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

## Retrieval Security Model

Authorization is enforced using three independent layers.

```text
Layer 1
Chroma Metadata Filter
      │
      ▼
Layer 2
Application Permission Validation
      │
      ▼
Layer 3
Audit Logging
```

**Layer 1 — Chroma Metadata Filter**

Storage-level filtering using Chroma metadata filters and PostgreSQL visibility filters. Only accessible chunks are eligible for retrieval.

**Layer 2 — Application Permission Validation**

PermissionService validates every retrieved chunk before reranking.

**Layer 3 — Audit Logging**

Every retrieval and generation event is recorded for traceability and compliance review.

This defense-in-depth architecture ensures unauthorized content never reaches the language model even if retrieval implementations change. All persistence operations must pass through storage abstractions.

---

# Registry Extension System

The Smart Knowledge Bank uses registry-based extension points to keep major subsystems open for extension while avoiding modifications to existing business logic.

Each registry follows the same principle:

- Register a new implementation
- Retrieve the implementation through the registry
- Business logic never depends on concrete classes

This allows new capabilities to be added without modifying existing workflows.

```text
                Registry System

          Loader Registry
          Retriever Registry
          Permission Registry
          Agent Registry
          Tool Registry

                     │
                     ▼

            Business Services

                     │
                     ▼

           Runtime Resolution
```

## Loader Registry

Location:

```text
core/knowledge/loaders/factory.py
```

Current implementation:

- PDFLoader
- DocxLoader
- TxtLoader
- MarkdownLoader

How to add a new loader:

1. Create a class inheriting `DocumentLoader`.
2. Implement `load()` and `supported_extension()`.
3. Register it:

```python
register_loader(".xlsx", ExcelLoader)
```

Do NOT change:

- KnowledgeService
- IngestionService
- get_loader()

The loader registry automatically resolves implementations by file extension.

## Retriever Registry

Location:

```text
core/retrieval/registry.py
```

Current implementation:

- HybridRetriever (default)

Supports runtime injection for testing.

How to add a new retriever:

1. Implement the `Retriever` interface.
2. Register it:

```python
register_retriever(
    "graph",
    GraphRetriever,
)
```

3. Inject it when required:

```python
inject_retriever("graph")
```

Do NOT modify:

- RetrievalPipeline
- ResearchAgent

These always retrieve implementations through the registry.

## Permission Policy Registry

Location:

```text
core/permissions/registry.py
```

Current implementation:

- DepartmentPermissionPolicy

How to add a new permission model:

1. Implement `PermissionPolicy`.
2. Register:

```python
register_permission_policy(
    "attribute_based",
    ABACPolicy,
)
```

3. Activate through controlled code configuration.

Do NOT expose policy selection through any public API. Permission enforcement must remain entirely server-controlled.

## Tool Registry

Location:

```text
tools/registry.py
```

Current implementation:

Generic `Tool` interface.

Future tools may include:

- Calculator Tool
- Web Search Tool
- SQL Tool
- Knowledge Graph Tool

Register example:

```python
register_tool(
    "calculator",
    CalculatorTool,
)
```

Do NOT modify agent implementations when adding tools. Agents should request tools through the registry only.

## Agent Registry

Location:

```text
agents/registry.py
```

Current implementation:

- PlannerAgent
- ResearchAgent
- ResponseAgent

How to add a new workflow agent:

1. Create a class inheriting `Agent`.
2. Register:

```python
register_agent(
    "reviewer",
    ReviewerAgent,
)
```

3. Add the required workflow edge in `workflow.py`.

No existing agents require modification. This keeps the LangGraph workflow extensible while preserving existing agent implementations.

## Vector Store Interface

The application communicates only with VectorStore. Future vector databases can replace Chroma without changing business services.

Potential replacements:

- Pinecone
- Weaviate
- Qdrant
- pgvector

---

# Frontend Architecture

The frontend is implemented using Next.js with feature-oriented pages and reusable UI components.

```text
Frontend
   │
   ▼
Protected Layout
   │
   ▼
Dashboard
Knowledge Base
Chat
Users
Audit Logs
Settings
   │
   ▼
Reusable Components
   │
   ▼
Services
   │
   ▼
API
```

Application state is divided into:

- Authentication (AuthContext)
- API Services
- Feature Components

## Chat UI Architecture

```text
Chat Page
│
├── Chat Sidebar
│     ├── Session History
│     └── New Chat
│
├── Chat Window
│     ├── User Messages
│     ├── Assistant Messages
│     │      ├── Confidence Badge
│     │      ├── Citation Panel
│     │      └── Reasoning Panel
│     │
│     ├── Typing Indicator
│     ├── Loading Spinner
│     └── Error Card
│
└── Chat Input
```

Administrative pages are protected through both frontend role checks and backend authorization.

API communication is centralized through service modules that encapsulate all HTTP requests.

This separation keeps presentation components independent from backend implementation details while allowing future UI changes without affecting business logic.

## Shared UI Infrastructure

To provide a consistent user experience across all pages, the frontend reuses common presentation components.

Shared UI behaviors include:

- Loading spinner component
- Error card component
- Empty-state messaging
- Feature-oriented service layer
- Centralized API helper
- Authentication context
- Reusable UI primitives

Pages remain focused on business logic while presentation concerns are shared through reusable components.

---

# Current Platform Summary

**Architecture**

- Multi-Agent AI Workflow
- Hybrid Retrieval
- Registry-Based Extensions
- Layered Backend
- Next.js Frontend

**Storage**

- PostgreSQL
- ChromaDB
- Local File Storage

**Security**

- JWT
- RBAC
- Department Permissions
- Three-Layer Authorization

**AI**

- LangGraph
- Planner Agent
- Research Agent
- Response Agent

**Performance**

- Pipeline Cache
- BM25 Cache
- Parallel Retrieval
- Parallel Persistence
- Profiling

## Current Platform Capabilities

Implemented:

- JWT authentication
- Role-based authorization
- Department-aware permissions
- Hybrid retrieval
- Cross-Encoder reranking
- Retrieval quality gates
- Grounded response generation
- Citation generation
- Multi-agent LangGraph workflow
- Conversation-aware retrieval
- Session persistence
- Enterprise audit logging
- Observability and metrics
- Administrative dashboard
- User management
- Knowledge base management
- Complete chat interface
- Frontend role protection
- Settings page
- Shared loading spinner component
- Reusable frontend error cards
- Consistent empty-state components
- Session-based chat interface
- Agent execution reasoning display
- Confidence visualization
- Multi-level in-memory caching
- Parallel research execution
- Parallel persistence pipeline
- Request-level performance profiling
- Permission metadata caching
- BM25 index caching

---

# Architectural Evolution

```text
Week 1
Knowledge Infrastructure
      │
      ▼
Week 2
Permission-Aware RAG
      │
      ▼
Week 3
Multi-Agent AI
      │
      ▼
Week 4
Performance & Enterprise Platform
```