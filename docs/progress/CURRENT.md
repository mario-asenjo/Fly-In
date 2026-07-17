# Current project state

- Last updated: 2026-07-17
- Current milestone: M0 - Repository and executable contract
- Production implementation: only the mandatory temporary `python -m flyin` entry point exists
- Mandatory completion: 0%
- API/UI/EDA implementation: intentionally not started

## Verified completed

- Fly-In 1.2 and 1.5 subjects compared; the Fly-In 1.5 Makefile rules were rechecked directly.
- `maps/maps-v1.5-added-before-m0/` is confirmed as the official 1.5 map package and hash-pinned.
- The historical v1.2 snapshot remains immutable comparison evidence only.
- `masenjo` is the confirmed README 42 login.
- Python 3.13.14, `uv` 0.11.19, GNU Make 4.4.1, and GitHub CLI authentication are verified locally.
- The Makefile provides the subject-required `install`, `run`, `debug`, `clean`, `lint`, and optional
  `lint-strict` targets; `run` executes the temporary M0 module entry point.
- First comment-free minimal-map acceptance test remains the intentional M0 red test.

## Next smallest slice

Implement only the production types and parser necessary to make
`tests/test_minimal_map_parsing.py` pass:

- one typed parsed-map representation;
- `MapParser.parse()` for drone count, start, end, and one connection;
- no comments, metadata, regular hubs, malformed-input handling, pathfinding, simulation, or CLI.

Then replace the temporary `python -m flyin` message only when a real CLI adapter exists, and run
all Makefile quality gates before opening the parser PR.

## Active blockers

None. The M0 acceptance test is intentionally red until the next parser slice.

## Required context for next session

- `AGENTS.md`
- `docs/project/02_SOURCE_OF_TRUTH.md`
- Parser parts of `docs/project/03_DOMAIN_CONTRACT.md`
- `docs/project/05_ROADMAP.md` M0/M1
- `docs/progress/OPEN_QUESTIONS.md`
