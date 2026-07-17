# Fly-In 1.2 to 1.5 delta

## Summary

Version 1.5 does not change the fundamental project. It clarifies terminal-zone capacity,
corrects ambiguous wording, updates performance targets substantially, and adds three map
figures. The implementation risk is concentrated in parsing terminal capacity and in the
more demanding benchmark targets.

## Functional and normative changes

| Area | Version 1.2 | Version 1.5 | Required response |
| --- | --- | --- | --- |
| Start/end `max_drones` | Terminal zones described as exceptions, metadata behavior ambiguous | Metadata is explicitly ignored and is not a validation error | Model terminal capacity as unlimited |
| Zone names | “any valid characters but dashes and spaces” | “any valid characters except dashes and spaces” | Reject names containing `-` or spaces |
| Input description | “network of drones” | “network of zones” | Editorial correction |
| Same-turn capacity | Grammatically broken wording | Confirms outgoing drones have freed space | Evaluate departures before incoming occupancy |
| Restricted transit wording | “connexion” | “connection” | Editorial correction; behavior unchanged |

## Benchmark changes

| Map | Version 1.2 | Version 1.5 | Consequence |
| --- | ---: | ---: | --- |
| Linear path | 2 drones, <= 6 | 2 drones, <= 6 | No change |
| Simple fork | 3 drones, <= 6 | 4 drones, <= 8 | Different workload |
| Basic capacity | 4 drones, <= 8 | 4 drones, <= 6 | Stricter |
| Dead end trap | 5 drones, <= 15 | 5 drones, <= 12 | Stricter |
| Circular loop | 6 drones, <= 20 | 6 drones, <= 15 | Stricter |
| Priority puzzle | 4 drones, <= 12 | 5 drones, <= 12 | More drones |
| Maze nightmare | 8 drones, <= 45 | 8 drones, <= 30 | Much stricter |
| Capacity hell | 12 drones, <= 60 | 12 drones, <= 35 | Much stricter |
| Ultimate challenge | 15 drones, <= 35 | 15 drones, <= 45 | More permissive |
| Impossible Dream | 25 drones, record 45 | 25 drones, record 45 | No subject change |

Category expectations in 1.5:

- Easy: fewer than 10 turns.
- Medium: 10-30 turns.
- Hard: fewer than 60 turns.
- Challenger: optional; aim to beat 45 turns.

The evaluation rubric reproduces the 1.5 per-map values and uses them for the exceptional
performance bonus.

## Documentary changes

- Three example figures were added: Easy map 2, Medium map 3, and Hard map 2.
- “Exceptional performances” became “Exceptional performance”.
- “Perfectly” is clarified as matching or beating each target.
- Grammar and formatting were corrected in several sections.

## Known supplied-map conflicts

The included maps are retained as a v1.2 snapshot, at the user's request:

| File | Snapshot value | Subject 1.5/evaluation value |
| --- | ---: | ---: |
| `easy_02_simple_fork.txt` | 3 drones | 4 drones |
| `medium_03_priority_puzzle.txt` | 4 drones | 5 drones |
| `README_maps.md` Challenger record | 41 turns | 45 turns |

Do not edit either snapshot. `maps/maps-v1.5-added-before-m0/` is the confirmed official 1.5
package; retain the v1.2 copy only for historical provenance. Derived v1.5 fixtures may change
only `nb_drones` and must say so in their comments.

## Compatibility policy

- Target Fly-In 1.5 behavior.
- Keep tests demonstrating terminal `max_drones` is accepted and ignored.
- Treat the first significant line after blank/comment lines as `nb_drones`, because supplied
  maps place comments first even though the subject says “first line”. Record this as an
  interpretation and preserve physical line numbers in errors.
- Never lower a 1.5 benchmark expectation because an old map file contains fewer drones.
