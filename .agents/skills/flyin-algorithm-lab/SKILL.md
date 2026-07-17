---
name: flyin-algorithm-lab
description: Validate and optimize Fly-In routing schedules
version: 1.0.0
metadata:
  hermes:
    category: software-development
    tags: [fly-in, algorithms, benchmarking]
    requires_toolsets: [terminal]
---

# Fly-In algorithm lab

## When to use

Use for graph/pathfinding/scheduling design, invalid schedules, benchmark gaps, complexity,
profiling, route allocation, reservations, or Challenger research.

## Procedure

1. Read graph/simulation contracts in `docs/project/03_DOMAIN_CONTRACT.md`.
2. Verify map provenance, drone count, and hash before comparing results.
3. Run/implement an independent schedule validator before optimizing.
4. Record a deterministic baseline across all relevant maps.
5. Diagnose one general bottleneck with evidence:
   - candidate paths/cost;
   - zone/link bottleneck throughput;
   - waits/conflicts;
   - fleet makespan estimate;
   - compute hot spots.
6. State one optimization hypothesis, affected invariants, complexity/memory cost, and expected
   map categories.
7. Add a regression/property example for correctness.
8. Implement one minimal general change; never branch on map name/coordinates.
9. Validate every schedule and compare every benchmark, including regressions.
10. Update `docs/progress/BENCHMARKS.md` with real values only.

## Algorithm ladder

Begin with the smallest correct custom algorithm:

- reachability/BFS;
- weighted shortest path/Dijkstra implemented in-project;
- bounded candidate paths only when multiple routes matter;
- time-indexed zone/link reservations;
- fleet allocation using estimated completion throughput;
- more complex search/heuristics only from measured need.

Do not add caching until repeated computation is measured. Document deterministic tie-breaking.

## Ponytail relationship

Ponytail removes speculative optimizers. It must not replace asymptotic reasoning or accept a
naive ceiling that misses mandatory targets without recording an upgrade trigger.

## Verification

Report validity first, turns second, compute/memory third. A turn improvement without independent
validity is rejected.
