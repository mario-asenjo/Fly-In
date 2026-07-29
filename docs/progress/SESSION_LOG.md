# Session log

## 2026-07-29 - M6.1-M6.2 application service and evaluator CLI

- After PRs #61 and #62 were merged, created `feat/m6-application-cli-service` from updated `main`.
- Combined #55 and #56 because they share one adapter boundary: map file/text input, application
  solve result, and evaluator-safe movement lines. Kept #57 visualization and #60 FastAPI out.
- Added `flyin.application.FlyInSolver` with immutable `SolveResult` / `SolveWarning` and stable
  `SolveError` codes. It parses map text, calls `RouteAllocator.schedule()`, validates with
  `ScheduleValidator`, formats movement lines, exposes adapter-safe map/turn projections with zone
  colors, and emits terminal-zone metadata warnings without touching stdout.
- Replaced the temporary `python -m flyin` placeholder with `flyin.adapters.cli`: it reads one map
  path, prints movement lines only on stdout by default, maps invalid input to exit 2/stderr, and
  maps no-route failures to exit 3/stderr.
- Added `flyin.adapters.terminal_visual` on the same PR after reviewing Fly-In 1.5 color
  requirements. The explicit visual mode renders zones, coordinates, static capacities, source color
  metadata, endpoint-colored connections, and turn movements with known ANSI/256-color swatches from
  `MapView` / `TurnView`.
- Added `MetricsView` for the subject's optional secondary metrics: drones moved per turn, average
  delivery turn per drone, and total weighted path cost. The terminal view prints these without
  reparsing or adapter-side simulation.
- Updated `Makefile` so `make run ARGS=<map-path>` and `make debug ARGS=<map-path>` pass evaluator
  arguments through the module entry point.

## 2026-07-28 - M5-D benchmark closure and dense candidate guard

- PR #53 was still open, so M5-D was started as stacked branch `feat/m5-d-benchmark-closure` on top
  of M5-C to keep the final diff reviewable without waiting for merge.
- Added a dense layered-map regression: current unbounded DFS produced 891 complete route objects for
  `max_routes=8`; M5-D stops at 8 complete candidates and still injects the exact A* shortest route.
- Official benchmark turns remain unchanged from M5-C: easy 4/4/4, medium 8/10/6, hard 13/16/26,
  challenger 43.
- Added `docs/progress/M5_CLOSURE.md` with final benchmark evidence, anti-overfit rationale,
  complexity ceilings, and upgrade trigger for a measured k-shortest path enumerator.

## 2026-07-28 - M5-C non-prefix route selection robustness

- After PR #52 merged, updated local `main` and created `feat/m5-c-beneficial-route-allocation`.
- Added a derived regression map where candidate routes `R1` and `R2` look cheap individually but
  share a bottleneck; the optimal useful set is non-prefix (`R1`, `R3`, `R4`). M5-B produced 6 turns;
  M5-C produces 4 turns and validates independently.
- Added a metamorphic-style check: renaming zones while preserving topology keeps the same 4-turn
  makespan, guarding against accidental name-order overfitting.
- `RouteAllocator` now evaluates bounded non-prefix route selections ranked by the existing fleet
  estimate, then still returns the shortest validator-clean schedule it actually measures.
- Official map turns stay unchanged from M5-B: easy 4/4/4, medium 8/10/6, hard 13/16/26,
  challenger 43. The M5-C value is generalization evidence, not an official-table improvement.

## 2026-07-28 - M5-B route metrics and makespan estimates

- After PR #51 merged, updated local `main` and created `feat/m5-b-route-makespan-estimator`.
- Removed benchmark logic from the `flyin` application package. `scripts/benchmark_official_maps.py`
  now owns the developer benchmark dataclass, collection, records, and table rendering; application
  code has no target/evaluation thresholds.
- Added `RouteMetrics` for candidate route cost, priority, restricted count, min zone capacity, min
  link capacity, and bottleneck identity.
- Added `FleetMakespanEstimator` and `RouteWindowEstimate` to rank candidate route windows by fleet
  load and shared capacity resources.
