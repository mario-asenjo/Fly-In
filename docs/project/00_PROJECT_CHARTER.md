# Project charter

## Purpose

Fly-In is a Python program that parses a capacity-annotated undirected graph and plans the
movement of a fleet of drones from one start hub to one end hub in as few discrete turns as
practical. It must respect zone types, zone capacity, link capacity, simultaneous movement,
and two-turn transit into restricted zones.

The implementation has three simultaneous goals:

1. Pass and defend the mandatory 42 project and its peer evaluation.
2. Develop a strong, measurable pathfinding and scheduling solution.
3. Become a teaching vehicle for APIs, event-driven architecture, and frontend integration.

## Product outcome

The final repository should provide:

- evaluator-safe Python CLI;
- strict line-aware parser;
- custom graph implementation;
- deterministic pathfinding and capacity-aware scheduling;
- valid turn-by-turn simulation and independent schedule validation;
- colored terminal representation;
- benchmark report for all official maps;
- typed domain/application events;
- FastAPI REST API and OpenAPI contract;
- React + TypeScript visualization;
- SSE event playback, with WebSocket/broker only if justified;
- tests, `mypy`, `flake8`, README, algorithm explanation, and evaluation rehearsal.

## Explicit non-goals until justified

- Authentication or user accounts.
- Database persistence.
- Event sourcing.
- Distributed transactions.
- Kafka.
- Kubernetes or production cloud deployment.
- Microservices from the first phase.
- A generic graph framework beyond Fly-In requirements.
- A visual graph editor.
- Mobile support.
- Algorithm decisions in the frontend.

## Success dimensions

### Correctness

All produced schedules pass an independent validator and all mandatory parser/simulation
rules have executable tests.

### Evaluation readiness

Every rubric item is mapped to evidence. The developer can explain the graph, parser,
algorithm, capacity model, complexity, and trade-offs without relying on generated prose.

### Performance

The solver meets category expectations first, then individual targets. Optimization never
invalidates a schedule or hard-codes a provided map.

### Architecture

The domain and mandatory CLI remain independently executable when API, UI, streaming, or
broker components are absent.

### Learning

Each vertical slice leaves a concise example and explanation suitable for teaching a teammate.

## Team model

Mario initially implements with Hermes assistance, but the code must remain suitable for a
second teammate to join later. Hermes acts as guide and reviewer, not as an opaque code
generator. Ponytail supervises minimalism and prevents speculative infrastructure.

## Working principles

- Correct before fast; measured before optimized.
- One behavior per slice.
- Tests before non-trivial implementation.
- Source hierarchy before interpretation.
- Explicit decisions before architecture expansion.
- Reversible decisions while requirements are ambiguous.
- Fresh evidence before claiming completion.
