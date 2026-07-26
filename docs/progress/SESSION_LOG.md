# Session log

## 2026-07-25 - M1.5-M1.6 structural integrity and inline comments

- Combined adjacent cross-line constraints: exactly one start/end, globally unique zone names,
  prior-defined connection endpoints, and exact/reversed undirected connection duplicates.
- Added `Connection.identity` as a canonical unordered name pair while retaining directed
  `left`/`right` references for future traversal/output.
- Replaced terminal assertions and endpoint `KeyError` leakage with physical-line `MapParseError`.
- Supported inline `#` comments through the existing significant-line normalization and resolved Q2
  following explicit user approval.
- TDD RED produced ten expected failures; GREEN has twelve tests, strict gates, and all ten official
  v1.5 maps parsing successfully.
- Independent Ponytail full review accepted the slice without blocking changes. It deferred the
  syntax-versus-duplicate terminal error precedence to M1.9 and accepted centralized name coverage
  through `_register_zone()` without testing every role permutation.
- Deliberately deferred self-loops, metadata semantics, zone/color interpretation, effective
  capacities, and stable complete error codes.

## 2026-07-25 - M1.3-M1.4 significant lines and raw metadata

- Combined two adjacent parser concerns into one coherent slice: blanks/full-line comments with
  physical line tracking, then valid raw metadata tokenization/default/canonical order.
- Added public `MapParseError.line_number`, immutable raw metadata tuples on zones/connections, and
  exact declaration classification; semantic zone/color/capacity interpretation stays deferred.
- Proved comments before `nb_drones`, blanks between declarations, metadata in different orders,
  empty metadata defaults, connection metadata, and physical line 5 for an unknown declaration.
- Verified four tests, all local gates, and direct parsing of official easy maps 01 and 02.
- Independent Ponytail full review accepted the slice without blocking changes; malformed empty
  keys/values, empty/multiple blocks, and the complete metadata error matrix remain deferred to
  M1.9 rather than receiving partial validation here.
- Next: approve M1.5 for terminal/name uniqueness and prior-defined connection endpoints.

## 2026-07-25 - M1.2 regular hubs and multiple connections

- Added one wider but coherent RED example with two regular hubs, three connections, four drones,
  and a negative coordinate; the M1.1 fixed four-line parser failed on the extra declarations.
- Extended `ParsedMap` with immutable regular hubs and changed `MapParser` to process valid
  declarations in source order, resolving connection names through one shared zone dictionary.
- Preserved M1.1 behavior and deliberately excluded comments, metadata, formal errors, duplicate
  rules, bidirectional identity, pathfinding, simulation, and CLI concerns.
- Independent Ponytail full review accepted the diff without blocking or requested changes.
- Verified both parser tests, context validation, `flake8`, and `mypy --strict`.
- Next: approve M1.3 for blanks/full-line comments plus physical source-line tracking.

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
