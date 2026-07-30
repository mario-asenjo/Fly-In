# `--capacity-info` walkthrough with an easy map

Status: M6 rehearsal document for explaining the implemented CLI flag with real data.

Map used for this walkthrough:

```bash
maps/maps-v1.5-added-before-m0/easy/01_linear_path.txt
```

Command used to collect the output:

```bash
make run ARGS='--capacity-info maps/maps-v1.5-added-before-m0/easy/01_linear_path.txt'
```

Real command output:

```text
D1-waypoint1
D1-waypoint2 D2-waypoint1
D1-goal D2-waypoint2
D2-goal
Capacity info:
  Turn 1:
    zone start: 1/unlimited drones
    zone waypoint1: 1/1 drones
    zone waypoint2: 0/1 drones
    zone goal: 0/unlimited drones
    connection start-waypoint1: 1/1 used
    connection waypoint1-waypoint2: 0/1 used
    connection waypoint2-goal: 0/1 used
  Turn 2:
    zone start: 0/unlimited drones
    zone waypoint1: 1/1 drones
    zone waypoint2: 1/1 drones
    zone goal: 0/unlimited drones
    connection start-waypoint1: 1/1 used
    connection waypoint1-waypoint2: 1/1 used
    connection waypoint2-goal: 0/1 used
  Turn 3:
    zone start: 0/unlimited drones
    zone waypoint1: 0/1 drones
    zone waypoint2: 1/1 drones
    zone goal: 1/unlimited drones
    connection start-waypoint1: 0/1 used
    connection waypoint1-waypoint2: 1/1 used
    connection waypoint2-goal: 1/1 used
  Turn 4:
    zone start: 0/unlimited drones
    zone waypoint1: 0/1 drones
    zone waypoint2: 0/1 drones
    zone goal: 2/unlimited drones
    connection start-waypoint1: 0/1 used
    connection waypoint1-waypoint2: 0/1 used
    connection waypoint2-goal: 1/1 used
```

## 1. What the flag is for

`--capacity-info` is an explicit human/debug flag. It exists for explanation and defense, not for the mandatory evaluator stream.

Default command:

```bash
make run ARGS='maps/maps-v1.5-added-before-m0/easy/01_linear_path.txt'
```

prints only movement lines on stdout:

```text
D1-waypoint1
D1-waypoint2 D2-waypoint1
D1-goal D2-waypoint2
D2-goal
```

With `--capacity-info`, the CLI keeps those movement lines first and then appends a diagnostic block. That means the solver behavior is the same; only the adapter output changes.

## 2. Real input map

File contents:

```text
1: # Easy Level 1: Simple linear path
2: nb_drones: 2
3:
4: start_hub: start 0 0 [color=green]
5: hub: waypoint1 1 0 [color=blue]
6: hub: waypoint2 2 0 [color=blue]
7: end_hub: goal 3 0 [color=red]
8:
9: connection: start-waypoint1
10: connection: waypoint1-waypoint2
11: connection: waypoint2-goal
```

Important real facts from the map:

- `nb_drones: 2`, so the solver creates drone IDs `1` and `2`.
- `start` and `goal` are terminal zones, so their capacity is `unlimited`.
- `waypoint1` and `waypoint2` do not declare `max_drones`, so each normal hub gets default capacity `1`.
- Every connection omits `max_link_capacity`, so each connection gets default capacity `1`.
- The graph is linear: `start -> waypoint1 -> waypoint2 -> goal`.

## 3. CLI call chain

Entry point: `backend/src/flyin/adapters/cli.py`.

For this command:

```bash
make run ARGS='--capacity-info maps/maps-v1.5-added-before-m0/easy/01_linear_path.txt'
```

`main()` receives equivalent argv data:

```text
('--capacity-info', 'maps/maps-v1.5-added-before-m0/easy/01_linear_path.txt')
```

Then it does these calls:

1. `argparse.ArgumentParser(...).parse_args(argv)`
   - real `args.map_path`: `maps/maps-v1.5-added-before-m0/easy/01_linear_path.txt`
   - real `args.visual`: `False`
   - real `args.capacity_info`: `True`

2. `Path(args.map_path).read_text(encoding='utf-8')`
   - returns the exact map text shown above.

3. `FlyInSolver.solve_text(source)`
   - this is the adapter-neutral application call.
   - it owns parsing, route allocation, scheduling, validation, metrics, movement lines, and capacity projection.

4. `output_lines = list(result.movement_lines)` because `args.visual` is false.
   - real value:

