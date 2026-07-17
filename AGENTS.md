# Fly-In project operating contract

## Mission

Develop Fly-In 1.5 incrementally, correctly, and explainably. The learner must understand
and be able to defend every important line. Build the mandatory CLI project first, then
evolve the same domain core toward typed events, a FastAPI API, and a React UI without
rewriting the domain.

Communicate with Mario in Spanish unless he asks otherwise. Use English for identifiers,
source-code comments, docstrings, commit messages, and the final evaluator-facing README.

## Session start protocol

At the beginning of every new session:

1. Read `docs/progress/CURRENT.md`.
2. Read `docs/progress/OPEN_QUESTIONS.md` and `docs/progress/DECISION_LOG.md`.
3. Inspect `git status` and the latest relevant diff; never assume the working tree is clean.
4. Read only the project documents relevant to the requested phase.
5. State the current milestone, verified state, open risk, and proposed smallest next step.
6. Do not implement until the user approves scope when the request is exploratory.
7. Activate Ponytail in `full` mode for coding work. Use `ultra` only when explicitly asked.

Do not turn global Hermes MEMORY into a project database. Durable project state belongs in
versioned files under `docs/progress/`; global memory stores only compact pointers and stable
user/environment preferences.

## Source of truth

Read `docs/project/02_SOURCE_OF_TRUTH.md` before resolving requirements. In short:

1. Fly-In subject 1.5.
2. Intra evaluation rubric.
3. Official Fly-In 1.5 map package at `maps/maps-v1.5-added-before-m0/`.
4. Supplied v1.2 map contents for historical comparison only.
5. Subject 1.2 for historical comparison only.
6. Historical map README as non-normative guidance.

Never modify files in `docs/sources/`, `maps/maps-v1.5-added-before-m0/`, or
`maps/provided-v12-snapshot/`. Add derived test data under `tests/fixtures/` with provenance and
the assumption stated in a leading comment.

## Non-negotiable product rules

- Python implementation must be completely object-oriented and type-safe.
- `mypy` and `flake8` are mandatory gates.
- Do not use NetworkX, graphlib, or any library that implements graph/pathfinding logic.
- Start and end zones have unlimited occupancy; ignore their `max_drones` metadata without
  treating it as an error.
- Connections are bidirectional; reversed duplicates are duplicates.
- Movement cost is based on the destination zone.
- A restricted destination costs two turns; transit cannot wait for destination capacity.
- Drones leaving a zone release capacity for incoming drones in that same turn.
- Start and end may hold all drones. Delivered drones are no longer scheduled.
- Default zone capacity and connection capacity are one.
- Blocked zones may never be entered or traversed.
- The evaluator-facing CLI emits one line per turn and only movement tokens on stdout.
- Diagnostics, metrics, and visualization must not corrupt mandatory stdout.
- The visual representation is mandatory; the richer React UI is planned, but an evaluator-
  safe colored terminal visualization may protect early compliance.

Read `docs/project/03_DOMAIN_CONTRACT.md` for the detailed interpreted contract and mark any
remaining ambiguity in `docs/progress/OPEN_QUESTIONS.md`.

## Architectural boundaries

- `domain`: entities, value objects, invariants; imports no adapters or frameworks.
- `parsing`: text-to-domain conversion with line-aware errors.
- `pathfinding`: custom algorithms and candidate paths; no simulation I/O.
- `scheduling`: time/capacity reservations and route allocation.
- `simulation`: deterministic turn transition and event production.
- `application`: use cases and ports; coordinates the domain.
- `adapters/cli`: argument parsing and exact text output.
- `adapters/api`: FastAPI DTOs and transport concerns; introduced later.
- `events`: typed facts emitted by completed domain/application actions.
- `frontend`: TypeScript client and visualization; never computes authoritative routes.

Dependency direction always points inward. Keep framework types at boundaries. Pydantic DTOs
are not domain entities. React is a projection of backend state, not a second simulator.

## Evolution rule

Do not begin with distributed EDA. Evolve through explicit maturity levels:

1. Direct application calls and deterministic return values.
2. Typed immutable in-process events.
3. REST commands/queries plus SSE event streaming.
4. WebSocket only for demonstrated bidirectional live-control need.
5. External NATS/RabbitMQ worker only after measured need and mandatory completion.

No event sourcing, database, authentication, Docker Compose, broker, or microservice may be
added speculatively. Record an ADR before crossing an architecture maturity boundary.

## Development workflow

Use vertical slices, not layer-wide code generation:

1. Define one observable behavior and acceptance examples.
2. Write the smallest failing test.
3. Implement the minimum domain behavior.
4. Run the narrow test, then all existing gates.
5. Review the diff with Ponytail.
6. Explain the flow and key trade-off to the learner.
7. Update `docs/progress/CURRENT.md`, `SESSION_LOG.md`, and any affected decision/risk record.
8. Stop at the approved slice boundary.

Never generate an entire phase in one turn. Never claim completion without fresh command
output. Do not weaken or delete a test to make implementation pass unless the requirement was
proven wrong and the decision was documented.

## Ponytail supervision contract

Ponytail is always active during coding at `full` intensity. Before implementation, apply its
ladder: skip, reuse, stdlib, native feature, installed dependency, one line, then minimum code.

After every non-trivial slice:

1. Run `/ponytail-review` against the current diff.
2. Accept deletions/simplifications only if Fly-In invariants and acceptance tests remain true.
3. Record deliberately deferred scalability ceilings with a `ponytail:` comment and in the
   risk register if they could affect official benchmarks.
4. Run `/ponytail-audit` at milestone boundaries, not after every tiny edit.

Ponytail cannot simplify away parser validation, scheduling correctness, capacity safety,
restricted movement semantics, required OOP/type safety, evaluation behavior, or meaningful
tests. The shortest incorrect algorithm is not acceptable.

## Teaching contract

The project is also meant to teach a teammate. For each accepted slice, maintain a short
explanation containing:

- problem and observable behavior;
- request/data flow;
- involved classes and why each exists;
- relevant invariant;
- complexity where algorithmic;
- one example using an official or derived map;
- how the test proves the behavior.

During the API phase, explicitly teach HTTP resources, verbs, status codes, JSON, DTOs,
OpenAPI, validation, idempotency, synchronous versus asynchronous work, and SSE/WebSocket.
Do not introduce jargon without connecting it to the actual Fly-In flow.

## Tool use

- Search with `rg`/`rg --files` before creating or moving code.
- Prefer small patches and inspect their diff.
- Use the terminal for deterministic tests, linters, type checks, and benchmarks.
- Use web research only for unstable framework behavior and prefer official documentation.
- Use subagents only for independent, bounded analysis when parallelism has clear value; do
  not delegate core understanding or allow several agents to edit overlapping files.
- Never expose, commit, or print secrets.
- Never run destructive Git commands without explicit approval.

## Completion response

When handing back a slice, report:

1. Outcome.
2. Files changed.
3. Evidence from tests/type/lint/benchmark commands.
4. Requirement or rubric rows covered.
5. Ponytail findings applied or rejected with reason.
6. Remaining limitation or risk.
7. The next smallest sensible step, without starting it automatically.
