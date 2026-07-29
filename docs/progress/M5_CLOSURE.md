# M5 closure report

Date: 2026-07-28
Branch: `feat/m5-d-benchmark-closure`

## Scope

M5 closes measured route optimization for the mandatory CLI/core project. It does not start API,
React UI, event streaming, or visualization work.

## Final benchmark command

```bash
UV_PROJECT_ENVIRONMENT=$(pwd)/../.flyin-venv uv run --extra dev python -m scripts.benchmark_official_maps
```

The runner emits neutral CSV facts: map path, drone count, turn count, validity, duration, and map
SHA-256. Rubric/target comparison is documented here and in `BENCHMARKS.md`, not inside production
code.

## Final official results

| Category | Map | Drones | Target | M5-D turns | Valid | Delta |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| Easy | Linear path | 2 | 6 | 4 | Yes | -2 |
| Easy | Simple fork | 4 | 8 | 4 | Yes | -4 |
| Easy | Basic capacity | 4 | 6 | 4 | Yes | -2 |
| Medium | Dead end trap | 5 | 12 | 8 | Yes | -4 |
| Medium | Circular loop | 6 | 15 | 10 | Yes | -5 |
| Medium | Priority puzzle | 5 | 12 | 6 | Yes | -6 |
| Hard | Maze nightmare | 8 | 30 | 13 | Yes | -17 |
| Hard | Capacity hell | 12 | 35 | 16 | Yes | -19 |
| Hard | Ultimate challenge | 15 | 45 | 26 | Yes | -19 |
| Challenger | Impossible Dream | 25 | <=44 optional | 43 | Yes | -1 |

## What changed during M5

1. M5-A added a reproducible benchmark runner and ledger.
2. M5-B moved benchmark code out of the application package, added neutral route metrics and a
   deterministic makespan estimate, then selected the shortest validator-clean route window.
3. M5-C removed the prefix-only route-selection blind spot by evaluating bounded non-prefix route
   selections. This protects cases where two individually cheap routes share a bottleneck but a later
   route is independent.
4. M5-D adds a dense-graph guard so candidate discovery stops after the bounded number of complete
   candidate routes instead of enumerating every simple route before slicing.

## Why this is not map-specific overfitting

The implementation does not contain official map names, official turn targets, Challenger-specific
branches, or evaluator thresholds. Decisions use general properties:

- route movement cost;
- priority tie-break score;
- regular-zone and link capacities;
- shared zone/link bottlenecks;
- actual validator-clean schedule length;
- bounded candidate and route-selection search.

The official suite is used as measurement evidence. Additional derived tests protect generalization:

- non-prefix route combinations for shared-bottleneck cases;
- topology-preserving zone renaming;
- dense layered route graphs where candidate discovery must stop at the requested bound.

## Complexity and known ceilings

Candidate discovery now stops after `max_routes` complete routes, then forces the exact A* shortest
route to the front if necessary. That keeps dense maps from exploding just to produce eight
candidates. It is deliberately not a full k-shortest-path algorithm.

Route selection evaluates bounded combinations up to four selected routes from the candidate set.
For the default `max_routes=8`, that is small enough for the current benchmark suite and avoids a
global solver.

Known ceiling: a future unknown dense map could still need a useful route that appears after the
bounded DFS stop. The upgrade path is a measured k-shortest/simple-path enumerator, not a hard-coded
map exception.

## Defense summary

The final scheduler remains conservative: heuristics rank route sets, but the chosen answer is always
an actual schedule validated by an independent validator. M5 prioritizes correctness and explainable
throughput improvements over sophisticated optimization machinery.
