Fly-In project: use repository AGENTS.md as the always-on contract and docs/progress/CURRENT.md as
the current-state pointer. Target subject is Fly-In 1.5 plus the Intra evaluation rubric; bundled
maps are a known stale 1.2 snapshot until Mario replaces them.
§
Fly-In architecture evolves mandatory typed Python CLI -> in-process events -> FastAPI -> React ->
SSE -> optional broker only after measured need. Keep the pure domain independent of adapters.
§
For Fly-In coding keep official Ponytail plugin in full mode; run ponytail-review after non-trivial
slices and ponytail-audit at milestones. Spec, correctness, validation, tests and accessibility
outrank minimalism.
§
Persist detailed project state, decisions, risks and benchmarks in repository docs, not global
Hermes memory.
