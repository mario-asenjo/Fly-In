# Evaluation matrix

Status values: `NOT_STARTED`, `IN_PROGRESS`, `EVIDENCED`, `BLOCKED`.
Only mark `EVIDENCED` with a test, command, file, or demonstrated output.

| Rubric area | Required behavior/evidence | Planned evidence | Status |
| --- | --- | --- | --- |
| README | First line, description, instructions, resources/AI use, algorithm, visual docs, example | Root README review | IN_PROGRESS |
| OOP | Proper separation/encapsulation, justified inheritance only | Package design + explanation | NOT_STARTED |
| Type safety | `mypy .` no errors/full hints | M1 strict local/CI command logs | IN_PROGRESS |
| Custom graph | No forbidden graph library; explain implementation | M2.1-M2.3 `TraversableGraph` and reverse-hop tests | IN_PROGRESS |
| Parser valid input | Drone count, zone prefixes, connections, defaults, optional comments | M1.1-M1.9 tests + permanent official easy 01 input + all 10 official maps | EVIDENCED |
| Parser errors | Malformed, invalid types, missing terminals, capacity, duplicates | M1.9 full matrix with stable code, physical line, cause, and excerpt | EVIDENCED |
| Zone occupancy | Default/explicit capacity, start/end unlimited, same-turn releases | M1.8 typed/default/unlimited parsing; later validator/simulator tests | IN_PROGRESS |
| Movement cost | Normal/priority 1, restricted 2, blocked inaccessible | M2.4 A* route-cost tests; later state-transition tests | IN_PROGRESS |
| Link capacity | Default/explicit, simultaneous enforcement | M1.8 default/explicit parsing; later reservation tests | IN_PROGRESS |
| Visualization | Clear positions/movement/colors/capacity | Terminal demo then React | NOT_STARTED |
| Basic scenarios | Single/multiple/maps/output/stationary omission | CLI integration tests | NOT_STARTED |
| Termination | Stop exactly after all delivered | CLI/simulator test | NOT_STARTED |
| Valid paths | Linear/multiple/bottleneck/types | M2.1-M2.5 graph/A* tests; later full validator tests | IN_PROGRESS |
| Conflicts | Competition/simultaneous/restricted | Scheduler tests | NOT_STARTED |
| Efficiency | 10+ drones, complex graphs, reasonable compute | Benchmark report | NOT_STARTED |
| Explanation | Complexity, design, capacity/optimization trade-offs | README + defense notes | NOT_STARTED |
| Easy benchmarks | Category <10; targets 6/8/6 with 2/4/4 drones | Fresh benchmark table | NOT_STARTED |
| Medium benchmarks | 10-30; targets 12/15/12 with 5/6/5 | Fresh benchmark table | NOT_STARTED |
| Hard benchmarks | <60; targets 30/35/45 with 8/12/15 | Fresh benchmark table | NOT_STARTED |
| Edge cases | Single, bottleneck, disconnected, invalid links, zero/high capacity | Edge-case suite; M2.2 disconnected domain test | IN_PROGRESS |
| Error handling | Clear invalid/disconnected errors | Parser errors plus M2.2 `NoRouteError`; later CLI/API tests | IN_PROGRESS |
| Code quality | Structure, comments/docs/style, visual integration | Raw default `flake8 .`, mypy strict, Ponytail | IN_PROGRESS |
| Live coding | Add `--capacity-info` output within 10 minutes | Rehearsal record | NOT_STARTED |
| Bonus performance | Meet/beat every individual target | Benchmark evidence | NOT_STARTED |
| Challenger | Beat 45 turns, meaning <=44 | Optional benchmark | NOT_STARTED |

## Live-coding design seam

The rubric may ask for:

```text
./main.py --capacity-info map.txt
```

It should add per-turn information such as:

```text
Zone X: Y/Z drones, Connection A-B: Y/Z capacity used
```

Prepare, but do not overfit:

- CLI option parsing must be isolated.
- Simulation result/turn snapshot must expose occupancy without reparsing text.
- Formatter strategy/function can add a diagnostic view.
- Default output remains unchanged.
- Rehearse from a clean branch and time it.

Do not commit a fake “live modification” history. The goal is understanding and a clean seam.

## Benchmark authority

Use Fly-In 1.5 and the evaluation sheet values with the confirmed official package at
`maps/maps-v1.5-added-before-m0/`. The v1.2 maps have known count conflicts; preserve both map
packages' hashes with final benchmark evidence.
