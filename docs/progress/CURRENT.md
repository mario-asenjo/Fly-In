# Current project state

- Last updated: 2026-07-17
- Current milestone: M0 - Repository and executable contract
- Production implementation: not started by design
- Mandatory completion: 0%
- API/UI/EDA implementation: intentionally not started

## Verified completed

- Fly-In 1.2 and 1.5 subjects compared.
- Evaluation rubric inspected and mapped.
- Current architecture/roadmap/source hierarchy documented.
- Hermes context, skills, bundles, templates, and Ponytail integration prepared.
- Supplied v1.2 map snapshot retained unchanged.
- Python 3.13.14, `uv` 0.11.19, GNU Make 4.4.1, and GitHub CLI authentication verified locally.
- First comment-free minimal-map acceptance test added as the intentional M0 red test.
- A repository PR template now requires scope, invariant, quality-gate, risk, teaching, and Ponytail evidence.

## Next smallest slice

Implement only the production types and parser necessary to make
`tests/test_minimal_map_parsing.py` pass:

- one typed parsed-map representation;
- `MapParser.parse()` for drone count, start, end, and one connection;
- no comments, metadata, regular hubs, malformed-input handling, pathfinding, simulation, or CLI.

Then run the focused test and all mandatory M0 quality gates before opening the implementation
iteration PR.

## Active blockers

- README team login placeholders are still unknown (Q12); do not invent them.
- Supplied maps are a tracked v1.2 snapshot risk, not a blocker for the minimal parser contract.

## Required context for next session

- `AGENTS.md`
- `docs/project/02_SOURCE_OF_TRUTH.md`
- Parser parts of `docs/project/03_DOMAIN_CONTRACT.md`
- `docs/project/05_ROADMAP.md` M0/M1
- `docs/progress/OPEN_QUESTIONS.md`
