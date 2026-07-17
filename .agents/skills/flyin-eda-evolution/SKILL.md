---
name: flyin-eda-evolution
description: Evolve Fly-In from typed events to optional EDA
version: 1.0.0
metadata:
  hermes:
    category: software-development
    tags: [fly-in, events, sse, eda]
    requires_toolsets: [terminal]
---

# Fly-In EDA evolution

## When to use

Use for domain/application event design, SSE, event projections, broker feasibility, ordering,
duplicates, retry, or distinguishing EDA from event sourcing.

## Procedure

1. Read `docs/project/08_EVENT_CATALOG.md` and ADR-0001/0003.
2. Identify the real consumer and the fact it needs.
3. Confirm current maturity level and implement only the next level.
4. Use immutable past-tense events with simulation ID and ordered sequence.
5. Emit only after a transition commits; keep simulator atomic/synchronous.
6. Map events explicitly at transport boundaries.
7. Test order, duplicate handling, gaps, and deterministic projection relevant to the level.
8. Add SSE after REST; add broker only after an accepted ADR proving need.

## Broker ADR checklist

- precise problem solved;
- NATS/RabbitMQ comparison;
- process ownership/deployment;
- at-least-once/idempotency;
- per-simulation order;
- retry/backoff/dead letter;
- observability and correlation;
- local/evaluator behavior;
- operational cost and removal path.

## Reject

- Event sourcing without a replay/audit requirement.
- A bus for ordinary internal function calls.
- One event/class per implementation detail.
- Kafka for project prestige.
- Frontend as an authoritative event producer for domain movements.

## Verification

The same core tests/CLI output pass with events enabled. Consumer projections reproduce committed
state and safely handle the delivery semantics of their current maturity level.
