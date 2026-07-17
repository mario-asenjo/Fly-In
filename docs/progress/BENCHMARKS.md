# Benchmark ledger

No solver exists yet. Never add estimated/fabricated results.

## Fly-In 1.5 targets

| Category | Map | Drones | Target turns | Current turns | Validated | Map hash |
| --- | --- | ---: | ---: | ---: | --- | --- |
| Easy | Linear path | 2 | 6 | - | No | pending v1.5 refresh |
| Easy | Simple fork | 4 | 8 | - | No | pending v1.5 refresh |
| Easy | Basic capacity | 4 | 6 | - | No | pending v1.5 refresh |
| Medium | Dead end trap | 5 | 12 | - | No | pending v1.5 refresh |
| Medium | Circular loop | 6 | 15 | - | No | pending v1.5 refresh |
| Medium | Priority puzzle | 5 | 12 | - | No | pending v1.5 refresh |
| Hard | Maze nightmare | 8 | 30 | - | No | pending v1.5 refresh |
| Hard | Capacity hell | 12 | 35 | - | No | pending v1.5 refresh |
| Hard | Ultimate challenge | 15 | 45 | - | No | pending v1.5 refresh |
| Challenger | Impossible Dream | 25 | <45 | - | No | pending v1.5 refresh |

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