- Updated `RouteAllocator` to try estimated windows and return the shortest validator-clean schedule,
  instead of accepting the first non-deadlocking candidate window.
- Fresh benchmark comparison vs M5-A: hard maze improves 14 -> 13, hard ultimate 29 -> 26, and
  optional Challenger 51 -> 43. Easy and Medium remain unchanged and covered.

## 2026-07-28 - M5-A benchmark baseline

- Created `feat/m5-a-benchmark-baseline` from updated `main` after PR #45 was merged.
- Re-read Fly-In 1.5 VII.1/VII.7 and the Intra rubric performance rows before coding. The sources
  require throughput, multi-path distribution, strategic waiting, deadlock avoidance, and comparison
  against targets, but do not prescribe a concrete algorithm family.
- Added a developer benchmark seam: `flyin.benchmarking` plus `scripts/benchmark_official_maps.py`.
  The code records map path, drone count, turns, validator result, duration, and SHA-256 only; target
  and evaluation comparisons stay in documentation/reporting, not code.
- Added `tests/test_benchmark_runner.py`, a smoke contract proving the runner covers every immutable
  official v1.5 map and emits the required table columns.
- Fresh baseline: Easy 4/4/4, Medium 8/10/6, Hard 14/16/29, and Challenger 51 turns; every row is
  validator-clean. Easy/Medium/Hard already meet or beat their individual targets; optional
  Challenger does not yet beat 45.
- Updated `docs/progress/BENCHMARKS.md`, `docs/progress/CURRENT.md`, and the benchmark rows in
  `docs/project/10_EVALUATION_MATRIX.md`.

## 2026-07-28 - M4-D deadlock detection and official-map closure

- Verified PR #44 was merged to `origin/main`, then created `feat/m4-d-deadlock-official-closure`
  from updated main for issue #41.
- Ran an official-map smoke through `RouteAllocator.schedule()`. Nine maps produced valid schedules;
  `hard/02_capacity_hell.txt` exposed a real no-progress failure when all eight candidate routes were
  round-robin allocated together.
- Added `ScheduleDeadlockError` as the explicit scheduler failure boundary for no-progress and
  max-turn exhaustion, then made `RouteAllocator` retry smaller candidate windows before surfacing the
  last deadlock.
- Added permanent official-map closure tests: every immutable v1.5 map now parses, schedules,
  terminates, and validates through `ScheduleValidator`. The capacity-hell regression locks the
  fallback behavior at a validator-clean 16-turn schedule without claiming M5 optimality.
- Kept CLI/API/UI, benchmark tuning, smarter makespan scoring, and evaluator confirmation for Q7/Q8
  out of this final M4 correctness slice.

## 2026-07-27 - M4-C candidate route allocation

- Added `CandidateRouteFinder.find_candidates()` as a bounded deterministic simple-route seam. It
  excludes blocked/dead branches through `TraversableGraph` and reverse reachability, sorts by cost,
  priority, and route names, and keeps the exact A* shortest route as the first/default candidate.
- Added `RouteAllocator.schedule()` to assign drones over candidate routes before delegating all
  waits, capacity reservations, restricted arrivals, and fact production to `KnownRouteScheduler`.
- Protected route splitting across two beneficial paths, single-route bottleneck waiting, and
  unsolvable-map reporting through public scheduler tests plus `ScheduleValidator`.
- Deliberately used round-robin allocation and a simple DFS candidate seam; measured optimization,
  deadlock handling, official-map closure, API/UI, and visualization remain outside this slice.

## 2026-07-27 - M4-B link and restricted reservation scheduler

- Extended `KnownRouteScheduler` with per-turn link-capacity reservations using the connection's
  unordered physical identity, so capacity is shared by both traversal directions.
- Added scheduler regressions for default link capacity queuing, explicit `max_link_capacity > 1`,
  opposite-direction traversals over the same physical link, and same-arrival restricted destination
  reservations.
- Resolved Q6 as a project decision: link capacity is aggregated across both directions. Q8 remains
  open only for evaluator confirmation of the exact restricted link-occupancy window during transit;
  M4-B covers destination capacity reservation for restricted arrivals.
