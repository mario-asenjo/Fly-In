# Current project state

- Last updated: 2026-07-25
- Current milestone: M1 - Parser vertical slices
- Production implementation: M1.6 validates structural identity and undirected connection uniqueness
- Mandatory completion: M0 plus parser slices M1.1-M1.6 are complete
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
- M1.2 supports any number of regular hubs and valid prior-defined connections while preserving
  source order, coordinates, and shared `Zone` object identity across the parsed map.
- M1.3 ignores blanks/full-line comments and preserves physical source lines in `MapParseError`.
- M1.4 stores immutable canonical `key=value` metadata on zones/connections, with empty metadata as
  the default and tag order proven irrelevant; metadata semantics remain deliberately deferred.
- M1.5 requires unique terminals/names and prior-defined connection endpoints with physical-line
  `MapParseError` diagnostics.
- M1.6 rejects exact and reversed duplicate connections through canonical unordered identity while
  preserving directed `left`/`right` endpoints.
- Inline `#` comments are supported by the same physical-line normalization used for full comments.
- All ten official v1.5 maps parse through this boundary in direct local verification.
- The focused test, full pytest suite, `flake8`, and `mypy --strict` pass.

## Next smallest slice

Define and approve M1.7-M1.8 as one coherent metadata-semantics slice:

- interpret `zone` into an explicit normal/blocked/restricted/priority type;
- expose optional color without using it for authoritative routing;
- interpret default/explicit regular-zone and connection capacities;
- represent terminal effective capacity as unlimited while retaining ignored declared metadata;
- validate the supported metadata values with physical-line errors.

Keep pathfinding, adjacency filtering, movement cost, simulation, scheduling, and CLI out of this
parser/domain slice. Decide the self-loop policy before parser lock.
Replace the temporary `python -m flyin` message only when a real CLI adapter exists.

## Active blockers

None. The parser milestone remains intentionally incomplete beyond the proven M1.6 grammar.

## Required context for next session

- `AGENTS.md`
- `docs/project/02_SOURCE_OF_TRUTH.md`
- Parser parts of `docs/project/03_DOMAIN_CONTRACT.md`
- `docs/project/05_ROADMAP.md` M0/M1
- `docs/progress/OPEN_QUESTIONS.md`
