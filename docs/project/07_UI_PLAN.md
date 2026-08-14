# Native web UI plan

Status: synchronous native UI implemented; current refinement prioritizes a readable simulation canvas for dense maps.

## Purpose

Visualize Fly-In while keeping the browser as a projection client. Python remains authoritative for parsing, pathfinding, scheduling, capacities, restricted transit and validation.

## Technology and runtime

ADR-0007 supersedes the React-first plan. Use semantic HTML, CSS and native JavaScript. Serve the frontend independently on port 8080 and call the FastAPI JSON/OpenAPI API on port 8000 through narrow CORS.

No React, Vite, TypeScript, Node, UI kit, graph library, state library, reverse proxy or event transport is required.

## Synchronous flow

```text
GET /api/v1/maps
        |
        v
map selector
        |
        v
POST /api/v1/maps/{index}/simulate
        |
        v
completed SolveResponse
        |
        +--> native SVG graph projection
        +--> local turn projection
        +--> playback controls
        +--> optional warning presentation
```

The browser stores the completed response and changes only its local playback cursor. It never asks the backend to recompute a turn during playback.

## Canvas-first presentation

The simulation is the primary visual artifact, not a dashboard.

- the workspace may use roughly 90-96% of the viewport width;
- the airspace consumes most of the visible height;
- dense maps grow a virtual graph surface larger than the viewport;
- the user can scroll or drag to pan;
- `-`, `Fit`, and `+` control canvas scale;
- playback stays directly below the graph;
- zone/connection inspection appears as a lightweight overlay;
- metrics, fleet summary cards and evaluator `movement_lines` are not painted;
- warnings appear only when the backend returns them.

## Runtime graph renderer

The supplied `zone.svg` and `conn.svg` were implemented first and reviewed on the Challenger map. The result proved that those card-shaped assets are too large to repeat at dense coordinate spacing: making the viewport larger did not remove node overlap.

The runtime graph therefore uses compact native SVG primitives:

- physical connections: `<line>` plus a small capacity/transit badge only when useful;
- zones: compact `<g>` groups built from `<rect>`, `<circle>` and `<text>`;
- zone metadata color: outer accent;
- zone semantic type: independent marker color so meaning does not depend on metadata color;
- full zone/connection detail: inspector overlay instead of permanent text inside every node.

Coordinate meaning is preserved, but each coordinate unit receives a minimum visual spacing. The surface grows from the map coordinate bounds instead of scaling all nodes into a fixed 1200x700 box. For Challenger (`x=0..21`), this intentionally produces a virtual width of roughly 3.3k px before user zoom.

The supplied drone artwork remains part of the graph:

- `sad.svg`: waiting at start;
- `normal.svg`: active or restricted transit;
- `happy.svg`: delivered and favicon.

Large groups at one location are aggregated into one drone icon plus a count badge instead of drawing dozens of overlapping icons. `zone.svg` and `conn.svg` remain available as visual/decorative assets but are no longer runtime graph primitives.

## Projection rules

Use structured `turns[].movements`; never parse `movement_lines` to reconstruct state.

- Initial state: all drones at `map.start`.
- `path_cost == 2`: drone is visually in transit on `origin <-> destination` for the restricted-entry turn.
- Other movement: drone is at `destination` after that turn.
- Destination equal to `map.end`: drone is delivered.

## Interaction

The workspace includes reset, previous, next, play/pause, timeline seek and playback speed. Zones and connections are inspectable. The canvas adds pan, scroll, fit and zoom. Console traces use `[Fly-In UI]` for transport, selection, simulation, playback, inspection, layout and canvas actions.

## CORS

Keep the API policy deliberately narrow: only the documented local frontend origins on port 8080, methods `GET`/`POST`, headers `Accept`/`Content-Type`, no wildcard origin and no credentials.

## Accessibility and motion

Use native controls, visible focus, keyboard graph inspection, semantic type cues in addition to metadata colors, textual inspector information and `prefers-reduced-motion`.

## Validation

Static frontend-contract tests lock the real catalog/simulate calls, native zone/connection primitives, retained drone SVG assets, dynamic graph dimensions, pan/zoom/fit controls, and the absence of metrics/fleet/movement-line dashboard elements. Challenger is the key dense-map visual regression case.

## Deferred work

Events, SSE, WebSocket, async simulation resources, custom map upload/paste and any frontend framework remain deferred until a concrete requirement appears.