```python
[
    'D1-waypoint1',
    'D1-waypoint2 D2-waypoint1',
    'D1-goal D2-waypoint2',
    'D2-goal',
]
```

5. Because `args.capacity_info` is true, CLI calls `format_capacity_info(result)` and extends `output_lines` with that returned block.

6. Finally it prints each line to stdout and returns exit code `0`.

## 4. Application call: `FlyInSolver.solve_text(source)`

Implementation file: `backend/src/flyin/application/solver.py`.

The method performs these calls in order.

### 4.1 `MapParser().parse(source)`

Real parsed data:

```python
parsed.drone_count = 2

parsed.start = (
    'start',
    0,
    0,
    'normal',
    'green',
    'unlimited',
)

parsed.hubs = (
    ('waypoint1', 1, 0, 'normal', 'blue', 1),
    ('waypoint2', 2, 0, 'normal', 'blue', 1),
)

parsed.end = (
    'goal',
    3,
    0,
    'normal',
    'red',
    'unlimited',
)

parsed.connections = (
    ('start', 'waypoint1', 1, ('start', 'waypoint1')),
    ('waypoint1', 'waypoint2', 1, ('waypoint1', 'waypoint2')),
    ('waypoint2', 'goal', 1, ('goal', 'waypoint2')),
)
```

The final tuple in each connection row is the physical connection identity. It is sorted by name so reverse duplicates use the same identity. For example, `waypoint2-goal` has identity `('goal', 'waypoint2')` because `goal` sorts before `waypoint2`.

### 4.2 `_warnings(parsed_map)`

For this map, there are no non-fatal warnings:

```python
warnings = ()
```

### 4.3 `RouteAllocator.schedule(parsed_map, max_routes=8, max_turns=1000)`

Implementation file: `backend/src/flyin/scheduling/allocator.py`.

Internally it calls `CandidateRouteFinder.find_candidates(parsed_map, max_routes=8)`.

Real candidate routes:

```python
candidate_routes = (
    (('start', 'waypoint1', 'waypoint2', 'goal'), 3, 0),
)
```

Each row means:

```text
(zone names, route cost, priority score)
```

So there is one route, with cost `3`, and no priority zones.

Then `RouteAllocator.allocate(parsed_map, candidates)` assigns drones round-robin over the candidate list.

Real allocation:

```python
{
    1: ('start', 'waypoint1', 'waypoint2', 'goal'),
    2: ('start', 'waypoint1', 'waypoint2', 'goal'),
}
```

Both drones use the only route.

Then the known-route scheduler creates a capacity-safe schedule.

Real schedule facts:

```python
Turn 1:
    MovementFact:D1:start->waypoint1

Turn 2:
    MovementFact:D1:waypoint1->waypoint2
    MovementFact:D2:start->waypoint1

Turn 3:
    MovementFact:D1:waypoint2->goal
    MovementFact:D2:waypoint1->waypoint2

Turn 4:
    MovementFact:D2:waypoint2->goal
```

Why there are four turns:

- `waypoint1` capacity is `1`, so both drones cannot enter it on turn 1.
- Drone 1 enters `waypoint1` on turn 1.
- On turn 2, Drone 1 leaves `waypoint1` and Drone 2 enters `waypoint1` in the same turn. That is legal because leaving releases capacity before incoming occupancy is checked for the completed turn.
- The same pipeline repeats through `waypoint2` and then `goal`.

### 4.4 `ScheduleValidator.validate(parsed_map, schedule)`

Real result:

```python
validation.is_valid = True
validation.errors = ()
```

This matters because `--capacity-info` is not a second scheduler. It explains the schedule after the authoritative validator has accepted it.

### 4.5 `_turn_views(schedule)`

This builds adapter-safe movement projections for each turn.

Real movement lines produced from the schedule:

```python
result.movement_lines = (
    'D1-waypoint1',
    'D1-waypoint2 D2-waypoint1',
    'D1-goal D2-waypoint2',
    'D2-goal',
)
```

These are the mandatory evaluator lines.

### 4.6 `_capacity_turns(parsed_map, schedule)`

This is the core of `--capacity-info`.

It starts with this location table before turn 1:

```python
locations = {
    1: AtZone(start),
    2: AtZone(start),
}
```

For each turn, it:

1. groups the turn facts by drone ID;
2. applies the movement/transit fact for each drone;
3. counts where drones are after that completed turn;
4. counts connection usage from the facts in that turn;
5. stores a `TurnCapacityView(number, zones, connections)`.

