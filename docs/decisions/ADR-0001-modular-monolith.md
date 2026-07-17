# ADR-0001: Start with a modular monolith

- Status: Accepted
- Date: 2026-07-10

## Context

Fly-In requires one Python CLI but the learning target later includes API, UI, and EDA. Beginning
with separately deployed services adds failure modes before the algorithm is correct.

## Decision

Build a modular Python core with ports/adapters in one process. Add typed in-process events before
considering an external broker. Keep CLI, API, and event transports outside the domain.

## Alternatives considered

- Single unstructured script: smallest initially but difficult to test/extend/defend.
- Microservices with broker: educational but excessive before mandatory correctness.
- Event-sourced system: no product need and disproportionate complexity.

## Consequences

Simple execution/evaluation and clean evolution. Module boundaries require discipline rather
than deployment isolation.

## Revisit trigger

Measured need for independent scaling, durable queueing, or failure isolation.
