# Map provenance

`maps/maps-v1.5-added-before-m0/` contains the official Fly-In 1.5 map package, confirmed by the
project owner on 2026-07-17. Its files are immutable benchmark/topology inputs; their hashes are
recorded in `docs/sources/MANIFEST.sha256`.

`provided-v12-snapshot/` contains the historical v1.2 package. It remains unchanged for comparison
only and must not override the current subject, rubric, or official v1.5 maps.

Known historical differences:

- Simple Fork snapshot: 3 drones; official v1.5 map: 4.
- Priority Puzzle snapshot: 4 drones; official v1.5 map: 5.
- Snapshot README Challenger record: 41; official v1.5 map/rubric reference: 45.

`tests/fixtures/derived-v15/` contains local edge-case fixtures. Their leading comments identify
changes and assumptions; they are not official maps.
