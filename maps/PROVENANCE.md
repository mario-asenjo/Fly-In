# Map provenance

`provided-v12-snapshot/` contains the exact map files supplied with the older project package in
this ChatGPT project. They are intentionally unchanged even where Fly-In 1.5 and the current
evaluation sheet specify different drone counts or Challenger records.

Known differences:

- Simple Fork snapshot: 3 drones; v1.5 target: 4.
- Priority Puzzle snapshot: 4 drones; v1.5 target: 5.
- Snapshot README Challenger record: 41; v1.5/rubric reference: 45.

Replace/add the fresh official v1.5 map package before final benchmarking. Do not claim that the
derived fixtures are official.

`tests/fixtures/derived-v15/` contains minimal local adaptations and edge-case fixtures. Their
leading comments identify changes and assumptions.

`maps-v1.5-added-before-m0/` was present locally before M0 but has no independently verified
package provenance. Treat it as a provisional, non-official topology/benchmark candidate until
its original source is confirmed; it must not override the subject or rubric.
