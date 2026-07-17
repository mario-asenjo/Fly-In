# ADR-0002: Prefer React over Qt for the final GUI

- Status: Accepted
- Date: 2026-07-10

## Context

Both can satisfy graphical visualization. A key additional objective is teaching APIs and
event-driven client/server communication.

## Decision

Use React + TypeScript after the FastAPI contract exists. Retain Qt as a fallback if schedule or
packaging constraints materially change.

## Alternatives considered

- PySide/Qt: fewer languages and easier direct Python integration, but an HTTP boundary would be
  more artificial.
- Terminal-only: mandatory-compatible but misses the desired final GUI/API learning outcome.

## Consequences

Natural REST/SSE teaching and web visualization, at the cost of TypeScript/toolchain work.

## Revisit trigger

Insufficient UI time, browser restrictions, or inability to package/run the web stack reliably.
