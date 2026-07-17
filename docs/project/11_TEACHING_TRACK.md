# Teaching track for the teammate

The teaching path follows working software. Do not teach distributed EDA before the teammate can
trace one drone through the pure domain and CLI.

## Lesson 1 - Problem and graph

Use `easy_01_linear_path.txt`.

- Nodes/zones and undirected edges/connections.
- Metadata versus effective behavior.
- Why destination type makes traversal cost directional.
- Custom adjacency representation.
- Reachability and shortest path.

Exercise: draw the graph and predict one drone's movements.

## Lesson 2 - Discrete simulation

- State, transition, invariant, and turn.
- Simultaneous movement versus a Python loop.
- Same-turn capacity release.
- Delivered state.
- Why deterministic ordering matters.

Exercise: manually validate a two-drone linear schedule.

## Lesson 3 - Capacity and scheduling

Use Basic Capacity and a derived restricted fixture.

- Shortest path for one drone versus fleet makespan.
- Zone and shared link capacity.
- Reservation tables.
- Future capacity required by restricted transit.
- Waiting, conflict, and deadlock.

Exercise: find a plausible invalid schedule and identify the violated invariant.

## Lesson 4 - CLI as an adapter

- Domain result versus string formatting.
- stdout contract, stderr diagnostics, exit codes.
- File I/O at a boundary.
- Why the core must not print.

Exercise: add a harmless alternate formatter without touching simulation.

## Lesson 5 - First API

Use `POST /maps/validate`.

- Process boundary and client/server roles.
- HTTP request/response.
- URL/resource, method, headers, JSON body.
- 200 versus 422.
- Pydantic request DTO versus domain `Map`.
- FastAPI OpenAPI/Swagger.

Exercise: send one valid and one invalid map from Swagger and curl.

## Lesson 6 - Resource lifecycle

Use `/simulations`.

- `POST`, resource ID, `GET`, `DELETE`.
- 201 versus 202.
- Synchronous computation versus queued/background computation.
- Idempotency and duplicate requests.
- Stable error envelopes.

Exercise: trace a request through adapter, application service, domain, mapper, response.

## Lesson 7 - Events

- Command versus event.
- Immutable past-tense fact.
- Event envelope, simulation ID, sequence, schema version.
- Producer, consumer, and projection.
- Why in-process events come before a broker.
- EDA versus event sourcing.

Exercise: project `TurnCompleted` events into the exact CLI movement lines.

## Lesson 8 - SSE and React

- Ordinary REST creates/queries; SSE streams.
- Browser reconnect and last event ID.
- Reducer/projection and local playback cursor.
- Why React does not rerun the planner.
- Network errors and incomplete streams.

Exercise: inspect one event in browser devtools and locate its originating domain transition.

## Lesson 9 - Distributed worker, only if implemented

- Broker, queue, backpressure.
- At-least-once delivery, duplicates, idempotent consumer.
- Ordering per simulation.
- Retry/dead-letter behavior.
- Operational cost and why it may not be justified here.

Exercise: replay a duplicate event and prove the projection remains correct.

## Per-slice explanation template

```markdown
# <Behavior>

## Problem
## Example input
## Expected observable result
## Flow through classes/modules
## Invariant protected
## Complexity
## Test that proves it
## What we deliberately did not build yet
```
