# Map provenance

`maps/{easy,medium,hard,challenger}/` contains the official Fly-In 1.5 map package, confirmed by the
project owner on 2026-07-17. The files were moved byte-for-byte from the former
`maps/maps-v1.5-added-before-m0/` wrapper on 2026-08-09 to keep evaluator paths short. Their exact
content hashes remain pinned in `docs/sources/MANIFEST.sha256`.

The duplicate historical v1.2 map package was removed from the evaluator-facing tree on 2026-08-09.
Historical comparison now uses `docs/sources/fly-in_1.2.pdf`, the delta document, Git history, and the
provenance comments on derived fixtures. It never overrides the 1.5 subject, rubric, or official maps.

Known historical differences:

- Simple Fork snapshot: 3 drones; official v1.5 map: 4.
- Priority Puzzle snapshot: 4 drones; official v1.5 map: 5.
- Snapshot README Challenger record: 41; official v1.5 map/rubric reference: 45.

`tests/fixtures/derived-v15/` contains local edge-case fixtures. Their leading comments identify
changes and assumptions; they are not official maps.
