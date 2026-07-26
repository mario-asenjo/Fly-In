# Interpreted domain contract

This document converts Fly-In 1.5 into testable invariants. Labels distinguish direct facts
from interpretations or engineering decisions.

## Input contract

### Significant lines

- **FACT**: comments start with `#` and are ignored.
- **FACT**: `nb_drones: <positive_integer>` defines the number of drones.
- **INTERPRETATION**: `nb_drones` must be the first non-empty, non-comment line because supplied
  maps contain title comments before it.
- **DECISION**: accept blank and full-line comment lines anywhere. Support inline comments only
  when stripping them is unambiguous; cover behavior with tests.
- Errors report physical 1-based line number and a stable human-readable cause.

### Zones

Syntax:

```text
start_hub: <name> <x> <y> [metadata]
end_hub: <name> <x> <y> [metadata]
hub: <name> <x> <y> [metadata]
```

Invariants:

- Exactly one start and one end.
- Names are unique.
- Coordinates are integers; duplicate coordinates are not forbidden by the subject.
- Names contain neither dash nor whitespace.
- Zone type is one of `normal`, `blocked`, `restricted`, `priority`.
- Default type is `normal`.
- Default regular-zone capacity is one.
- Explicit capacity is a positive integer.
- Start and end capacity is unlimited. A non-empty raw `max_drones` value on them is preserved but
  ignored without numeric validation, as required by Fly-In 1.5 section VII.4.
- Color is optional, defaults to none, and accepts any valid single-word value.
- Metadata tag order is irrelevant.
- **DECISION**: preserve source metadata needed for visualization, but keep effective terminal
  capacity distinct from declared ignored capacity for diagnostics.

### Connections

Syntax:

```text
connection: <zone1>-<zone2> [max_link_capacity=<positive_integer>]
```

Invariants:

- Both zones were defined earlier in the file.
- Connection is bidirectional.
- Default link capacity is one.
- Explicit link capacity is positive.
- `a-b` and `b-a` are the same edge and cannot both appear.
- **INTERPRETATION**: link capacity is shared by simultaneous traversals in both directions.
- **DECISION**: store a canonical unordered identity for equality and a directed traversal for
  movement/output.
- Self-loops are not specified; default policy is reject with a clear error until clarified.

### Metadata strictness

- **FACT**: listed metadata blocks must be syntactically valid.
- **INTERPRETATION**: unknown metadata keys are rejected rather than silently ignored, because
  typos otherwise change routing/capacity invisibly.
- Repeated keys in one block are rejected.
- Metadata brackets must be balanced and contain `key=value` tokens.

## Graph contract

- The graph implementation is custom and object-oriented.
- Blocked zones may exist in the parsed graph for visualization but are absent from traversable
  adjacency.
- The start must be able to reach the end through traversable zones; otherwise return a clear
  unsolvable/disconnected result, not an infinite simulation.
- Movement cost is directional because it is determined by the destination zone:
  - normal: 1;
  - priority: 1 and favored when otherwise equivalent;
  - restricted: 2;
  - blocked: infinite/not traversable.
- Priority is a preference, not permission to choose a slower global plan blindly.

## Drone state machine

Each drone is in exactly one state:

1. `AT_ZONE(zone_id)`
2. `IN_TRANSIT(connection_id, origin, destination, arrival_turn)`
3. `DELIVERED`

Transitions:

```text
AT_ZONE --cost 1--> AT_ZONE or DELIVERED
AT_ZONE --restricted destination--> IN_TRANSIT
IN_TRANSIT --next turn--> AT_ZONE or DELIVERED
```

A delivered drone never moves again and is omitted from tracking/output.

## Turn semantics

The simulator uses an atomic turn plan. A safe conceptual order is:

1. Identify transit arrivals due this turn.
2. Determine candidate departures for at-zone drones.
3. Reserve link use and mandatory future restricted arrivals.
4. Count departures as releasing origin capacity in this turn.
5. Validate all arrivals/entries against effective post-departure capacity.
6. Validate total undirected link usage against capacity.
7. Apply the complete turn atomically.
8. Emit movement facts and snapshot/metrics.

No sequential “move one drone and mutate immediately” implementation may make correctness
depend on drone iteration order.

## Restricted movement

- Entering a restricted destination costs two turns.
- First turn output identifies the connection while the drone is in flight.
- On the following turn it must arrive and output the destination zone.
- It cannot remain on the connection waiting for capacity.
- Therefore, departure is legal only if destination capacity is reserved for the required
  arrival turn.
- The connection is occupied during transit as required by the subject. Tests must define the
  exact two-turn reservation window before optimizing.

## Capacity invariants

For every applied turn:

```text
regular_zone_occupancy <= effective_max_drones
undirected_connection_usage <= max_link_capacity
```

Start/end occupancy is unlimited. Multiple entries into a capacity-N zone in the same turn are
legal up to N after outgoing releases. Simultaneous swapping across an edge is legal only if
the shared link capacity permits both traversals and zone post-state capacities remain valid.

## Output contract

- One line represents one turn.
- Tokens are space-separated.
- Zone arrival/move token: `D<ID>-<zone>`.
- In-transit token: `D<ID>-<connection>`.
- Stationary drones are omitted.
- Simulation stops after all drones are delivered.
- **DECISION**: stable output ordering by ascending drone ID.
- **OPEN**: exact directed/canonical textual name for an in-flight connection must be tested
  against evaluator expectations. Default proposal is `<origin>-<destination>`.
- Mandatory stdout contains movement lines only. Human visualization/metrics use an explicit
  flag, stderr, or a separate adapter.

## Schedule validity versus quality

Validity is binary and checked independently. Optimization metrics are separate:

- makespan/total turns (primary);
- moved drones per turn;
- average turns per drone;
- total weighted path cost;
- compute time and explored search states (developer metrics).

A faster invalid schedule always loses to a slower valid one.