- Kept multiple candidate paths, route allocation, strategic waiting, deadlock handling, benchmark
  optimization, CLI wiring, API/UI, and visualization out of this slice.

## 2026-07-27 - M4-A regular-zone capacity scheduler

- Added `flyin.scheduling.KnownRouteScheduler` as the first capacity-aware scheduling seam over
  already-selected routes. It returns turn facts, not CLI text, so future schedulers can keep using
  the independent validator before any adapter formats stdout.
- Covered default single-capacity queueing, waiting-drone omission, downstream-first same-turn
  release, and explicit regular-zone `max_drones > 1`.
- Kept link-capacity planning, restricted future reservations, candidate path generation, strategic
  route allocation, deadlock handling, benchmark optimization, CLI wiring, API/UI, and visualization
  out of M4-A.
- TDD RED was the expected missing `flyin.scheduling` import. Focused GREEN has the new scheduler
  tests validated through `ScheduleValidator`.

## 2026-07-27 - M3.5-M3.6 validation and known-route output closure

- Added an independent `ScheduleValidator` for emitted turn facts. It replays schedules from the
  parsed initial state and reports stable errors for illegal movement, blocked entry, zone overflow,
  undirected link overflow, delivered-drone movement, unknown/duplicate drone facts, and missing
  restricted arrivals.
- Added `simulate_known_routes()` for the M3 stdout seam over already-known routes: it advances the
  deterministic engine until all drones are delivered and returns exact evaluator-style movement
  lines without wiring the temporary CLI adapter yet.
- Combined #30 and #31 because both share the same schedule/fact/output seam and stay below the M4
  scheduler boundary.
- TDD RED was the expected missing `ScheduleValidator` import. GREEN has focused schedule validation
  tests plus full pytest, raw Flake8, mypy, and context validation clean.

## 2026-07-27 - M3.4 restricted transit

- Implemented restricted destination movement as a two-turn transition: departure enters
  `InTransit`, emits the proposed directed connection token, and stores the mandatory next-turn
  arrival.
- The following turn forces arrival to `AtZone` or `Delivered`; the drone does not depart again in
  the same turn even if a remaining route exists.
- Kept capacity-aware future reservations, independent schedule validation, route allocation,
  optimization, CLI wiring, API/UI, and visualization out of this slice.
- TDD RED was the existing `NotImplementedError` for restricted transit. GREEN has 84 tests, raw
  Flake8, mypy, and context validation clean.

## 2026-07-26 - M3.1-M3.3 simulation foundation

- Added `flyin.simulation` with explicit `Drone` objects and `AtZone`, `InTransit`, and `Delivered`
  location states. The initial snapshot creates stable one-based drone IDs at the start hub.
- Added an atomic normal-turn transition for known routes: it plans from the input state, returns a
  new `SimulationState`, emits ordered movement facts, and marks end arrivals as `Delivered`.
- Added evaluator-safe `format_turn()` output for zone movement tokens only; the CLI still stays
  unwired until a real adapter slice.
- Kept restricted two-turn transit, capacity-aware scheduling, independent validation, optimization,
  API/UI, and visualization out of this batch.
- TDD RED was the expected missing `flyin.simulation` import. GREEN has 82 tests, raw Flake8, and
  mypy clean.

## 2026-07-26 - M3 planning and GitHub project sync

- Re-verified repository state after M2.6: branch `feat/m2-pathfinding-closure` matches origin with
  no source diff before planning changes.
- Fresh gates pass: `make test` runs 77 tests green; `make lint` runs raw Flake8 plus mypy clean.
- Confirmed M2 is functionally closed and corrected stale Project statuses for closed M2 work.
- Broke M3 into GitHub issues #26-#31 under umbrella #3 and moved #26 plus #3 to In Progress;
  #27-#31 remain Todo.
- Recommended next implementation batch: #26 + #27 + #28, keeping restricted transit, independent
  validation, capacity-aware scheduling, optimization, API/UI, and visualization outside the first
  M3 slice.

## 2026-07-26 - M2.6 pathfinding closure matrix

- Closed the M2 one-drone pathfinding matrix with tests for official linear input, fork tie-breaks,
  restricted weighted costs, priority-only tie-breaks, blocked/disconnected no-route, loops, and
  lateral dead-end handling.
