# Event catalog and EDA evolution

Status: design constraint for M7 onward. Create only events with a real consumer.

## Command versus event

- Command: request that may be rejected, imperative name, e.g. `StartSimulation`.
- Event: immutable fact that already happened, past-tense name, e.g. `SimulationStarted`.

Never use an event name for a request and never allow consumers to mutate the emitted event.

## Envelope

Proposed transport-neutral fields:

```json
{
  "event_id": "uuid",
  "simulation_id": "uuid",
  "sequence": 12,
  "turn": 4,
  "occurred_at": "2026-07-10T10:00:00Z",
  "type": "drone.arrived.v1",
  "schema_version": 1,
  "payload": {}
}
```

For deterministic simulation tests, do not make wall-clock time part of equality or inject a
clock. Sequence is strictly increasing within a simulation and supplies authoritative order.

## Minimal candidate catalog

| Event | When | Core payload |
| --- | --- | --- |
| `MapParsed` | Valid parsing completed | map summary/hash |
| `SimulationStarted` | Initial state established | drone count/start/end |
| `TurnStarted` | A turn begins, only if a consumer needs it | turn |
| `DroneDeparted` | Drone leaves an at-zone state | drone/origin/destination/link |
| `DroneEnteredTransit` | Two-turn restricted movement begins | drone/link/arrival turn |
| `DroneArrived` | Drone reaches a non-end destination | drone/destination |
| `DroneDelivered` | Drone reaches end | drone/end |
| `TurnCompleted` | Atomic turn applied | movement tokens/summary |
| `CapacitySnapshotCreated` | Optional diagnostic projection | occupancy/link use |
| `SimulationCompleted` | All drones delivered | turns/metrics |
| `SimulationFailed` | Identified simulation cannot complete | safe code/message |

Do not emit both an overly granular and aggregate event until consumers prove they need both.
`TurnCompleted` may be sufficient for the first React playback.

## Ordering and duplication

In-process level:

- Preserve list order from deterministic simulation.
- A failed consumer cannot partially change domain state.

SSE level:

- Use sequence as SSE `id`.
- Support reconnection from the last acknowledged/received sequence when retained events exist.
- Client reducer ignores a duplicate event ID/sequence and detects a gap.

Broker level, if reached:

- Assume at-least-once delivery.
- Consumers are idempotent by event ID.
- Preserve per-simulation order; global ordering is unnecessary.
- Define retry/backoff/dead-letter behavior.
- Never acknowledge before durable/required processing.
- Correlate command and resulting stream with simulation ID and optional causation ID.

## Schema evolution

- Event type includes major schema version.
- Additive optional fields are preferred.
- Breaking payload change creates a new version/mapper.
- Domain classes are not serialized directly.
- Keep old readers working for the supported replay window.

## What EDA does not mean here

- Not event sourcing.
- Not microservices by default.
- Not one queue per class.
- Not eventual consistency inside the deterministic simulator.
- Not putting every function call on a bus.

The simulator remains synchronous and atomic internally. Events describe committed transitions.

## Broker decision gate

An external broker is permitted only if at least one is demonstrated:

- solver computation must outlive/request process;
- multiple independent consumers need durable delivery;
- workload queueing/backpressure is required;
- computation must scale separately;
- failure isolation across processes materially helps.

The ADR must address operations, observability, ordering, duplicates, retry, local development,
evaluation impact, and removal path.
