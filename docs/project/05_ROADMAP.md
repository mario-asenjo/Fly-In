# Incremental roadmap

Each milestone must end with demonstrable behavior, tests, quality gates, explanation, progress
update, and Ponytail review. Do not begin a later milestone to make an earlier one “look useful”.

## M0 - Repository and executable contract

Goal: establish environment and one red test without designing the whole system.

Deliverables:

- Confirm Python/version/package workflow.
- Replace README login placeholders when known.
- Install dev dependencies.
- Create the smallest package/CLI entry point only when its first test needs it.
- One failing acceptance test using inline comment-free text: parse and represent the minimal map.
- `mypy` and `flake8` configured and runnable.

Exit: commands run predictably and the first failing test describes real behavior.

Do not declare a console-script entry point until a real CLI adapter exists; a broken placeholder
command is worse than adding the one-line configuration in its actual slice.

## M1 - Parser vertical slices

Order:

1. `nb_drones` and smallest start/end/connection graph.
2. Regular hubs and coordinates.
3. Comments/blanks and physical line numbers.
4. Metadata/defaults/order.
5. Unique start/end/names and prior-definition connections.
6. Duplicate undirected connections.
7. Zone types and blocked representation.
8. Capacity validation and terminal-capacity ignore rule.
9. Clear malformed-input errors.

Exit: rubric parser cases pass; parser does not know pathfinding or CLI colors.

## M2 - Custom graph and path correctness

Deliverables:

- Traversable adjacency without graph libraries.
- Reachability/disconnected handling.
- Reverse BFS hop-distance table for reachability and an admissible A* heuristic.
- A* weighted shortest path for destination costs, implemented with `heapq` only.
- Deterministic priority/tie-break policy.
- Complexity documentation.

Exit: one drone reaches end on linear, fork, restricted, priority, blocked, loop, and dead-end
fixtures; no multi-drone optimization yet.

## M3 - Deterministic simulation engine

Deliverables:

- Explicit drone state machine.
- Atomic `SimulationState -> TurnPlan -> SimulationState` transition.
- One-turn movement.
- Two-turn restricted transit and mandatory arrival.
- Delivered-drone removal.
- Exact turn/token formatter.
- Independent schedule validator.

Exit: known single/multi-drone schedules validate and exact stdout tests pass.

## M4 - Capacity-aware scheduler

Order:

1. Default single-capacity zone queue.
2. Same-turn outgoing release.
3. `max_drones > 1`.
4. Default link capacity.
5. `max_link_capacity > 1`.
6. Future reservation for restricted arrival.
7. Multiple candidate paths.
8. Route allocation and strategic waiting.
9. Deadlock prevention/detection.

Exit: all supplied maps receive valid terminating schedules, independent of target count.

## M5 - Benchmark optimization

Baseline first; optimize only from measurements:

- Collect candidate path cost and bottleneck capacity.
- Estimate fleet completion time, not only per-drone shortest path.
- Distribute drones across beneficial paths.
- Reuse/caching only when profiling shows repeated work.
- Add deterministic parameterized benchmark runner.
- Compare every change to validity and previous makespan.

Target sequence:

1. Easy category.
2. Medium category.
3. Hard category.
4. Every individual 1.5 target.
5. Optional Challenger under 45.

Exit: documented table with fresh results and explanations of remaining gaps.

## M6 - Mandatory presentation and evaluation hardening

Deliverables:

- Colored terminal visual mode using map colors.
- Clear zone/drone/capacity states without altering default stdout.
- README mandatory sections and examples.
- Evaluation matrix with evidence.
- `--capacity-info` live-coding seam rehearsed, then decide whether to retain it.
- Edge cases, invalid maps, large counts, clean-clone run.

Exit: mandatory project is defensible before API work begins.

## M7 - Typed in-process events

Deliverables:

- Minimal event catalog driven by actual consumers.
- Event envelope with simulation ID, sequence, turn, type, schema version, payload.
- CLI/metrics projection consuming emitted facts where beneficial.
- Event ordering/idempotency tests.
- ADR confirming no external broker yet.

Exit: events add consumers without changing simulator correctness or output.

## M8 - FastAPI learning API

Order:

1. Health endpoint and OpenAPI orientation.
2. Map validation resource.
3. Synchronous solve endpoint returning graph/turns/metrics.
4. Simulation resource with ID/status/result.
5. Stable error envelope.
6. API contract/integration tests.
7. SSE event stream after ordinary REST works.

Exit: API can be taught and exercised from Swagger/curl without React.

## M9 - React visualization

Order:

1. Vite + strict TypeScript scaffold.
2. Generated/typed API boundary.
3. Upload/paste and validation display.
4. Static graph SVG from coordinates.
5. Completed-turn playback.
6. Controls and metrics/capacity panel.
7. SSE live projection/reconnection.
8. Accessibility/responsive polish.

Exit: UI never computes routes and reproduces backend state reliably.

## M10 - Optional distributed EDA

Enter only if a written ADR demonstrates value. Candidate design:

- FastAPI publishes `SimulationRequested`.
- Worker computes and publishes ordered simulation events.
- API projects/streams them to clients.
- Correlation, idempotency, retry, duplicate, ordering, timeout, and poison-message behavior
  are tested.

Prefer NATS JetStream for minimal operations; prefer RabbitMQ if exchange/routing/acknowledgment
learning is an explicit goal. Do not use Kafka for this project.

## M11 - Final defense and teammate handoff

- Clean-clone installation rehearsal.
- Full rubric rehearsal.
- Complexity and algorithm whiteboard explanation.
- Two map walkthroughs: simple and capacity/restricted complex.
- Live-coding `--capacity-info` under ten minutes.
- Teammate teaching sequence from CLI through REST/events/UI.
- Final Ponytail audit and delete-list review.
