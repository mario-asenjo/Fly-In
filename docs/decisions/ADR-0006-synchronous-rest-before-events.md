# ADR-0006: Allow synchronous REST before typed events

- Status: Accepted
- Date: 2026-08-09

## Context

The original roadmap placed typed in-process events before FastAPI. PR #68 introduced the API
launcher, application factory, OpenAPI, and health endpoint first, and the active branch now exposes
an official-map catalog plus synchronous simulation through the existing `FlyInSolver` return value.
Neither flow needs asynchronous work, replay, or streaming.

## Decision

Allow ordinary synchronous REST adapters to call the application service directly before typed
events exist. Keep typed immutable events mandatory before SSE or any asynchronous simulation
resource. FastAPI remains an outer adapter; it must not move HTTP/Pydantic types into the application
or core.

## Alternatives considered

- Revert the API until events exist: discards working adapter-boundary learning without improving
  solver correctness.
- Add placeholder events immediately: creates abstractions with no real event consumer.
- Treat all REST as event-driven: adds identity, sequencing, and lifecycle machinery to synchronous
  request/response behavior that does not need it.

## Consequences

The roadmap records synchronous FastAPI as M7 and typed events/SSE readiness as M8. The current API
can remain small and synchronous. Error mapping, trust-boundary limits, and OpenAPI tests are still
required before the API phase closes. React, SSE, background work, persistence, auth, and a broker
remain deferred.

## Revisit trigger

A request must outlive its HTTP call, clients need ordered live playback/reconnection, or another
real consumer needs committed simulation facts.
