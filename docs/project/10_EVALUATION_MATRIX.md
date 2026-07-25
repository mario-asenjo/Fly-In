# Evaluation matrix

Status values: `NOT_STARTED`, `IN_PROGRESS`, `EVIDENCED`, `BLOCKED`.
Only mark `EVIDENCED` with a test, command, file, or demonstrated output.

| Rubric area | Required behavior/evidence | Planned evidence | Status |
| --- | --- | --- | --- |
| README | First line, description, instructions, resources/AI use, algorithm, visual docs, example | Root README review | IN_PROGRESS |
| OOP | Proper separation/encapsulation, justified inheritance only | Package design + explanation | NOT_STARTED |
| Type safety | `mypy .` no errors/full hints | CI/local command log | NOT_STARTED |
| Custom graph | No forbidden graph library; explain implementation | Dependency audit + graph tests | NOT_STARTED |
| Parser valid input | Drone count, zone prefixes, connections, defaults, comments | M1.1-M1.2 topology + M1.3 comments/blanks + M1.4 raw metadata/default/order tests | IN_PROGRESS |
| Parser errors | Malformed, invalid types, missing terminals, capacity, duplicates | Error matrix tests | NOT_STARTED |
| Zone occupancy | Default/explicit capacity, start/end unlimited, same-turn releases | Validator/simulator tests | NOT_STARTED |
| Movement cost | Normal/priority 1, restricted 2, blocked inaccessible | State-transition tests | NOT_STARTED |
| Link capacity | Default/explicit, simultaneous enforcement | Reservation tests | NOT_STARTED |
| Visualization | Clear positions/movement/colors/capacity | Terminal demo then React | NOT_STARTED |
| Basic scenarios | Single/multiple/maps/output/stationary omission | CLI integration tests | NOT_STARTED |
| Termination | Stop exactly after all delivered | CLI/simulator test | NOT_STARTED |
| Valid paths | Linear/multiple/bottleneck/types | Planner + validator tests | NOT_STARTED |
| Conflicts | Competition/simultaneous/restricted | Scheduler tests | NOT_STARTED |
| Efficiency | 10+ drones, complex graphs, reasonable compute | Benchmark report | NOT_STARTED |
| Explanation | Complexity, design, capacity/optimization trade-offs | README + defense notes | NOT_STARTED |
| Easy benchmarks | Category <10; targets 6/8/6 with 2/4/4 drones | Fresh benchmark table | NOT_STARTED |
| Medium benchmarks | 10-30; targets 12/15/12 with 5/6/5 | Fresh benchmark table | NOT_STARTED |
| Hard benchmarks | <60; targets 30/35/45 with 8/12/15 | Fresh benchmark table | NOT_STARTED |
| Edge cases | Single, bottleneck, disconnected, invalid links, zero/high capacity | Edge-case suite | NOT_STARTED |
| Error handling | Clear invalid/disconnected errors | CLI/API tests | NOT_STARTED |
| Code quality | Structure, comments/docs/style, visual integration | Review + lint | NOT_STARTED |
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
