# Algorithm design space

This is a decision guide, not an instruction to implement every algorithm.

## Decompose the problem

Fly-In combines:

1. Graph parsing/reachability.
2. Candidate path discovery with destination-weighted costs.
3. Multi-commodity-like fleet allocation across shared capacities.
4. Discrete-time conflict-free scheduling.
5. Primary makespan minimization.

An exact global optimum can become expensive. The project asks for efficient good schedules and
benchmark targets, so evolve from correct baselines to measured heuristics.

## Baseline A - one shortest path

Find one weighted shortest path and pipeline all drones through it.

- Strength: easy to prove and debug.
- Weakness: ignores parallel paths and may fail benchmarks.
- Use: M2/M3 correctness baseline.

## M2 pathfinding choice - exact A*

Use A* for the one-drone M2 path decision, but keep it exact rather than heuristic-only:

- `g`: accumulated movement cost, where each edge cost is based on the destination zone.
- `h`: reverse BFS hop distance from the current zone to the end, computed on the traversable
  unweighted graph with blocked zones excluded.
- `f = g + h` and a deterministic tie-break tuple decide heap order.
- Python stdlib `heapq` is enough; no graph/pathfinding dependency is allowed.

Viability notes:

- The hop-distance heuristic is admissible because every remaining move costs at least one turn.
- It is consistent because adjacent hop distances differ by at most one and all movement costs are
  at least one.
- Coordinate distance is intentionally rejected as the default heuristic: map coordinates do not
  constrain edge length, so Euclidean/Manhattan distance can overestimate and break optimality.
- If `h = 0`, the same implementation degenerates to Dijkstra. Keep that as the debug fallback or
  test oracle if the heuristic ever becomes suspicious.
- A* still finds only one best path; path diversity and fleet allocation remain M4/M5 concerns.

Planned deterministic ordering:

1. Lowest `f`.
2. Lowest `g` for stable shortest-cost behavior.
3. Higher priority-score only when total route cost is otherwise equivalent.
4. Lexicographic zone/path key as the final deterministic fallback.

Implementation boundary:

- M2.1 builds only the traversable graph; it does not compute heuristics or paths.
- M2.2 can reuse reverse BFS as the reachability proof and store hop distances to the end.
- M2.3 turns that hop-distance table into the public heuristic contract and verifies `h = 0`
  matches Dijkstra-style behavior on small fixtures.
- M2.4 introduced the `heapq` A* loop and route reconstruction.
- M2.5 added priority/tie-break ranking without changing shortest-cost correctness.
- M2.6 closed coverage with a fixture matrix and official/derived-map evidence before simulation.
  Expansion skips neighbors absent from the reverse-hop table before calculating `h`; those neighbors
  cannot improve a route to `end` and must not abort otherwise valid search.

Minimum tests before trusting A*:

- blocked zones are absent from both adjacency and reverse-hop distances;
- a disconnected end produces a clear no-route result before heap search runs forever;
- a restricted shortcut with fewer hops loses to a normal route with lower destination cost;
- a priority route wins only when total cost is tied;
- the same map parsed twice returns the same route and cost.

## Baseline B - several simple candidate paths

Generate a bounded deterministic set of loop-free paths, then evaluate cost and bottleneck.

- Do not enumerate all simple paths on large cyclic graphs.
- Exclude blocked zones.
- Prefer priority in a tie, not at arbitrary total cost.
- Candidate-generation algorithm must be custom and complexity documented.

## Fleet allocation estimate

For a path `p`, estimate:

- latency: sum of destination movement costs;
- throughput: limiting effective zone/link capacity along the route;
- congestion from overlap with already selected paths;
- expected completion turn for the next assigned drone.

Assign each next drone to the path with the smallest predicted fleet completion increase, then let
the actual reservation scheduler validate/adjust timing. This is a heuristic, not proof of optimum.

## Reservation scheduling

Maintain time-indexed usage:

```text
zone_usage[turn][zone]
link_usage[turn][undirected_link]
```

Before a departure reserve every required resource, including future restricted arrival. A simple
earliest-feasible-start search is preferable before complex backtracking.

## Conflict/deadlock strategy

- Never route into blocked/dead-end zones that do not lead to end.
- Plan using complete paths to the end rather than greedy next-edge movement.
- Waiting is explicit and may be optimal.
- Detect no-progress turns; fail clearly instead of looping forever.
- Bound any backtracking/search and expose the ceiling as a measured limitation.

## Optimization candidates, in order of evidence

1. Better candidate path diversity.
2. Bottleneck-aware assignment.
3. Overlap penalty between selected paths.
4. Reservation-aware earliest arrival.
5. Reassignment/local improvement of worst drones.
6. Cached path calculations if profiling proves repetition.
7. Bounded search/beam/A* over schedule states only if targets still justify cost.

## Complexity reporting

Report separately:

- parser/graph construction;
- path search;
- number/path-generation bound;
- per-drone allocation;
- reservation horizon scan;
- simulation/validation;
- memory in graph, candidates, and reservations.

Avoid claiming a single `O(...)` for the entire system without defining variables.