- Added a defensive A* expansion guard: neighbors absent from `ReverseHopDistances` are skipped
  before `hops_from()` is called, so a missing heuristic row cannot abort an otherwise valid route.
- Added a supervisor-requested regression around a route with a lateral branch. Under the current
  undirected graph contract a physically connected branch can normally reach back to the route, so
  the exact guard is also protected with a focused monkeypatched heuristic-table test.
- Kept simulation, capacity reservations, multiple candidate paths, CLI formatting, and visualization
  out of M2. M3 starts from the immutable `Route` result.
- Fresh gates passed with 77 tests, raw Flake8, mypy, and context validation.

## 2026-07-26 - M2.4-M2.5 exact A* and priority tie-breaks

- Added `AStarPathfinder.shortest_path()` and immutable `Route` results for one-drone weighted
  routes over the existing `TraversableGraph`.
- The A* implementation uses stdlib `heapq`, destination costs, reverse-hop `h`, and a
  `use_heuristic=False` path that behaves as the Dijkstra-equivalent oracle for tests.
- Tests prove exact A* matches the zero-heuristic oracle, a fewer-hop restricted route can lose to a
  lower-cost normal route, disconnected maps raise `NoRouteError`, priority wins only on equal cost,
  and priority cannot override a cheaper route.
- Kept multi-path allocation, scheduling, simulation, CLI output, and visualization out of this
  slice.
- TDD RED was the expected missing `AStarPathfinder` import. GREEN has 73 tests, raw Flake8, mypy,
  and context validation.

## 2026-07-26 - M2.1-M2.3 graph foundation and A* heuristic

- Added `flyin.pathfinding` with a custom `TraversableGraph` projection over `ParsedMap` physical
  connections; the graph is bidirectional, deterministic, and excludes blocked zones from adjacency.
- Added `ReverseHopDistances.to_end()` using reverse BFS from the end hub. It proves reachability,
  returns a clear `NoRouteError` for unreachable starts/dead ends, and provides the planned
  admissible A* heuristic for M2.4.
- Kept weighted A*, priority ranking, path reconstruction, scheduling, simulation, CLI output, and
  visualization out of this slice.
- TDD RED was the expected missing `flyin.pathfinding` module. GREEN has focused graph tests for
  bidirectional adjacency, blocked exclusion, reachability hops, and blocked/dead-end no-route.
- Fresh gates passed with 68 tests, raw Flake8, mypy, and context validation.

## 2026-07-26 - M2 A* planning breakdown

- Analyzed A* viability for Fly-In M2. It is acceptable if used as an exact shortest-path
  algorithm, not as a speculative optimizer.
- Rejected coordinate-distance heuristics because Fly-In edges are explicit and a long coordinate
  jump can still cost one turn, so Euclidean/Manhattan distance can overestimate.
- Chose reverse BFS hop distance over traversable edges as the planned admissible/consistent
  heuristic; `h = 0` remains the Dijkstra-equivalent fallback for debugging.
- Updated the M2 roadmap, graph contract, algorithm design notes, decision log, and GitHub M2
  issues/project to reflect A* as the weighted one-drone pathfinding approach.

## 2026-07-26 - M1.9 parser lock and raw Flake8 compliance

- Added an explicit two-variant regression proving that a leading title comment is optional:
  `nb_drones` may be the first physical line or the first significant line after comments.
- Added stable `MapParseErrorCode` values plus physical line, human cause, and a declaration excerpt
  bounded to 120 characters.
- Locked validation for empty/invalid drone counts, field counts, integer coordinates, names,
  balanced non-empty metadata blocks, `key=value` tokens, supported/unique keys, types, capacities,
  prior endpoints, duplicate undirected links, and self-connections.
- Re-read Fly-In 1.5 VII.4 and resolved Q13 literally: terminal `max_drones` remains raw metadata but
  its value is not validated numerically and never changes unlimited effective capacity.
- Resolved Q1/Q3/Q4/Q5/Q9/Q13 and retained graph, route, disconnected-map, and movement concerns for
  M2 and later milestones.
