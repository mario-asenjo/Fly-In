# Test and verification strategy

## Test pyramid adapted to Fly-In

### Unit/contract tests

- Parser line/token/metadata/error rules.
- Domain invariants and capacity semantics.
- Graph adjacency and custom shortest-path behavior.
- Reservation-table operations.
- Atomic turn transition.
- Event envelope/projection reducer.

### Integration tests

- File -> parser -> solver -> schedule validator.
- CLI exit/stdout/stderr contract.
- FastAPI request -> application -> DTO/error mapping.
- SSE sequence and reconnection.

### End-to-end tests

- Clean invocation on a representative map.
- Later: React submit -> result/playback.

Keep end-to-end cases few; algorithms receive richer focused tests.

## Independent schedule validator

The validator must consume the initial map and produced movement plan without reusing planner
decisions. It checks:

- known drones/zones/links;
- adjacency and blocked zones;
- legal state transitions;
- restricted transit duration and mandatory arrival;
- same-turn zone capacity after departures;
- shared link capacity;
- no movement after delivery;
- every drone delivered;
- no extra turns/output after completion.

This prevents the planner and simulator from sharing the same mistaken assumption unchallenged.

## Parser matrix

Valid:

- minimal map;
- comments/blanks before `nb_drones`;
- negative coordinates;
- metadata in different order;
- all zone types;
- arbitrary single-word color;
- larger zone/link capacity;
- terminal `max_drones` accepted but ignored;
- inline comments if chosen by decision.

Invalid:

- absent/non-positive/duplicate drone declaration;
- missing/duplicate start or end;
- duplicate zone name;
- non-integer coordinate;
- dash/space in name;
- unknown/duplicate/malformed metadata;
- invalid zone type;
- zero/negative/non-integer capacity;
- connection to a later/unknown zone;
- duplicate reversed connection;
- self-loop under current policy;
- disconnected start/end handled gracefully.

## Simulation matrix

- one drone linear;
- pipeline of multiple drones through capacity-one zones;
- same-turn leave/enter;
- capacity-N concurrent entry;
- link capacity one/N;
- opposing link movement;
- one/multiple restricted transitions;
- reserved destination fills before arrival attempt;
- strategic wait;
- fork distribution;
- dead end and loop avoidance;
- unreachable map;
- deterministic tie.

## Property/invariant testing

Property-based libraries are optional, not required. Start with parameterized examples. If many
state combinations expose repeated blind spots, add a property-testing dependency via ADR. Useful
properties:

- occupancy never exceeds capacity;
- delivered count never decreases;
- each drone is in exactly one state;
- event sequence strictly increases;
- identical input produces identical plan;
- reversing stored undirected edge lookup preserves capacity identity.

## Quality commands

Canonical local gate:

```bash
python scripts/validate-context.py
flake8 .
mypy .
pytest
```

Benchmarking is separate so normal correctness tests remain fast:

```bash
python -m flyin.devtools.benchmark maps/maps-v1.5-added-before-m0
```

The benchmark command is a target interface to implement during M5, not present initially.

## Coverage policy

Coverage identifies blind spots; it is not a score target. Critical parser branches, capacity
conflicts, restricted state transitions, and error mapping must be directly asserted. Do not add
meaningless tests to reach a percentage.

## Regression protocol

1. Add the smallest failing public-behavior test.
2. Confirm it fails for the expected reason.
3. Fix the shared/root cause.
4. Run narrow and full gates.
5. Keep the regression test permanently.
