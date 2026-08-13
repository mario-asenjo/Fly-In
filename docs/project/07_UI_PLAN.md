# Native web UI plan

Status: synchronous native UI implemented; current refinement prioritizes the simulation canvas for dense maps.

## Purpose

Visualize Fly-In while keeping the browser as a projection client. Python remains authoritative for parsing, pathfinding, scheduling, capacities, restricted transit and validation.

## Technology and runtime

ADR-0007 supersedes the React-first plan. Use semantic HTML, CSS and native JavaScript. The frontend is served independently on port 8080 with Python's standard static server and calls the FastAPI JSON/OpenAPI API on port 8000 through narrow CORS.

No React, Vite, TypeScript, Node, UI kit, graph library, state library, animation framework, reverse proxy or event transport is required.

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
        +--> SVG-first map projection
        +--> local turn projection
        +--> playback controls
        +--> optional warning presentation
```

The browser stores the completed response and changes only its local playback cursor. It never asks the backend to recompute a turn during playback.

## Canvas-first presentation

The simulation is the primary visual artifact, not a dashboard. After a simulation loads:

- the workspace may use roughly 90-96% of the viewport width;
- the airspace consumes most of the visible height;
- dense maps use a virtual graph surface larger than the viewport rather than compressing every label and SVG template;
- the user can scroll or drag to pan around the airspace;
- simple `-`, `Fit`, and `+` controls change the virtual canvas scale;
- playback controls stay directly below the graph;
- zone/connection inspection appears as a lightweight overlay instead of a permanent sidebar.

Do not render redundant metrics, fleet summary cards or evaluator `movement_lines` in the page. Those values may remain in `SolveResponse` for API/debug/other consumers, but the visualizer should communicate drone state directly through the graph. Warnings are shown only when the backend actually returns them.

## SVG-first decision

Use the supplied artwork first:

- `sad.svg`: waiting at start;
- `normal.svg`: active or restricted transit;
- `happy.svg`: delivered and favicon;
- `zone.svg`: runtime zone shell;
- `conn.svg`: runtime physical-connection shell.

Runtime labels and counts are overlaid by JavaScript. Zone metadata colors are shown as a halo while a separate kind badge preserves semantic meaning without relying on color alone.

Do **not** replace zone/connection templates with native SVG primitives pre-emptively. First inspect real easy, medium, hard and challenger maps. Switch only if actual rendering demonstrates unacceptable overlap, scaling or label readability after the larger pannable canvas is available.

## Projection rules

Use structured `turns[].movements`; never parse `movement_lines` to reconstruct state.

- Initial state: all drones at `map.start`.
- `path_cost == 2`: drone is visually in transit on `origin <-> destination` for the restricted-entry turn.
- Other movement: drone is at `destination` after that turn.
- Destination equal to `map.end`: drone is delivered and uses the happy visual state.

## Interaction

The workspace includes reset, previous, next, play/pause, timeline seek and playback speed. Zones and connections are inspectable. The canvas adds pan, scroll, fit and zoom. Console traces use `[Fly-In UI]` for transport, selection, simulation, playback, inspection and canvas actions.

## CORS

Keep the API policy deliberately narrow: only the documented local frontend origins on port 8080, methods `GET`/`POST`, headers `Accept`/`Content-Type`, no wildcard origin and no credentials.

## Accessibility and motion

Use native controls, visible focus, keyboard graph inspection, semantic type labels in addition to colors, textual inspector information and `prefers-reduced-motion`.

## Validation

Static frontend-contract tests lock the real catalog/simulate calls, supplied SVG usage, large scrollable canvas controls, and the absence of metrics/fleet/movement-line dashboard elements. Human review of hard and challenger maps remains the visual acceptance gate for the SVG templates.

## Deferred work

Events, SSE, WebSocket, async simulation resources, custom map upload/paste and any frontend framework remain deferred until a concrete requirement appears.
