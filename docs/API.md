# Smart Knowledge Bank API

## Overview

The Smart Knowledge Bank backend exposes a versioned REST API under:

```text
/api/v1
```

### Authentication

All protected endpoints require a JWT Bearer Token.

Example:

```http
Authorization: Bearer <access_token>
```

### Content Type

```http
Content-Type: application/json
```

File uploads use:

```http
multipart/form-data
```

---

# Health

## GET /health

Authentication

- None

Description

Returns service health and API version information.

Response

```json
{
  "status": "ok",
  "version": "1.0",
  "api_version": "v1",
  "schema_version": "009"
}
```

---

# Auth

## POST /api/v1/auth/login

Authentication

- None

Description

Authenticate a user and return a JWT access token.

Request Body

```json
{
  "email": "user@example.com",
  "password": "password"
}
```

Response

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user": {}
}
```

---

## POST /api/v1/auth/logout

Authentication

- Required

Description

Logs out the currently authenticated user.

Request Body

None

Response

```json
{
  "message": "Successfully logged out"
}
```

---

## GET /api/v1/auth/me

Authentication

- Required

Description

Returns the currently authenticated user's profile.

Response

```json
{
  "id": "...",
  "email": "...",
  "full_name": "...",
  "role": "...",
  "department_id": "..."
}
```

---

## PUT /api/v1/auth/password

Authentication

- Required

Description

Change the current user's password.

Request Body

```json
{
  "current_password": "...",
  "new_password": "...",
  "confirm_password": "..."
}
```

Response

Success message.

---

# Admin – Documents

Authentication

All endpoints require **Admin** privileges.

---

## POST /api/v1/admin/documents

Description

Upload a new knowledge document.

Content Type

```text
multipart/form-data
```

Form Fields

| Field | Type |
|--------|------|
| file | UploadFile |
| department_id | string |
| visibility | string |
| description | string (optional) |

Response

```json
{
  "id": "...",
  "name": "...",
  "status": "processing",
  "department_id": "...",
  "created_at": "..."
}
```

---

## GET /api/v1/admin/documents

Description

Return all uploaded documents.

Response

List of document records with department information.

---

## GET /api/v1/admin/documents/{document_id}

Description

Return details for a single document.

Response

Complete document metadata.

---

## PUT /api/v1/admin/documents/{document_id}

Description

Update document metadata.

Request Body

```json
{
  "department_id": "...",
  "visibility": "...",
  "metadata": {}
}
```

Response

Updated document.

---

## DELETE /api/v1/admin/documents/{document_id}

Description

Soft delete a document.

Response

```json
{
  "message": "Document deleted",
  "document": {}
}
```

---

# Admin – Departments

Authentication

Admin only.

---

## GET /api/v1/admin/departments

Description

Return all departments.

---

## POST /api/v1/admin/departments

Description

Create a department.

Request Body

```json
{
  "name": "...",
  "display_name": "...",
  "description": "..."
}
```

---

## GET /api/v1/admin/departments/{department_id}/documents

Description

Return all documents belonging to a department.

---

# Admin – Permissions

Authentication

Admin only.

---

## POST /api/v1/admin/permissions

Description

Create a department access rule.

Request Body

```json
{
  "role": "...",
  "department_id": "...",
  "can_access_department_id": "..."
}
```

---

# Admin – Users

Authentication

Admin only.

---

## GET /api/v1/admin/users

Description

Return all users.

---

## POST /api/v1/admin/users

Description

Create a user.

Request Body

```json
{
  "email": "...",
  "password": "...",
  "full_name": "...",
  "department_id": "...",
  "role": "..."
}
```

---

## PUT /api/v1/admin/users/{user_id}

Description

Update an existing user.

Request Body

```json
{
  "role": "...",
  "department_id": "...",
  "is_active": true
}
```

---

# Admin – Audit Logs

Authentication

Admin only.

---

## GET /api/v1/admin/audit-logs

Description

Return audit log entries with optional filtering.

Query Parameters

| Parameter | Description |
|------------|-------------|
| user_id | Filter by user |
| action | Filter by action |
| from_date | Start date |
| to_date | End date |
| limit | Maximum results |
| offset | Pagination offset |

Response

Audit log collection.

---

# Admin – Metrics

Authentication

Admin only.

---

## GET /api/v1/admin/metrics/summary

Description

Return dashboard summary metrics.

Response

Dashboard statistics including:

- Active users
- Documents
- Retrieval metrics
- Query statistics
- Latency metrics

---

## GET /api/v1/admin/config

Description

Return system configuration visible to administrators.

---

# Admin – Evaluation

Authentication

Admin only.

---

## POST /api/v1/admin/evaluation/run

Description

Start a background evaluation job.

Response

```json
{
  "job_id": "...",
  "status": "running"
}
```

---

## GET /api/v1/admin/evaluation/results

Description

Return the latest evaluation report.

Response

```json
{
  "status": "completed",
  "results": {}
}
```

---

# Chat

Authentication

All endpoints require authentication.

---

## POST /api/v1/chat/query

Rate Limit

```
20 requests/minute
```

Description

Execute the complete Smart Knowledge Bank retrieval pipeline.

Pipeline

```text
Session
    ↓
Conversation Resolver
    ↓
Planner Agent
    ↓
Research Agent
    ↓
Response Agent
    ↓
Grounded Answer
```

Request Body

```json
{
  "message": "...",
  "session_id": "..."
}
```

Response

```json
{
  "answer": "...",
  "citations": [],
  "confidence_score": 92,
  "confidence_level": "high",
  "trace": []
}
```

---

## POST /api/v1/chat/plan

Description

Execute only the Planner Agent.

Useful for debugging retrieval planning independently of retrieval and generation.

Request Body

```json
{
  "message": "..."
}
```

Response

```json
{
  "strategy": "...",
  "queries": [],
  "trace": []
}
```

---

## POST /api/v1/chat/sessions

Description

Create a new chat session.

Response

```json
{
  "id": "...",
  "created_at": "...",
  "last_active": "..."
}
```

---

## GET /api/v1/chat/sessions

Description

Return all chat sessions belonging to the authenticated user.

---

## GET /api/v1/chat/sessions/{session_id}/messages

Description

Return the complete conversation history for a session.

Response

```json
{
  "session_id": "...",
  "messages": []
}
```

---

# User

Authentication

Required.

---

## GET /api/v1/user/permissions

Description

Return the authenticated user's effective permission set.

Response

```json
{
  "user": {
    "id": "...",
    "email": "...",
    "role": "...",
    "department_id": "..."
  },
  "allowed_departments": [],
  "allowed_visibilities": []
}
```

---

# API Design Principles

- All endpoints are versioned under `/api/v1`.
- JWT Bearer authentication secures protected endpoints.
- Administrative endpoints require administrator privileges.
- Background processing is used for long-running operations such as document ingestion and evaluation.
- Responses are strongly typed using Pydantic response models where applicable.
- Extension points (registries) allow new loaders, retrievers, agents, tools, and permission policies to be added without changing API contracts.