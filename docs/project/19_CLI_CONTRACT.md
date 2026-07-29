# CLI contract

Status: implemented mandatory adapter behavior through `python -m flyin` and `make run ARGS=...`.

## Implemented invocation

```bash
make run ARGS=map.txt
```

or direct development entry point:

```bash
uv run --extra dev python -m flyin map.txt
```

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

## Optional flags

- `--visual`: colored human view using `MapView` / `TurnView`; must not change domain computation
  or default evaluator stdout.
- `--capacity-info`: explicit capacity diagnostic mode for rubric live-coding rehearsal. It appends
  per-turn zone/link capacity use and is never emitted by default.
- Visual mode includes optional secondary metrics.
- `--debug`: developer diagnostics to stderr/logging.

## Architecture seam

```text
parse args -> read text -> application solve -> SimulationResult
                                      -> MandatoryOutputFormatter -> stdout
                                      -> VisualFormatter -> human output
                                      -> CapacityFormatter -> diagnostic output
```

The simulator returns data/events, never prints. Exact-output integration tests capture both stdout
and stderr.

## Implemented visual mode

`python -m flyin --visual map.txt` switches from evaluator output to a human terminal view. It prints
map metadata, zone coordinates, zone capacities, source `color=<value>` metadata, and turn-by-turn
movements with known color names rendered through ANSI/256-color escape codes plus a colored swatch
next to each zone. Connection text colors each endpoint with that endpoint's zone color instead of
painting the whole edge as one color. Unknown valid single-word color values are preserved as text
metadata even when the terminal adapter cannot map them to an ANSI code.
The special `rainbow` visual color is rendered character-by-character with a repeating ANSI palette.

It also prints the optional subject metrics already derivable from the solved schedule: drones moved
per turn, average delivery turn per drone, and total weighted path cost. Restricted destination moves
count once as cost 2 on departure; their later arrival fact is visual progress, not an additional path
cost.


## Implemented capacity-info mode

`python -m flyin --capacity-info map.txt` prints the normal evaluator movement lines first, then a
`Capacity info:` block with per-turn rows such as:

```text
zone waypoint: 1/1 drones
connection start-waypoint: 1/1 used
```

The data comes from the validated `SolveResult.capacity_turns` projection, not from reparsing in the
CLI. Regular zone counts represent post-turn occupancy. Delivered drones are counted against the end
hub's unlimited sink for human diagnostics; they are still removed from authoritative scheduling.
