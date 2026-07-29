# Current project state

- Last updated: 2026-07-29
- Current milestone: M6 - Mandatory presentation and evaluation hardening
- Production implementation: M6.1-M6.4 have landed the adapter-neutral application service,
  evaluator-safe CLI adapter, optional terminal visual mode, visual metrics, rainbow labels,
  `--capacity-info`, and README/evaluation hardening
- Mandatory completion: M0, parser slices M1.1-M1.9, graph/path slices M2.1-M2.6, and M3
  deterministic simulation slices M3.1-M3.6 are complete
- API/UI/EDA implementation: intentionally not started

## Verified completed

- Fly-In 1.2 and 1.5 subjects compared; the Fly-In 1.5 Makefile rules were rechecked directly.
- `maps/maps-v1.5-added-before-m0/` is confirmed as the official 1.5 map package and hash-pinned.
- The historical v1.2 snapshot remains immutable comparison evidence only.
- `masenjo` is the confirmed README 42 login.
- Python 3.13.14, `uv` 0.11.19, GNU Make 4.4.1, and GitHub CLI authentication are verified locally.
- The Makefile provides the subject-required `install`, `run`, `debug`, `clean`, `lint`, and optional
  `lint-strict` targets; `run` accepts map arguments through `ARGS` and delegates to `python -m flyin`.
- The first comment-free minimal-map acceptance test originated as the intentional M0 red contract.
- M1.1 turns that contract green with immutable typed `Zone`, `Connection`, and `ParsedMap`
  objects plus `MapParser.parse()` for one drone count, start, end, and connection.
- M1.2 supports any number of regular hubs and valid prior-defined connections while preserving
  source order, coordinates, and shared `Zone` object identity across the parsed map.
- M1.3 ignores blanks/full-line comments and preserves physical source lines in `MapParseError`.
- M1.4 stores immutable canonical `key=value` metadata on zones/connections, with empty metadata as
  the default and tag order proven irrelevant; metadata semantics remain deliberately deferred.
- M1.5 requires unique terminals/names and prior-defined connection endpoints with physical-line
  `MapParseError` diagnostics.
- M1.6 rejects exact and reversed duplicate connections through canonical unordered identity while
  preserving directed `left`/`right` endpoints.
- Inline `#` comments are supported by the same physical-line normalization used for full comments.
- M1.7 exposes typed normal/blocked/restricted/priority zones and optional colors while preserving
  canonical raw metadata.
- M1.8 applies positive default/explicit capacities to regular zones and links, and represents
  start/end effective capacity explicitly as unlimited while retaining ignored declarations.
- A permanent integration test feeds the actual official easy 01 file content, including its first
  title-comment line, into the text parser; all ten official maps also pass semantic verification.
- A named regression proves the title comment is optional: `nb_drones` may be the first physical
  line or the first significant line after comments.
- M1.9 validates the complete malformed-input matrix and exposes stable `MapParseErrorCode`,
  physical line, human-readable cause, and a bounded declaration excerpt.
- Terminal `max_drones` is preserved raw but ignored without numeric validation, exactly as Fly-In
  1.5 section VII.4 requires; effective terminal capacity remains unlimited.
- The repository has no Flake8 configuration file. The literal subject command `flake8 .` passes
  with Flake8's default 79-character rule, as do pytest and `mypy --strict`.
- M2.1 builds a custom undirected traversable graph from parsed physical connections without a graph
  library while excluding blocked zones from adjacency.
- M2.2 exposes a clear no-route boundary for disconnected/blocked maps rather than leaking raw
  lookup errors or looping.
- M2.3 computes reverse BFS hop distances to the end as the planned admissible A* heuristic; blocked
  and dead-end zones are absent from the reachable table.
- M2.4 uses stdlib `heapq` for exact one-drone A* pathfinding, with destination movement costs and
  `h = 0` as a Dijkstra-equivalent oracle covered by tests.
- M2.5 keeps priority as a deterministic tie-break for equal-cost routes only; tests prove priority
  cannot override a lower-cost route.
- M2.6 covers the one-drone matrix with linear official input, fork tie-breaks, restricted costs,
  priority tie-breaks, blocked/disconnected maps, loop safety, and dead-end/lateral-branch handling.
- A* expansion now skips neighbors absent from the reverse-hop table before calculating `h`, keeping
  heuristic lookup failures away from otherwise valid routes.
- M3.1 introduces explicit `Drone` objects with `AtZone`, `InTransit`, and `Delivered` location
  states, plus immutable `SimulationState.initial()` snapshots with stable one-based drone IDs.
- M3.2 applies a deterministic atomic one-turn transition for known normal/priority routes and
  moves drones reaching the end into `Delivered` so later turns emit no extra facts for them.
- M3.3 formats completed movement facts as evaluator-safe `D<ID>-<zone>` tokens ordered by drone ID,
  without wiring the temporary CLI stdout yet.
- M3.4 moves drones entering restricted destinations into `InTransit` for one turn, emits the
  directed proposed token `D<ID>-<origin>-<destination>`, and forces arrival on the following turn
  before the route can continue.