- Removed `.flake8`, adapted Python lines to the default 79-character standard, and moved the uv
  environment outside the repository so the mandatory literal `flake8 .` command runs unconfigured
  without traversing third-party packages.
- TDD RED was the expected missing `MapParseErrorCode` import. GREEN has 64 tests, context validation,
  raw Flake8, mypy strict, diff checking, and all ten official maps passing.
- Initial Ponytail review found that Python rejects conversions above 4300 digits before the parser
  could wrap them. Drone count, coordinates, regular capacity, and link capacity now convert inside
  guarded boundaries and have permanent line-aware regression tests.
- Follow-up Ponytail verdict: `ACEPTAR`, with the oversized-integer blocker resolved, all 19 public
  error codes explicitly exercised, all ten official maps under permanent regression, raw Flake8
  confirmed, and no new blocker.
- M1 is complete. The next bounded slice is M2.1 custom undirected adjacency without pathfinding.

## 2026-07-26 - M1.7-M1.8 metadata semantics and official-map regression

- Added typed `ZoneType` values for normal, blocked, restricted, and priority zones plus optional
  color projection from preserved raw metadata.
- Added default/explicit positive capacities for regular zones and connections.
- Added explicit `CapacityLimit.UNLIMITED` for start/end while retaining their declared
  `max_drones` metadata according to ADR-0004; M1.9 later locked the ignored-value rule.
- Kept terminal effective type normal under the current Q9 interpretation; raw `zone` metadata is
  retained for source fidelity pending parser lock.
- Added a provenance-commented derived fixture covering every type/capacity rule.
- Added a permanent test that reads official v1.5 easy 01 as text, proves its first line is the title
  comment, and passes that unmodified content to `MapParser.parse()`.
- TDD RED was the expected missing `CapacityLimit` import. GREEN has eighteen tests and strict gates.
- All ten official maps parse semantically: 130 regular hubs, 180 links, 32 restricted hubs,
  20 priority hubs, 55 explicit zone capacities above one, and 26 link capacities above one; every
  terminal has unlimited effective capacity.
- Initial Ponytail full review requested explicit Q9 regression coverage and stronger derived-fixture
  provenance. The fixture now declares blocked metadata on start, the test proves effective normal
  plus raw retention, and its header records source, assumption, and purpose. Follow-up verdict:
  `ACEPTAR`, with both findings resolved and no new blocker.
- M1.9 remained a separate malformed-input and stable-error taxonomy slice and is now complete.

## 2026-07-25 - M1.5-M1.6 structural integrity and inline comments

- Combined adjacent cross-line constraints: exactly one start/end, globally unique zone names,
  prior-defined connection endpoints, and exact/reversed undirected connection duplicates.
- Added `Connection.identity` as a canonical unordered name pair while retaining directed
  `left`/`right` references for future traversal/output.
- Replaced terminal assertions and endpoint `KeyError` leakage with physical-line `MapParseError`.
- Supported inline `#` comments through the existing significant-line normalization and resolved Q2
  following explicit user approval.
- TDD RED produced ten expected failures; GREEN has twelve tests, strict gates, and all ten official
  v1.5 maps parsing successfully.
- Independent Ponytail full review accepted the slice without blocking changes. It deferred the
  syntax-versus-duplicate terminal error precedence to M1.9 and accepted centralized name coverage
  through `_register_zone()` without testing every role permutation.
- Deliberately deferred self-loops, metadata semantics, zone/color interpretation, effective
  capacities, and stable complete error codes.

## 2026-07-25 - M1.3-M1.4 significant lines and raw metadata

- Combined two adjacent parser concerns into one coherent slice: blanks/full-line comments with
  physical line tracking, then valid raw metadata tokenization/default/canonical order.
- Added public `MapParseError.line_number`, immutable raw metadata tuples on zones/connections, and
  exact declaration classification; semantic zone/color/capacity interpretation stays deferred.
- Proved comments before `nb_drones`, blanks between declarations, metadata in different orders,
  empty metadata defaults, connection metadata, and physical line 5 for an unknown declaration.
