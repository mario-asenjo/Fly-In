# ADR-0003: Use SSE before WebSocket

- Status: Accepted
- Date: 2026-07-10

## Context

The first real-time need is ordered backend-to-browser simulation playback. Control buttons can
operate on local playback or ordinary REST resources.

## Decision

Implement REST first, then Server-Sent Events. Add WebSocket only when a demonstrated feature
requires bidirectional live communication during computation.

## Alternatives considered

- WebSocket immediately: flexible but adds connection/protocol/state complexity.
- Polling: simple but less suitable for ordered event learning/playback.

## Consequences

Simpler HTTP semantics/reconnect. Not suitable for high-frequency bidirectional commands.

## Revisit trigger

Commands must influence a running backend solver with low latency.
