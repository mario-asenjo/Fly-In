# CLI contract

Status: target mandatory adapter behavior; confirm exact executable name with project conventions.

## Proposed invocation

```bash
./main.py map.txt
```

or installed development entry point:

```bash
fly-in map.txt
```

The evaluator-facing wrapper may be added once repository expectations are confirmed.

## Default stdout

- Movement lines only.
- One line per turn.
- Tokens separated by one space.
- Tokens ordered by ascending drone ID.
- No banner, timing, colors, debug, warnings, blank separators, or summary.

## stderr and exit codes

Suggested stable policy:

| Result | Exit | stdout | stderr |
| --- | ---: | --- | --- |
| Valid completed simulation | 0 | movement lines | empty by default |
| Invalid map/arguments | 2 | empty | concise line-aware error |
| Unsolvable/disconnected | 3 | empty | clear cause |
| Unexpected internal error | 1 | empty | safe message; debug stack only in developer mode |

Confirm evaluator expectations before freezing numeric codes; the stdout isolation is more
important than the exact non-zero number.

## Optional flags by phase

- `--visual`: colored human view; must not change domain computation.
- `--capacity-info`: rubric live-coding behavior.
- `--metrics`: optional secondary metrics.
- `--debug`: developer diagnostics to stderr/logging.

Do not add flags before a real consumer/milestone.

## Architecture seam

```text
parse args -> read text -> application solve -> SimulationResult
                                      -> MandatoryOutputFormatter -> stdout
                                      -> VisualFormatter -> human output
                                      -> CapacityFormatter -> diagnostic output
```

The simulator returns data/events, never prints. Exact-output integration tests capture both stdout
and stderr.
