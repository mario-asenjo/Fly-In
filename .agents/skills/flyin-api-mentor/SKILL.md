---
name: flyin-api-mentor
description: Build and teach the Fly-In FastAPI boundary
version: 1.0.0
metadata:
  hermes:
    category: software-development
    tags: [fly-in, fastapi, api, teaching]
    requires_toolsets: [terminal]
---

# Fly-In API mentor

## When to use

Use only in the API milestone for endpoint design/implementation, OpenAPI, HTTP/DTO/error teaching,
contract tests, or integrating a client with the stable Fly-In core.

## Preconditions

Verify mandatory core/CLI and architectural isolation. Read `docs/project/06_API_CONTRACT.md` and
the API section of the roadmap. If preconditions fail, recommend the earlier smallest slice.

## Procedure

1. Select one endpoint behavior and consumer.
2. Explain resource, method, URL, headers/body, success/error status, and idempotency in Spanish.
3. Define transport DTOs and explicit domain mapping; keep FastAPI/Pydantic outside the core.
4. Write an API contract test first.
5. Implement the smallest adapter/use-case wiring.
6. Demonstrate one valid and one invalid request in Swagger/curl/test.
7. Verify core/CLI tests still pass independently.
8. Update OpenAPI/API teaching notes and run Ponytail review.

## Ordered learning slices

1. Health/OpenAPI orientation.
2. `POST /maps/validate`.
3. Synchronous `POST /solve`.
4. Simulation resource lifecycle.
5. Error normalization.
6. SSE only after REST works.

## Reject by default

Database, auth, generic repository pattern, broker, WebSocket, GraphQL, Kubernetes, domain models
as Pydantic classes, and an async job state machine that does not exist.

## Verification

Tests prove status/body/error line mapping; explanation traces HTTP -> DTO -> mapper -> application
-> domain -> response without hiding framework behavior.
