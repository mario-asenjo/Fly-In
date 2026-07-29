# Evaluation matrix

Status values: `NOT_STARTED`, `IN_PROGRESS`, `EVIDENCED`, `BLOCKED`.
Only mark `EVIDENCED` with a test, command, file, or demonstrated output.

| Rubric area | Required behavior/evidence | Planned evidence | Status |
| --- | --- | --- | --- |
| README | First line, description, instructions, resources/AI use, algorithm, visual docs, example | Root README review | IN_PROGRESS |
| OOP | Proper separation/encapsulation, justified inheritance only | Application/CLI adapter boundary plus package design explanation | IN_PROGRESS |
| Type safety | `mypy .` no errors/full hints | M1 strict local/CI command logs | IN_PROGRESS |
| Custom graph | No forbidden graph library; explain implementation | M2.1-M2.6 graph/A* tests and teaching notes | EVIDENCED |
| Parser valid input | Drone count, zone prefixes, connections, defaults, optional comments | M1.1-M1.9 tests + permanent official easy 01 input + all 10 official maps | EVIDENCED |
| Parser errors | Malformed, invalid types, missing terminals, capacity, duplicates | M1.9 full matrix with stable code, physical line, cause, and excerpt | EVIDENCED |
| Zone occupancy | Default/explicit capacity, start/end unlimited, same-turn releases | M1.8 parsing plus M3.5 validator overflow tests | EVIDENCED |
| Movement cost | Normal/priority 1, restricted 2, blocked inaccessible | M2.4-M2.6 A* route-cost tests plus M3.4 restricted two-turn state-transition tests | EVIDENCED |
| Link capacity | Default/explicit, simultaneous enforcement | M1.8 parsing plus M3.5 validator undirected overflow tests | EVIDENCED |
| Visualization | Clear positions/movement/colors/capacity | `--visual` terminal mode covers positions/movement/colors/static capacity with ANSI/256-color swatches and optional metrics; `--capacity-info` live occupancy remains next seam | IN_PROGRESS |
| Basic scenarios | Single/multiple/maps/output/stationary omission | M3.6 known-route exact output tests plus M6.2 CLI/application tests | IN_PROGRESS |
| Termination | Stop exactly after all delivered | M3.6 known-route output closure test | EVIDENCED |
| Valid paths | Linear/multiple/bottleneck/types | M2.1-M2.6 graph/A* matrix plus M3.5 validator tests | EVIDENCED |
| Conflicts | Competition/simultaneous/restricted | M3.5 validator, M4 scheduler, and M5 route-selection tests | EVIDENCED |
| Efficiency | 10+ drones, complex graphs, reasonable compute | M5-D benchmark runner, official suite, and dense candidate guard | EVIDENCED |
| Explanation | Complexity, design, capacity/optimization trade-offs | M5 closure report; README still needs final evaluator polish | IN_PROGRESS |
| Easy benchmarks | Category <10; targets 6/8/6 with 2/4/4 drones | M5-D: 4/4/4 turns, validator-clean | EVIDENCED |
| Medium benchmarks | 10-30; targets 12/15/12 with 5/6/5 | M5-D: 8/10/6 turns, validator-clean | EVIDENCED |
| Hard benchmarks | <60; targets 30/35/45 with 8/12/15 | M5-D: 13/16/26 turns, validator-clean | EVIDENCED |
| Edge cases | Single, bottleneck, disconnected, invalid links, zero/high capacity | Parser edge cases plus M2.6 blocked/loop/dead-end path tests | IN_PROGRESS |
| Error handling | Clear invalid/disconnected errors | Parser errors, M2.6 `NoRouteError`, and M6.2 CLI stderr/exit-code tests | IN_PROGRESS |
| Code quality | Structure, comments/docs/style, visual integration | Raw default `flake8 .`, mypy strict, Ponytail | IN_PROGRESS |
| Live coding | Add `--capacity-info` output within 10 minutes | Rehearsal record | NOT_STARTED |
| Bonus performance | Meet/beat every individual target | M5-D official suite table | EVIDENCED |
| Challenger | Beat 45 turns, meaning <=44 | M5-D valid schedule is 43 turns | EVIDENCED |
| Generalization | Avoid obvious overfit to known map names/prefix route windows | M5-C non-prefix/renaming tests plus M5-D dense-route guard | EVIDENCED |

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
