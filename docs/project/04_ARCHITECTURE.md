# Evolutionary architecture

## Architectural style

Use a modular monolith with ports and adapters. “Modular” protects dependency direction;
“monolith” keeps deployment, debugging, and evaluation simple. Typed events are introduced
inside the process before any external event infrastructure.

```text
CLI ---------\
              application -> domain/pathfinding/scheduling/simulation
FastAPI -----/                    |
                                  -> typed events -> CLI formatter / SSE projection
React <------ REST + SSE --------------------------------------------/
```

## Module responsibilities

| Module | Owns | Must not own/import |
| --- | --- | --- |
| `domain` | Zone, connection, graph, drone, capacities, immutable identities/invariants | FastAPI, CLI, React, filesystem |
| `parsing` | Text grammar, metadata, line-aware domain construction/errors | Route selection, rendering |
| `pathfinding` | Candidate paths and weighted/custom graph algorithms | Turn mutation, HTTP |
| `scheduling` | Route allocation, reservations, conflicts, throughput decisions | Output formatting |
| `simulation` | Atomic deterministic turn transitions and validation | Framework DTOs |
| `application` | Use cases, orchestration, ports | UI-specific state |
| `events` | Immutable typed facts | Broker-specific envelopes initially |
| `adapters/cli` | Arguments, file access, exact stdout, optional terminal view | Algorithm logic |
| `adapters/api` | HTTP DTOs/status/error mapping/streaming | Domain decisions |
| `frontend` | User interaction and visual projection | Authoritative routing/scheduling |

## Dependency rules

- Inner modules never import outer adapters.
- Application services depend on protocols/ports only where there are real alternate adapters.
- Avoid an interface with one implementation unless it isolates an actual framework/I/O seam.
- Domain objects are not Pydantic models.
- Serialization uses explicit mappers at boundaries.
- Events carry stable IDs and facts, not live mutable domain objects.

## Data flows

### Mandatory CLI

```text
file path -> CLI -> parser -> application solve use case -> planner/simulator
          -> validated turns -> exact movement formatter -> stdout
```

### API query/command

```text
JSON or uploaded text -> FastAPI DTO -> mapper -> application use case
                      -> result/error -> response DTO/status
```

### UI playback

```text
POST simulation -> simulation_id -> GET initial graph/result
                -> SSE ordered events -> React reducer/projection -> SVG view
```

## Event maturity levels

| Level | Mechanism | Exit condition |
| --- | --- | --- |
| 0 | Direct returns | Mandatory CLI behavior stable |
| 1 | Immutable in-process events | CLI and metrics consume without domain coupling |
| 2 | REST + SSE | React renders complete playback reliably |
| 3 | WebSocket | Demonstrated need for live bidirectional controls |
| 4 | NATS/RabbitMQ worker | Measured need for process isolation, queueing, or parallel compute |

An ADR is required before moving levels. Do not implement event sourcing.

## State and persistence

Initial application state is ephemeral. A simulation plan is deterministic input/output and can
be kept in memory. Persistence becomes relevant only if the product later needs history across
restarts, sharing, audit, or long-running workers. Add no database beforehand.

## Error model

Domain/parsing errors contain structured cause and context. Adapters map them:

- CLI: concise message and non-zero exit on stderr.
- API: stable error code, human message, optional line/details, correct 4xx/5xx status.
- Events: `SimulationFailed` only for work that already has a simulation identity.

Never leak stack traces as normal user output.

## Determinism

Stable ordering and explicit tie-breakers are architectural properties. The same input and
configuration must produce the same schedule, output, events, and metrics. This makes peer
evaluation, debugging, UI replay, and optimization comparisons credible.

## Why React over Qt

React creates a genuine client-server boundary and therefore teaches HTTP, OpenAPI, JSON,
streaming, and contract versioning naturally. Qt remains a fallback if delivery pressure makes
a single-language desktop application materially safer. Changing requires an ADR.

## Why SSE before WebSocket

Simulation playback is primarily server-to-client. SSE has reconnect semantics, ordered text
events, ordinary HTTP behavior, and less state than WebSocket. WebSocket becomes worthwhile
only if commands must influence computation while it is running, not merely local playback.
