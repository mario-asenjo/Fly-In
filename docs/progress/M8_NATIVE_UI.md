# M8 native UI progress

Date: 2026-08-13
Completed foundation: #71 / PR #73
Active slice: #72 - completed synchronous simulation playback

## Runtime architecture

PR #73 established a native frontend served independently on port 8080 and a pure FastAPI JSON/OpenAPI adapter on port 8000 with narrow CORS. ADR-0007 supersedes the earlier React-first decision.

The frontend is intentionally dependency-free: HTML, CSS, native JavaScript and the supplied SVG artwork. Events/SSE remain deferred because the backend already returns a complete synchronous simulation.

## #72 implementation

The selector now drives the real endpoint:

```text
GET /api/v1/maps
        |
        v
select official map
        |
        v
POST /api/v1/maps/{index}/simulate
        |
        v
completed SolveResponse
        |
        +--> SVG-first map
        +--> local turn projection
        +--> playback
        +--> metrics / warnings / evaluator output
```

The browser never computes paths or reparses evaluator stdout. `turns[].movements` is the state source; `movement_lines` is shown only as evaluator-facing output.

## SVG-first visual implementation

The user-supplied SVGs are used before considering native graph primitives:

- `zone.svg` is the shell for every runtime zone;
- `conn.svg` is stretched/rotated between map coordinates for physical links;
- `sad.svg` represents drones still waiting at start;
- `normal.svg` represents active/transit drones;
- `happy.svg` represents delivered drones and is also the favicon.

Runtime zone/connection labels were removed from the templates so JavaScript can overlay real names, capacities and occupancy. Zone metadata colors appear as a visual halo while the explicit zone-type badge preserves meaning without color alone.

No fallback to primitive-only rendering is chosen yet. The acceptance criterion is to inspect actual easy/medium/hard/challenger maps and change only if the supplied templates demonstrably hurt readability, overlap or scaling.

## Playback and inspection

The completed response is stored in memory and replayed locally with reset, previous, next, play/pause, timeline seek and speed controls. The workspace also exposes:

- turn number and evaluator line;
- waiting/active/delivered fleet counts;
- turn count, drone count, total path cost and average delivery turn;
- solver warnings;
- highlighted evaluator movement lines;
- clickable/keyboard-focusable zone and connection inspection.

Restricted-entry transit is projected from structured movement data: `path_cost == 2` places the drone on the connection for that completed turn. The following structured movement places it at the destination. No token parsing is used.

## Visual polish

The page now uses `happy.svg` as favicon and includes additional low-opacity drones, zones and connections in the background. The decoration remains non-interactive and reduced-motion preferences are respected.

## Code shape

Frontend scripts remain directly in `frontend/` and are split only by real responsibility after the UI outgrew one teaching script:

- `app.js`: catalog/API transport and simulation submission;
- `graph.js`: SVG-first graph/inspector;
- `project-turn.js`: deterministic turn projection;
- `render-simulation.js`: metrics/output/current-turn rendering;
- `playback.js`: local playback controller.

No bundler, module loader, framework, graph package or state library was introduced.

## Validation added

`tests/test_native_frontend_contract.py` locks the favicon/script pipeline, real catalog/simulate endpoints, supplied SVG renderer usage and removal of placeholder asset text. Existing API bootstrap tests continue to protect API-only hosting and narrow CORS.

## Still to verify visually

Human browser review on the densest official maps is required before declaring the supplied `zone.svg` / `conn.svg` layout universally readable. That review determines whether a later native-primitive fallback is necessary; it must not be assumed in advance.