- Verified four tests, all local gates, and direct parsing of official easy maps 01 and 02.
- Independent Ponytail full review accepted the slice without blocking changes; malformed empty
  keys/values, empty/multiple blocks, and the complete metadata error matrix remain deferred to
  M1.9 rather than receiving partial validation here.
- Next: approve M1.5 for terminal/name uniqueness and prior-defined connection endpoints.

## 2026-07-25 - M1.2 regular hubs and multiple connections

- Added one wider but coherent RED example with two regular hubs, three connections, four drones,
  and a negative coordinate; the M1.1 fixed four-line parser failed on the extra declarations.
- Extended `ParsedMap` with immutable regular hubs and changed `MapParser` to process valid
  declarations in source order, resolving connection names through one shared zone dictionary.
- Preserved M1.1 behavior and deliberately excluded comments, metadata, formal errors, duplicate
  rules, bidirectional identity, pathfinding, simulation, and CLI concerns.
- Independent Ponytail full review accepted the diff without blocking or requested changes.
- Verified both parser tests, context validation, `flake8`, and `mypy --strict`.
- Next: approve M1.3 for blanks/full-line comments plus physical source-line tracking.

## 2026-07-25 - M1.1 smallest linear-map parser

- Started from updated `main` and preserved the existing acceptance test as the TDD red contract:
  collection failed because `flyin.parsing` did not exist.
- Added immutable typed domain objects and the smallest `MapParser.parse()` implementation for one
  drone count, start, end, and connection; no parser error model or later grammar was introduced.
- Ponytail review strengthened the same acceptance test to prove coordinates, endpoint object
  references, the one-connection tuple, and immutable parsed state without expanding grammar scope.
- Ponytail also confirmed two deliberate deferrals already placed by the roadmap: strict prefix
  errors in M1.9 and canonical undirected connection identity in M1.6.
- Verified the focused test, full pytest suite, context validation, `flake8`, and `mypy --strict`.
- Next: approve one M1.2 red example for a regular hub, multiple connections, and coordinates.

## 2026-07-17 - Subject Makefile compliance and official-map confirmation

- Re-read Fly-In 1.5 §III.2 directly: `install`, `run`, `debug`, `clean`, `lint`, and optional
  `lint-strict` are mandatory Makefile behavior; `lint` carries the subject's explicit mypy flags.
- Implemented those targets with the existing `uv` workflow and verified `run` against the M0
  temporary module entry point.
- Confirmed `maps/maps-v1.5-added-before-m0/` as the official 1.5 package, added its hashes to
  the immutable manifest, and updated source hierarchy, provenance, benchmark path, risks, and Q10.
- Recorded the confirmed README login `masenjo` and resolved Q12.
- Next: the smallest parser slice that turns `tests/test_minimal_map_parsing.py` green.

## 2026-07-17 - M0 executable contract / repository publishing

- Verified local Python 3.13.14, `uv` 0.11.19, GNU Make 4.4.1, GitHub authentication, repository administration, and `main` as the default branch.
- Added the first intentionally failing, inline comment-free acceptance test for the smallest map: one drone, start, end, and one connection.
- Added a repository-wide pull-request template requiring real commands, scope, Fly-In invariants, documentation, risk, teaching, and Ponytail evidence.
- No production parser was added: M0 deliberately ends with the red executable contract.
- Next: implement only the types and parser behavior required to make `tests/test_minimal_map_parsing.py` pass.

## 2026-07-10 - Initial context package

- Compared subjects 1.2 and 1.5 and aligned the evaluation rubric.
- Recorded benchmark changes and stale-map conflicts.
- Chose evolutionary modular-monolith architecture.
- Planned mandatory CLI -> in-process events -> FastAPI -> React -> SSE -> optional broker.
- Integrated official Ponytail Hermes plugin as minimalism supervisor.
- Created project/Hermes context package; no production solution generated.
- Forward-tested the start/spec-guardian workflows from clean agent contexts.
- Tightened M0 to one inline comment-free failing test and removed a premature broken CLI entry.
- Added the terminal invalid-capacity ambiguity as Q13.
- Next: agree on M0 and first parser vertical slice.

Future entries should be short, evidence-based, and link decisions/tests rather than duplicate them.
