# Backend context

Implement only the currently approved vertical slice. Read the root `AGENTS.md` first.

## Intended package layout

Create packages only when their first real behavior is implemented:

```text
backend/src/flyin/
  domain/
  parsing/
  pathfinding/
  scheduling/
  simulation/
  application/
  events/
  adapters/cli/
  adapters/api/        # API phase only
```

Do not pre-create empty interfaces, repositories, factories, services, DTOs, or event classes.
Ponytail should challenge every new abstraction. OOP is mandatory, but OOP does not mean a
class per function or inheritance without substitutable implementations.

## Python rules

- Python 3.12 or later.
- Full annotations and `mypy --strict` compatibility.
- Immutable dataclasses/value objects where mutation is not part of the model.
- Explicit domain exceptions; adapters translate them to CLI/API errors.
- No `Any` escape hatches without a documented, narrow boundary.
- No framework imports inside domain, pathfinding, scheduling, or simulation.
- Deterministic algorithms: stable iteration and tie-breaking by explicit keys.
- Avoid global mutable state.
- Keep stdout pure in the mandatory CLI; use stderr/logging for diagnostics.

## Algorithm changes

Every non-trivial algorithm must include:

- invariant or contract;
- worst-case time and space complexity;
- deterministic tie-break rule;
- focused test including the failure mode it prevents;
- benchmark comparison when it touches route choice or scheduling.

Never optimize against a single provided map by name or coordinates.
