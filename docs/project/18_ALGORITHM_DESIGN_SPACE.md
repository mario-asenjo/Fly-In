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
