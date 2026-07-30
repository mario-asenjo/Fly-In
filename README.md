*This project has been created as part of the 42 curriculum by masenjo.*

# Fly-In

Fly-In 1.5 implementation in Python with a typed, object-oriented domain core, a custom graph/pathfinding stack, a deterministic capacity-aware scheduler, and an evaluator-safe CLI.

The mandatory CLI is the first-class product. Later API, events, and React work are planned as adapters over the same application service, not as rewrites of the routing or simulation core.

## Current state

Implemented and verified:

- Fly-In 1.5 parser with line-aware errors, comments, metadata, zone types, capacities, duplicate-link checks, and immutable typed map objects.
- Custom traversable graph and exact A* one-drone pathfinding using only the Python standard library (`heapq`), with destination movement costs and deterministic priority tie-breaks.
- Deterministic simulation engine with explicit drone states, two-turn restricted transit, delivered-drone removal, and exact evaluator movement tokens.
- Independent schedule validator for movement legality, blocked traversal, zone capacity, link capacity, delivered-drone immobility, and restricted arrivals.
- Capacity-aware route allocation over bounded candidate paths, with deadlock fallback and measured benchmark improvements.
- Application service `FlyInSolver` that parses text, schedules, validates, and returns adapter-neutral result projections.
- CLI adapter via `python -m flyin` / `make run` that prints movement lines only by default.
- Optional terminal presentation flags: `--visual` and `--capacity-info`.

Intentionally not started yet:

- FastAPI adapter.
- Typed event catalog.
- React UI.
- External broker/worker architecture.

## Requirements

- Python 3.12 or newer.
- `uv` for dependency management.
- GNU Make-compatible `make`.

Development dependencies are declared in `pyproject.toml` under the `dev` extra. The production package currently has no runtime third-party dependencies.

## Install

From the repository root:

```bash
make install
```

This runs:

```bash
uv sync --extra dev
```

The Makefile stores the uv virtual environment outside the repository at `../.flyin-venv` through `UV_PROJECT_ENVIRONMENT`, so the mandatory raw `flake8 .` command does not scan a checked-in or repo-local virtualenv.

## Run the evaluator CLI

Default mode prints exactly one line per simulation turn and only movement tokens on stdout:

```bash
make run ARGS=maps/maps-v1.5-added-before-m0/easy/01_linear_path.txt
```

Equivalent direct command:

```bash
uv run --extra dev python -m flyin maps/maps-v1.5-added-before-m0/easy/01_linear_path.txt
```

Example output for the official easy linear map:

```text
D1-waypoint1
D1-waypoint2 D2-waypoint1
D1-goal D2-waypoint2
D2-goal
```

Diagnostics and errors are written to stderr. Default successful output has no banner, colors, metrics, warnings, or blank separators.

## Debug and presentation modes

Colored terminal view:

```bash
make run ARGS="--visual maps/maps-v1.5-added-before-m0/easy/01_linear_path.txt"
```

This explicit mode renders zones, coordinates, source colors, static capacities, connections, turn-by-turn movement, and optional subject metrics. `color=rainbow` is rendered character-by-character in the terminal adapter.

Capacity diagnostics / live-coding seam:

```bash
make run ARGS="--capacity-info maps/maps-v1.5-added-before-m0/easy/01_linear_path.txt"
```

This explicit mode keeps the movement lines and appends per-turn zone/link usage diagnostics. It is intentionally not part of the default evaluator stdout.

Debug with pdb:

```bash
make debug ARGS=maps/maps-v1.5-added-before-m0/easy/01_linear_path.txt
```

## Quality gates

Run all regular tests:

```bash
make test
```

Run mandatory lint/type checks:

```bash
make lint
```

Run strict type checks:

```bash
make lint-strict
```

Validate project context and source/hash rules:

```bash
make context
```

Full local quality gate:

```bash
make quality
```

Before a slice is called complete, the project contract requires fresh evidence for relevant tests, lint/type checks, context validation, progress docs, and Ponytail review.

## Benchmark evidence

The benchmark runner is developer-only and lives outside the application package:

```bash
UV_PROJECT_ENVIRONMENT=$(pwd)/../.flyin-venv uv run --extra dev python -m scripts.benchmark_official_maps
```

Current documented M5-D results on the official Fly-In 1.5 map package are validator-clean:

| Category | Current turns |
| --- | --- |
| Easy | 4 / 4 / 4 |
| Medium | 8 / 10 / 6 |
| Hard | 13 / 16 / 26 |
| Challenger | 43 |

The detailed benchmark ledger and map hashes live in `docs/progress/BENCHMARKS.md` and `docs/progress/M5_CLOSURE.md`.

## Architecture

Dependency direction points inward:

```text
adapters/cli -> application -> parsing/pathfinding/scheduling/simulation -> domain
```

Key boundaries:

- `domain`: immutable entities/value objects and invariants.
- `parsing`: text-to-domain conversion with line-aware errors.
- `pathfinding`: custom graph and route discovery; no graph/pathfinding library.
- `scheduling`: capacity reservations, route allocation, and deadlock fallback.
- `simulation`: deterministic turn facts, state transitions, validation, and token formatting.
- `application`: adapter-neutral solve use case and projections.
- `adapters/cli`: argument parsing, file I/O, stdout/stderr policy, and terminal presentation.

No NetworkX, `graphlib`, FastAPI, React, broker, or visualization dependency is used by the domain/core scheduler.

## Source hierarchy

When sources disagree, use this order:

1. `docs/sources/flyin_1.5.pdf` - current normative subject.
2. `docs/sources/Intra-Projects-Fly-in-Edit.pdf` - evaluation rubric.
3. `maps/maps-v1.5-added-before-m0/` - official Fly-In 1.5 map package.
4. `maps/provided-v12-snapshot/` - historical v1.2 comparison snapshot.
5. `docs/sources/fly-in_1.2.pdf` - historical comparison only.
6. `maps/provided-v12-snapshot/README_maps.md` - non-normative historical helper documentation.

Never silently resolve contradictions. Record them in `docs/progress/OPEN_QUESTIONS.md`, choose the safest testable interpretation, and keep the decision reversible.

## AI and resources

Hermes Agent is used as a pair-programming assistant for planning, implementation, tests, documentation, review, and project tracking. Project state is stored in versioned files under `docs/progress/`; global assistant memory is not used as the project database.

Ponytail minimalism review is active for coding work. It rejects speculative abstractions, unnecessary dependencies, and future-facing scaffolding, but it does not override the Fly-In subject, evaluation rubric, correctness, type safety, or tests.

## Repository map

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Always-loaded project operating contract |
| `backend/src/flyin/` | Python implementation |
| `tests/` | Unit, integration, official-map, and regression tests |
| `docs/project/` | Source hierarchy, architecture, roadmap, contracts, evaluation matrix, `--capacity-info` walkthrough |
| `docs/progress/` | Current state, benchmarks, session log, risks, open questions |
| `docs/sources/` | Supplied subject/evaluation PDFs, retained unchanged |
| `maps/maps-v1.5-added-before-m0/` | Official Fly-In 1.5 maps, retained unchanged |
| `maps/provided-v12-snapshot/` | Historical v1.2 maps, retained unchanged |
| `scripts/` | Setup, context validation, and benchmark tooling |

## Open evaluation risks

- Q7: exact evaluator text for restricted in-transit tokens. The project currently emits directed `D<ID>-<origin>-<destination>` tokens.
- Q8: exact evaluator expectation for restricted link occupancy during the two-turn transit window.

Both risks are tracked in `docs/progress/OPEN_QUESTIONS.md` and kept visible during defense preparation.