For this easy map there are no restricted zones, so every movement is a normal one-turn `MovementFact`.

Real capacity projection:

```python
Turn 1:
    zones = (
        ('start', 1, 'unlimited'),
        ('waypoint1', 1, 1),
        ('waypoint2', 0, 1),
        ('goal', 0, 'unlimited'),
    )
    connections = (
        ('start', 'waypoint1', 1, 1),
        ('waypoint1', 'waypoint2', 0, 1),
        ('waypoint2', 'goal', 0, 1),
    )

Turn 2:
    zones = (
        ('start', 0, 'unlimited'),
        ('waypoint1', 1, 1),
        ('waypoint2', 1, 1),
        ('goal', 0, 'unlimited'),
    )
    connections = (
        ('start', 'waypoint1', 1, 1),
        ('waypoint1', 'waypoint2', 1, 1),
        ('waypoint2', 'goal', 0, 1),
    )

Turn 3:
    zones = (
        ('start', 0, 'unlimited'),
        ('waypoint1', 0, 1),
        ('waypoint2', 1, 1),
        ('goal', 1, 'unlimited'),
    )
    connections = (
        ('start', 'waypoint1', 0, 1),
        ('waypoint1', 'waypoint2', 1, 1),
        ('waypoint2', 'goal', 1, 1),
    )

Turn 4:
    zones = (
        ('start', 0, 'unlimited'),
        ('waypoint1', 0, 1),
        ('waypoint2', 0, 1),
        ('goal', 2, 'unlimited'),
    )
    connections = (
        ('start', 'waypoint1', 0, 1),
        ('waypoint1', 'waypoint2', 0, 1),
        ('waypoint2', 'goal', 1, 1),
    )
```

Interpretation of one row:

```python
('waypoint1', 1, 1)
```

means:

```text
zone waypoint1 has 1 drone after the completed turn, and its capacity is 1.
```

Interpretation of one connection row:

```python
('start', 'waypoint1', 1, 1)
```

means:

```text
connection start-waypoint1 was used by 1 movement fact in that turn, and its capacity is 1.
```

### 4.7 `_metrics(turns, parsed_map.end.name)`

Real metrics:

```python
MetricsView(
    moved_drones_per_turn=(1, 2, 2, 1),
    average_turns_per_drone=3.5,
    total_path_cost=6,
)
```

These metrics are not required for `--capacity-info`, but they are part of the same `SolveResult` used by visual/debug adapters.

### 4.8 `SolveResult(...)`

The final application object contains all adapter-safe data:

```python
SolveResult(
    parsed_map=parsed_map,
    schedule=schedule,
    map_view=MapView(...),
    turns=TurnView(...),
    capacity_turns=TurnCapacityView(...),
    metrics=MetricsView(...),
    movement_lines=(
        'D1-waypoint1',
        'D1-waypoint2 D2-waypoint1',
        'D1-goal D2-waypoint2',
        'D2-goal',
    ),
    warnings=(),
)
```

The CLI adapter receives this object. It does not receive domain internals directly and does not make scheduling decisions.

## 5. Formatting call: `format_capacity_info(result)`

Implementation file: `backend/src/flyin/adapters/terminal_visual.py`.

The formatter is deliberately boring:

```python
lines = ['Capacity info:']
for turn in result.capacity_turns:
    lines.append(f'  Turn {turn.number}:')
    lines.extend(
        f'    zone {name}: {used}/{capacity} drones'
        for name, used, capacity in turn.zones
    )
    lines.extend(
        f'    connection {left}-{right}: {used}/{capacity} used'
        for left, right, used, capacity in turn.connections
    )
```

It only reads `result.capacity_turns`. It does not parse text, inspect routes, or simulate moves.

For turn 1, this data:

```python
zones = (
    ('start', 1, 'unlimited'),
    ('waypoint1', 1, 1),
    ('waypoint2', 0, 1),
    ('goal', 0, 'unlimited'),
)
connections = (
    ('start', 'waypoint1', 1, 1),
    ('waypoint1', 'waypoint2', 0, 1),
    ('waypoint2', 'goal', 0, 1),
)
```

becomes:

```text
  Turn 1:
    zone start: 1/unlimited drones
    zone waypoint1: 1/1 drones
    zone waypoint2: 0/1 drones
    zone goal: 0/unlimited drones
    connection start-waypoint1: 1/1 used
    connection waypoint1-waypoint2: 0/1 used
    connection waypoint2-goal: 0/1 used
```

## 6. Turn-by-turn explanation

### Turn 1

Movement line:

