# Session log

## 2026-07-25 - M1.1 smallest linear-map parser

- Started from updated `main` and preserved the existing acceptance test as the TDD red contract:
  collection failed because `flyin.parsing` did not exist.
- Added immutable typed domain objects and the smallest `MapParser.parse()` implementation for one
  drone count, start, end, and connection; no parser error model or later grammar was introduced.
- Ponytail review strengthened the same acceptance test to prove coordinates, endpoint object
  references, the one-connection tuple, and immutable parsed state without expanding grammar scope.
- Ponytail also confirmed two deliberate deferrals already placed by the roadmap: strict prefix
  errors in M1.9 and canonical undirected connection identity in M1.6.
- Verified the focused test, full pytest suite, context validation, `flake8`, and `mypy --strict`.
- Next: approve one M1.2 red example for a regular hub, multiple connections, and coordinates.

## 2026-07-17 - Subject Makefile compliance and official-map confirmation

- Re-read Fly-In 1.5 §III.2 directly: `install`, `run`, `debug`, `clean`, `lint`, and optional
  `lint-strict` are mandatory Makefile behavior; `lint` carries the subject's explicit mypy flags.
- Implemented those targets with the existing `uv` workflow and verified `run` against the M0
  temporary module entry point.
- Confirmed `maps/maps-v1.5-added-before-m0/` as the official 1.5 package, added its hashes to
  the immutable manifest, and updated source hierarchy, provenance, benchmark path, risks, and Q10.
- Recorded the confirmed README login `masenjo` and resolved Q12.
- Next: the smallest parser slice that turns `tests/test_minimal_map_parsing.py` green.

## 2026-07-17 - M0 executable contract / repository publishing

- Verified local Python 3.13.14, `uv` 0.11.19, GNU Make 4.4.1, GitHub authentication, repository administration, and `main` as the default branch.
- Added the first intentionally failing, inline comment-free acceptance test for the smallest map: one drone, start, end, and one connection.
- Added a repository-wide pull-request template requiring real commands, scope, Fly-In invariants, documentation, risk, teaching, and Ponytail evidence.
- No production parser was added: M0 deliberately ends with the red executable contract.
- Next: implement only the types and parser behavior required to make `tests/test_minimal_map_parsing.py` pass.

## 2026-07-10 - Initial context package

- Compared subjects 1.2 and 1.5 and aligned the evaluation rubric.
- Recorded benchmark changes and stale-map conflicts.
- Chose evolutionary modular-monolith architecture.
- Planned mandatory CLI -> in-process events -> FastAPI -> React -> SSE -> optional broker.
- Integrated official Ponytail Hermes plugin as minimalism supervisor.
- Created project/Hermes context package; no production solution generated.
- Forward-tested the start/spec-guardian workflows from clean agent contexts.
- Tightened M0 to one inline comment-free failing test and removed a premature broken CLI entry.
- Added the terminal invalid-capacity ambiguity as Q13.
- Next: agree on M0 and first parser vertical slice.

Future entries should be short, evidence-based, and link decisions/tests rather than duplicate them.
