# ADR-0004: Model terminal capacity explicitly as unlimited

- Status: Accepted
- Date: 2026-07-10

## Context

Fly-In 1.5 says start/end have no capacity limit and any `max_drones` metadata is ignored without
validation error.

## Decision

Represent effective capacity with an explicit unlimited state/value, not a large numeric sentinel.
Retain declared metadata separately only if useful for diagnostics/source fidelity.

## Alternatives considered

- Capacity equal to drone count: works per simulation but mixes map and fleet state.
- Large integer sentinel: creates hidden ceilings and unclear serialization.

## Consequences

Invariants and API/UI serialization must handle unlimited capacity deliberately.

## Revisit trigger

Only an official subject revision changing terminal occupancy.