```text
D1-waypoint1
```

Real fact:

```text
MovementFact:D1:start->waypoint1
```

State after turn:

- Drone 1 moved from `start` to `waypoint1`.
- Drone 2 is still at `start`.
- `waypoint1` is full: `1/1`.
- `start-waypoint1` used `1/1` link capacity.

Printed capacity rows:

```text
zone start: 1/unlimited drones
zone waypoint1: 1/1 drones
zone waypoint2: 0/1 drones
zone goal: 0/unlimited drones
connection start-waypoint1: 1/1 used
connection waypoint1-waypoint2: 0/1 used
connection waypoint2-goal: 0/1 used
```

### Turn 2

Movement line:

```text
D1-waypoint2 D2-waypoint1
```

Real facts:

```text
MovementFact:D1:waypoint1->waypoint2
MovementFact:D2:start->waypoint1
```

State after turn:

- Drone 1 moved from `waypoint1` to `waypoint2`.
- Drone 2 moved from `start` to `waypoint1`.
- `waypoint1` remains `1/1` because D1 left and D2 entered in the same turn.
- `waypoint2` becomes `1/1`.
- Two different links were used once each.

Printed capacity rows:

```text
zone start: 0/unlimited drones
zone waypoint1: 1/1 drones
zone waypoint2: 1/1 drones
zone goal: 0/unlimited drones
connection start-waypoint1: 1/1 used
connection waypoint1-waypoint2: 1/1 used
connection waypoint2-goal: 0/1 used
```

### Turn 3

Movement line:

```text
D1-goal D2-waypoint2
```

Real facts:

```text
MovementFact:D1:waypoint2->goal
MovementFact:D2:waypoint1->waypoint2
```

State after turn:

- Drone 1 reached `goal`.
- Drone 2 moved to `waypoint2`.
- `goal` has unlimited capacity, so `1/unlimited` is allowed.
- `waypoint2` stays `1/1` because D1 left and D2 entered in the same turn.

Printed capacity rows:

```text
zone start: 0/unlimited drones
zone waypoint1: 0/1 drones
zone waypoint2: 1/1 drones
zone goal: 1/unlimited drones
connection start-waypoint1: 0/1 used
connection waypoint1-waypoint2: 1/1 used
connection waypoint2-goal: 1/1 used
```

### Turn 4

Movement line:

```text
D2-goal
```

Real fact:

```text
MovementFact:D2:waypoint2->goal
```

State after turn:

- Drone 2 reached `goal`.
- Both drones are delivered.
- `goal` shows `2/unlimited` for the human diagnostic.
- Only `waypoint2-goal` is used this turn.

Printed capacity rows:

```text
zone start: 0/unlimited drones
zone waypoint1: 0/1 drones
zone waypoint2: 0/1 drones
zone goal: 2/unlimited drones
connection start-waypoint1: 0/1 used
connection waypoint1-waypoint2: 0/1 used
connection waypoint2-goal: 1/1 used
```

## 7. Why this is evaluator-safe

The important boundary is in the CLI adapter:

```python
output_lines = list(
    format_visual_result(result) if args.visual else result.movement_lines
)
if args.capacity_info:
    output_lines.extend(format_capacity_info(result))
```

So:

- no flag: `result.movement_lines` only;
- `--visual`: human visualization instead of evaluator lines;
- `--capacity-info`: explicit diagnostic block appended;
- the domain, scheduler, and validator do not know about stdout formatting.

The tests lock this behavior:

- `test_cli_capacity_info_prints_diagnostics_without_default_stdout` checks the flag prints `Capacity info:` and the default command does not.
- `test_application_service_exposes_capacity_projection` checks the real capacity rows exist on the application result.
- `test_capacity_projection_skips_restricted_arrival_link` protects the restricted-transit edge case found during review.

## 8. Short defense script

If asked to explain `--capacity-info`, say:

> The mandatory output is still `movement_lines`; `--capacity-info` is opt-in. The CLI reads the map, calls `FlyInSolver.solve_text()`, and the solver returns one immutable `SolveResult`. Inside it, `capacity_turns` is a replay of the already validated schedule: after each turn we count zone occupancy and link usage, then the terminal adapter formats those rows. The formatter does not re-schedule or re-parse anything, so it cannot change the answer. On `easy/01_linear_path.txt`, two drones pipeline through two capacity-1 waypoints in four turns: turn 2 shows `waypoint1: 1/1` and `waypoint2: 1/1` because D1 leaves waypoint1 while D2 enters it in the same turn.
