# Benchmark ledger

Baseline command:

```bash
UV_PROJECT_ENVIRONMENT=$(pwd)/../.flyin-venv uv run --extra dev python -m scripts.benchmark_official_maps
```

## Subject/rubric algorithm guidance

Fly-In 1.5 does not prescribe one concrete algorithm such as Dijkstra, A*, max-flow, or genetic
search. It defines behavioral requirements and asks the learner to explain the trade-offs:

- move all drones in the fewest practical simulation turns;
- schedule simultaneous movement to maximize throughput and avoid unnecessary delays;
- distribute drones across multiple paths;
- wait strategically when capacity blocks movement;
- avoid path conflicts and deadlocks;
- account for path length, destination movement costs, graph structure, zone capacity, and link
  capacity;
- stay adaptable because different topologies may need different routing strategies;
- discuss complexity, recalculation/caching, and memory impact during defense.

M5 therefore starts from measurement. Optimization changes are accepted only when the complete map
suite remains validator-clean and the benchmark table improves or has a documented no-regression
reason.

## Fly-In 1.5 baseline: M5-D final

- Commit/ref: `feat/m5-d-benchmark-closure` with bounded dense-map candidate discovery.
- Previous baseline: M5-C non-prefix route selection.
- Configuration: `max_routes=8`, `max_turns=1000`, deterministic scheduler/allocation, no random seed.
- Runner output: neutral CSV records; Markdown below is a progress-ledger rendering only.
- Correctness check: every row below is validated by `ScheduleValidator`.
- Timing note: duration is environment-dependent and secondary; turns and hashes are primary.

M5-D is the final benchmark closure slice. It keeps the official M5-C turns without regression and
adds a dense-graph guard so candidate discovery does not enumerate every simple route before slicing.
The detailed defense notes live in `docs/progress/M5_CLOSURE.md`.

| Category | Map | Drones | Expected evaluation target | M5-C turns | Current turns | Change | Delta vs target | Covered now? | Validated | Duration ms | Map hash |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | ---: | --- |
| Easy | Linear path | 2 | 6 | 4 | 4 | 0 | -2 | Yes | Yes | 0.25 | a03b11a9b97852f299dff023f8c745e3c4e973856addeb585b7337ebad44945d |
| Easy | Simple fork | 4 | 8 | 4 | 4 | 0 | -4 | Yes | Yes | 0.52 | 9fc3bfd1977f3bcc47baec724f4f0b041d3c52908ca0ae90ad067831ee080858 |
| Easy | Basic capacity | 4 | 6 | 4 | 4 | 0 | -2 | Yes | Yes | 0.29 | 73f5fff2e1dae24e157995793d4f08e52a9c1caa3e4f6b510a9d70054be5f06f |
| Medium | Dead end trap | 5 | 12 | 8 | 8 | 0 | -4 | Yes | Yes | 0.52 | bbdc6acadc227783c5390b59f8dc963717022fe6cd14a0e10f0283eb2281d65f |
| Medium | Circular loop | 6 | 15 | 10 | 10 | 0 | -5 | Yes | Yes | 1.19 | bfcd2d64593582c151bc376d786c22f307198a3cb529cc091b125aa078206123 |
| Medium | Priority puzzle | 5 | 12 | 6 | 6 | 0 | -6 | Yes | Yes | 0.81 | 83fb923256647bfa6e727c94738e0afd3922f2b7a9a73ce974e409def967bb94 |
| Hard | Maze nightmare | 8 | 30 | 13 | 13 | 0 | -17 | Yes | Yes | 96.57 | cf5ef07781724d23e74f813258b6cca421ac03998bab18b1e65cb7397ae7348b |
| Hard | Capacity hell | 12 | 35 | 16 | 16 | 0 | -19 | Yes | Yes | 187.91 | 6f7645c1c60bc2df1f40d5b77fbbcd4de98b7f81db2d6d6fbf349a6ea46b1d92 |
| Hard | Ultimate challenge | 15 | 45 | 26 | 26 | 0 | -19 | Yes | Yes | 350.49 | 2ee0279d0c3cd1aa1aacee5546f3df535bc6d41559430096962b6144c20d1d97 |
| Challenger | Impossible Dream | 25 | <=44 optional | 43 | 43 | 0 | -1 | Yes | Yes | 1086.82 | c5ee3795bbfaa5911b48623100e3d32e052b12f11f1235e08c0e7c628e678e8c |

## Category status

| Category | Expected evaluation threshold | Current status |
| --- | --- | --- |
| Easy | less than 10 turns | Covered: all easy maps are 4 turns. |
| Medium | 10-30 turns; individual targets 12/15/12 | Covered: all medium maps meet or beat individual targets. |
| Hard | less than 60 turns; individual targets 30/35/45 | Covered: all hard maps meet or beat individual targets. |
| Challenger | optional: beat 45 turns, meaning 44 or less | Covered: current result is 43 turns. |

## Recording protocol

For every algorithm comparison record:

- commit/ref;
- map content SHA-256;
- configuration/seed;
- validity result from independent validator;
- total turns;
- compute time as secondary environment-dependent information;
- reason for change and any regressions.

Do not compare turn counts from maps with different drone counts as if they were the same case.
