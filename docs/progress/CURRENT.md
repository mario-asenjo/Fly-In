# Current project state

- Last updated: 2026-07-25
- Current milestone: M1 - Parser vertical slices
- Production implementation: M1.1 parses and represents the smallest comment-free linear map
- Mandatory completion: M0 and parser slice M1.1 are complete; later parser behavior is not started
- API/UI/EDA implementation: intentionally not started

## Verified completed

- Fly-In 1.2 and 1.5 subjects compared; the Fly-In 1.5 Makefile rules were rechecked directly.
- `maps/maps-v1.5-added-before-m0/` is confirmed as the official 1.5 map package and hash-pinned.
- The historical v1.2 snapshot remains immutable comparison evidence only.
- `masenjo` is the confirmed README 42 login.
- Python 3.13.14, `uv` 0.11.19, GNU Make 4.4.1, and GitHub CLI authentication are verified locally.
- The Makefile provides the subject-required `install`, `run`, `debug`, `clean`, `lint`, and optional
  `lint-strict` targets; `run` executes the temporary M0 module entry point.
- The first comment-free minimal-map acceptance test originated as the intentional M0 red contract.
- M1.1 turns that contract green with immutable typed `Zone`, `Connection`, and `ParsedMap`
  objects plus `MapParser.parse()` for one drone count, start, end, and connection.
- The focused test, full pytest suite, `flake8`, and `mypy --strict` pass.

## Next smallest slice

Define and approve M1.2 with one failing acceptance example for a regular hub and connections
that reference it, then implement only:

- regular `hub:` parsing;
- multiple zones and connections;
- explicit coordinate assertions for all parsed zone roles.

Keep comments, metadata, malformed-input handling, pathfinding, simulation, and CLI out of M1.2.
Replace the temporary `python -m flyin` message only when a real CLI adapter exists.

## Active blockers

None. The parser milestone remains intentionally incomplete beyond the proven M1.1 grammar.

## Required context for next session

- `AGENTS.md`
- `docs/project/02_SOURCE_OF_TRUTH.md`
- Parser parts of `docs/project/03_DOMAIN_CONTRACT.md`
- `docs/project/05_ROADMAP.md` M0/M1
- `docs/progress/OPEN_QUESTIONS.md`
