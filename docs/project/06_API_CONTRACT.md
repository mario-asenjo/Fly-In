# Fly-In API contract

Status: M7 synchronous foundation in progress. PR #68 implemented launcher, application factory,
OpenAPI, and health. The active map-catalog slice now has a stable error envelope and remains open
until all local gates and the PR review pass.

## Learning goals

Use the actual Fly-In flow to teach:

- client/server separation;
- HTTP request and response;
- resources and URLs;
- `GET`, `POST`, and `DELETE` semantics;
- JSON serialization;
- transport DTO versus domain entity;
- status codes and errors;
- OpenAPI/Swagger;
- validation at a trust boundary;
- idempotency;
- synchronous versus asynchronous work;
- server-to-client streaming.

## Versioning and media

- Base path: `/api/v1`.
- JSON for ordinary messages.
- UTF-8 map text in JSON initially; multipart upload can be added after the simplest contract.
- SSE uses `text/event-stream`.
- API schema types live only in the adapter layer.

## Implemented foundation

### Health

`GET /api/v1/health` returns `200 OK` with `{"status": "ok"}`.

### Official map catalog

`GET /api/v1/maps` returns deterministic one-based entries:

```json
{"maps": [{"index": 1, "display_path": "challenger/01_the_impossible_dream.txt"}]}
```

The index is a catalog selection key, not a filesystem path accepted from the client. Catalog order
is deterministic for one repository version but indices are not durable IDs across map-set changes.

### Synchronous official-map simulation

`POST /api/v1/maps/{map_index}/simulate` selects one server-known map and calls `FlyInSolver`.
Success returns `200 OK` with map projection, ordered turns/movements, metrics, evaluator movement
lines, and warnings. An unknown index returns `404 Not Found`.

The current map DTO represents finite capacity as an integer and unlimited terminal capacity as the
string `"unlimited"`. The closure tests must lock this public JSON choice or deliberately replace it
with the later `null` plus `unlimited: true` design before clients depend on both forms.

All `SolveError` variants, server map-read failures, unknown indices, and path validation failures
are translated into the stable error envelope instead of framework-generated responses or stack traces.

## Later content-input slice

### Validate a map

```http
POST /api/v1/maps/validate
Content-Type: application/json

{"content": "nb_drones: 2\n..."}
```

Success: `200 OK`

```json
{
  "valid": true,
  "map": {
    "drone_count": 2,
    "start": "start",
    "end": "goal",
    "zones": [],
    "connections": []
  },
  "warnings": []
}
```

Invalid syntax/domain input: `422 Unprocessable Content` with stable error envelope.

### Solve directly

```http
POST /api/v1/solve
Content-Type: application/json

{"map_content": "...", "options": {}}
```

Success: `200 OK` with graph, ordered turns, and metrics. This slice proves the boundary before
introducing asynchronous resources.

## Simulation resource slice

| Method | Endpoint | Meaning |
| --- | --- | --- |
| `POST` | `/api/v1/simulations` | Create/submit simulation |
| `GET` | `/api/v1/simulations/{id}` | State and summary |
| `GET` | `/api/v1/simulations/{id}/result` | Graph, turns, metrics after completion |
| `GET` | `/api/v1/simulations/{id}/events` | Ordered SSE stream |
| `DELETE` | `/api/v1/simulations/{id}` | Cancel active or release ephemeral state |

`POST /simulations` may return `201 Created` when computation completes in-request, or
`202 Accepted` when work is queued/background. Do not return `202` merely to look asynchronous.
Include a `Location` header for the resource.

## Status model

```text
PENDING -> RUNNING -> COMPLETED
                   -> FAILED
        -> CANCELLED
```

Do not expose states the backend cannot actually produce.

## Error envelope

```json
{
  "error": {
    "code": "MAP_INVALID_CAPACITY",
    "message": "max_drones must be a positive integer",
    "details": {
      "line": 7,
      "field": "max_drones"
    }
  }
}
```

Implemented M7 examples:

- Unknown catalog selection: `404` with `MAP_NOT_FOUND`.
- Invalid path parameter: `422` with `REQUEST_VALIDATION_ERROR`.
- Solver/application failure: `422` with the public `SolveError.code`.
- Server map-read failure: `500` with `MAP_READ_ERROR` and no filesystem path leakage.

Suggested mapping:

| Condition | Status |
| --- | ---: |
| Malformed JSON/request shape | 422 |
| Invalid Fly-In map | 422 |
| Unknown simulation | 404 |
| Unsupported media type | 415 |
| State conflict/cannot cancel completed work | 409 |
| Unexpected internal failure | 500 with safe generic message |

## DTO rules

- Request DTO validates transport shape, length, and presence.
- Parser validates Fly-In grammar and domain rules.
- Explicit mapper converts parser/domain results to response DTOs.
- Do not annotate domain entities with API serialization behavior.
- Use stable string IDs in public JSON.
- Represent unlimited capacity explicitly, for example `null` plus `unlimited: true`; document
  the choice and keep it consistent.

## Idempotency

Map validation and `GET` requests are naturally idempotent. Simulation creation is not
necessarily idempotent. Do not build an idempotency-key store until duplicate creation causes a
real product issue; explain the concept using a documented future option.

## Contract testing

- Assert status, body shape, and error code, not FastAPI internals.
- Ensure parser line numbers survive API mapping.
- Ensure OpenAPI exposes intended schemas.
- Ensure framework validation errors are normalized if the API promises one envelope.
- Ensure API result tokens match CLI schedule data, not reparsed stdout.

## Security and limits

Even without authentication:

- bound request/map size;
- bound numeric parsing and reject absurd resource requests gracefully;
- never accept paths from clients for server-side file reads;
- never return stack traces;
- configure CORS narrowly for the local React origin during development;
- do not add auth speculatively.
