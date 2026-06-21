# Roadmap

## Phase 2

- Reviewer Agent
- Workflow Engine

## Phase 3

- Knowledge Graph
- Slack Integration

## Phase 4

- Multi-Tenant Architecture


# Future Cleanup Tasks

## Document Deletion

Current implementation uses soft delete:

status = 'deleted'

Future version should:

- Remove Chroma vectors
- Remove chunk records
- Archive document versions
- Delete physical file
- Add audit log entry

Not implemented in V1 to avoid accidental data loss.