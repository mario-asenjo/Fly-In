*This project has been created as part of the 42 curriculum by masenjo.*

# Fly-In

Starter repository for the Fly-In 1.5 project and its Hermes-assisted development workflow.

This archive deliberately contains project context, source snapshots, agent skills, plans,
quality gates, and empty implementation areas. It does not contain a generated solution.
The objective is to let the learner implement and understand every mandatory part while
Hermes maintains continuity between sessions.

## Start here

1. Install and configure Hermes Agent.
2. From this repository, run:

   ```bash
   bash scripts/setup-hermes.sh
   ```

   Native Windows users can run:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\scripts\setup-hermes.ps1
   ```

   If this is a dedicated Fly-In Hermes profile/home, add `--install-soul` on Bash or
   `-InstallSoul` on PowerShell after reviewing `hermes/SOUL.flyin.md`.

4. Restart Hermes because Ponytail is installed as a Hermes plugin.
5. Open Hermes with this repository as the working directory.
6. Send the exact first message from [docs/prompts/FIRST_SESSION.md](docs/prompts/FIRST_SESSION.md).

The short version is:

> Vamos a implementar Fly-In. Lee el contexto del repositorio, realiza el protocolo de
> inicio de sesión, dime en qué estado real estamos y propón únicamente el primer vertical
> slice. No escribas código hasta que aprobemos juntos su alcance y criterios de aceptación.

## Source hierarchy

When sources disagree, use this order:

1. `docs/sources/flyin_1.5.pdf` - current normative subject.
2. `docs/sources/Intra-Projects-Fly-in-Edit.pdf` - actual evaluation rubric.
3. `maps/maps-v1.5-added-before-m0/` - official Fly-In 1.5 map package.
4. `maps/provided-v12-snapshot/` - historical v1.2 comparison snapshot.
5. `docs/sources/fly-in_1.2.pdf` - historical comparison only.
6. `maps/provided-v12-snapshot/README_maps.md` - non-normative historical helper documentation.

Never silently resolve a contradiction. Record it in
[docs/progress/OPEN_QUESTIONS.md](docs/progress/OPEN_QUESTIONS.md), choose the safest
testable interpretation, and keep the decision reversible.

## Intended architecture

The target is an evolutionary modular monolith:

1. Pure Python domain, parser, custom graph, pathfinding, scheduling, simulator, and CLI.
2. Typed in-process domain events.
3. FastAPI REST API with generated OpenAPI documentation.
4. React + TypeScript visualization.
5. Server-Sent Events first; WebSocket only if bidirectional live control becomes necessary.
6. An external broker/worker only after the mandatory project and benchmarks are solid.

The CLI remains a first-class adapter and must preserve the subject's exact movement output.
The algorithm must never depend on FastAPI, React, a broker, or a visualization library.

## Hermes and Ponytail

Hermes automatically reads the root `AGENTS.md` and discovers the nested `AGENTS.md` files
when it enters `backend/`, `frontend/`, `tests/`, or `docs/`.

Project skills live under `.agents/skills/`. The setup scripts register that directory as a
Hermes external skill directory and install the matching bundles.

Ponytail is installed from its official repository:

```bash
hermes plugins install DietrichGebert/ponytail --enable
```

Ponytail is the minimalism guard: it challenges speculative abstractions and unnecessary
dependencies. It does not override the Fly-In subject, evaluation rubric, correctness,
type safety, tests, security, accessibility, or explicit project decisions.

## Repository map

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Always-loaded project operating contract |
| `.agents/skills/` | On-demand Fly-In workflows for Hermes |
| `.agents/skill-bundles/` | Short commands for recurring development modes |
| `docs/project/` | Normative interpreted specification and global plan |
| `docs/decisions/` | Architecture Decision Records |
| `docs/progress/` | Current state, session ledger, risks, benchmarks, open questions |
| `docs/prompts/` | First-session, normal-session, review, and handoff prompts |
| `docs/sources/` | Supplied subjects and evaluation sheet |
| `maps/maps-v1.5-added-before-m0/` | Official Fly-In 1.5 maps, retained unchanged |
| `maps/provided-v12-snapshot/` | Historical v1.2 maps, retained unchanged |
| `tests/fixtures/derived-v15/` | Clearly marked local fixtures for v1.5 benchmark assumptions |
| `backend/` | Mandatory Python implementation and later API |
| `frontend/` | React UI, created only in the UI phase |
| `hermes/` | Global Hermes templates and integration notes |
| `scripts/` | Setup and deterministic context validation |

## Mandatory quality gates

Before a slice is called complete:

- Its acceptance tests pass.
- Existing tests pass.
- `mypy` passes without errors.
- `flake8` passes without errors.
- No graph library was introduced.
- CLI stdout remains evaluator-safe.
- Relevant progress and decision files are updated.
- Ponytail reviews the diff for avoidable complexity.
- Hermes explains what changed, why, evidence, and the next smallest step.

## Current state

The parser represents terminals, regular hubs, coordinates, structurally valid undirected
connections, full-line/inline comments, and canonical raw metadata. Metadata semantics, the
complete error model, pathfinding, simulation, and the real CLI remain deliberately unimplemented. See
[docs/project/05_ROADMAP.md](docs/project/05_ROADMAP.md) and
[docs/progress/CURRENT.md](docs/progress/CURRENT.md).