- M3.5 adds an independent `ScheduleValidator` for emitted turn facts, checking illegal moves,
  blocked traversal, per-turn zone/link capacity, delivered-drone immobility, and mandatory
  restricted arrivals without reusing the scheduler/engine decision path.
- M3.6 adds `simulate_known_routes()` as the known-route output seam: it advances deterministic
  routes until every drone is delivered and returns exact evaluator-style movement lines.
- M4.1-M4.2 add `KnownRouteScheduler.schedule_known_routes()` as the first capacity-aware
  scheduling seam over precomputed routes. It queues drones for default single-capacity regular
  zones, orders downstream departures before upstream entries so same-turn release is usable, omits
  waiting drones from stdout facts, supports explicit regular-zone capacity above one, and produces
  schedules accepted by `ScheduleValidator`.
- M4.3-M4.4 add link-capacity reservations to the known-route scheduler. Default connection capacity
  queues departures even when the destination zone has room, explicit `max_link_capacity > 1` permits
  concurrent use, reversed traversals share one undirected physical connection capacity, and
  same-turn departures into restricted destinations reserve next-arrival destination capacity.
- M4.5-M4.6 add `CandidateRouteFinder.find_candidates()` and `RouteAllocator.schedule()`. Candidate
  discovery returns a bounded deterministic set of simple traversable routes with A*'s exact shortest
  route first; route allocation distributes drones round-robin over those candidates and delegates
  turn validity, waits, and capacity enforcement to `KnownRouteScheduler` plus `ScheduleValidator`.
- M4.7 adds explicit `ScheduleDeadlockError` detection for known-route no-progress/max-turn failure,
  has `RouteAllocator` retry smaller candidate windows when a route mix deadlocks, and permanently
  validates terminating schedules for every official v1.5 map under
  `maps/maps-v1.5-added-before-m0/`.
- M5-A added `scripts/benchmark_official_maps.py` as a developer-only benchmark runner. M5-B keeps
  benchmarking outside the application package; no target/evaluation thresholds live in code.
- M5-B adds `RouteMetrics`, `RouteWindowEstimate`, and `FleetMakespanEstimator` for candidate-route
  cost/capacity facts and deterministic route-window estimates.
- `RouteAllocator` now ranks candidate windows by estimate and returns the shortest validator-clean
  schedule it can produce from those windows, preserving the independent validation boundary.
- The fresh M5-B baseline covers all expected Easy, Medium, Hard, and optional Challenger targets:
  easy 4/4/4, medium 8/10/6, hard 13/16/26, challenger 43 turns.
- M5-C addresses the correction-sheet risk that good individual routes can be bad together. The
  allocator now evaluates bounded non-prefix route combinations, so it can choose `[R1, R3]` when
  `[R1, R2]` shares a bottleneck. Derived tests also prove stable makespan under topology-preserving
  zone renaming. Official benchmark turns remain easy 4/4/4, medium 8/10/6, hard 13/16/26,
  challenger 43.
- M5-D adds a dense layered-map regression proving candidate discovery stops at the requested route
  bound instead of enumerating every simple route before slicing. `docs/progress/M5_CLOSURE.md`
  explains the final benchmark strategy, why it is not map-specific overfitting, complexity ceilings,
  and the measured upgrade path.
- M6.1-M6.2 introduce `flyin.application.FlyInSolver` as the shared use-case seam and
  `flyin.adapters.cli` as the evaluator CLI. The service parses text, schedules through the existing
  core, independently validates the schedule, returns immutable movement lines, warnings, and
  adapter-safe map/turn projections including zone colors for terminal/API visualization, and
  translates parse/no-route/deadlock failures into stable adapter-level `SolveError` codes.
- Default CLI stdout remains evaluator-safe movement lines. `--visual` renders map zones,
  coordinates, static capacities, source colors, connections, and turn-by-turn movements from
  `MapView`/`TurnView` using ANSI/256-color swatches plus optional subject metrics from
  `MetricsView`, while keeping diagnostics on stderr. `color=rainbow` is rendered per letter in
  the terminal adapter.
- `--capacity-info` reuses validated application capacity projections and appends per-turn zone/link
  diagnostics only when explicitly requested.
- README and the evaluation matrix now describe the real M6 state instead of the old parser-only
  snapshot.

## Next smallest slice

Open the M6 hardening PR for #57/#58, verify CI, then close the M6 umbrella if review accepts the
README/evaluation evidence. After M6 is merged, the next planned coding slice is #59 M7.1 typed
in-process events; do not start FastAPI (#60) before that event seam is proven.

## Active blockers

None for M6 hardening. Further route-allocation optimization, API/UI, and React visualization remain
intentionally deferred. Q7/Q8 restricted-transit evaluator confirmation remains open and should stay
visible during defense and before API/event projection hardening.

## Required context for next session

- `AGENTS.md`
- `docs/project/02_SOURCE_OF_TRUTH.md`
- Drone state, turn semantics, restricted movement, capacity invariants, and output sections of
  `docs/project/03_DOMAIN_CONTRACT.md`
- `docs/project/05_ROADMAP.md` M6-M8
- `docs/progress/OPEN_QUESTIONS.md`
