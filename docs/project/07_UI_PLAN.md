# Native web UI plan

Status: synchronous native UI implemented in draft PR #73.

## Purpose

Visualize Fly-In while keeping the browser as a projection client. Python remains authoritative for parsing, pathfinding, scheduling, capacities, restricted transit and validation.

## Technology and runtime

ADR-0007 supersedes the React-first plan. Use semantic HTML, CSS and native JavaScript. The frontend is served independently on port 8080 with Python's standard static server and calls the FastAPI JSON/OpenAPI API on port 8000 through narrow CORS.

No React, Vite, TypeScript, Node, UI kit, graph library, state library, animation framework, reverse proxy or event transport is required.

All frontend source files stay directly under `frontend/`; `frontend/img/` is the only nested asset directory. Scripts are separated only where the implemented UI now has distinct responsibilities: API/bootstrap, graph rendering, turn projection, result rendering and playback.

## Implemented synchronous flow (#71 + #72)

```text
GET /api/v1/maps
        |
        v
official map selector
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
        +--> metrics / warnings / evaluator output
        +--> zone and connection inspector
```

The browser stores the completed response and changes only its local playback cursor. It never asks the backend to recompute a turn during playback.

## SVG-first decision

Use the supplied artwork first:

- `sad.svg`: waiting at start;
- `normal.svg`: active or restricted transit;
- `happy.svg`: delivered and favicon;
- `zone.svg`: runtime zone shell;
- `conn.svg`: runtime physical-connection shell.

Runtime labels and counts are overlaid by JavaScript. Zone metadata colors are shown as a halo while a separate kind badge preserves semantic meaning without relying on color alone.

Do **not** replace zone/connection templates with native SVG primitives pre-emptively. First inspect real easy, medium, hard and challenger maps. Switch only if actual rendering demonstrates unacceptable overlap, scaling or label readability.

## Projection rules

Use structured `turns[].movements`; never parse `movement_lines` to reconstruct state.

- Initial state: all drones at `map.start`.
- `path_cost == 2`: drone is visually in transit on `origin <-> destination` for the restricted-entry turn.
- Other movement: drone is at `destination` after that turn.
- Destination equal to `map.end`: drone is delivered and uses the happy visual state.

Evaluator movement lines remain presentation-only and are highlighted alongside the current visual turn.

## Interaction

The implemented workspace includes reset, previous, next, play/pause, timeline seek and playback speed. Zones and connections are mouse/keyboard inspectable. Console traces use the `[Fly-In UI]` prefix for transport, selection, simulation, playback and inspection actions.

## CORS

Keep the API policy deliberately narrow: only the documented local frontend origins on port 8080, methods `GET`/`POST`, headers `Accept`/`Content-Type`, no wildcard origin and no credentials.

## Accessibility and motion

Use native controls, visible focus, keyboard graph inspection, text metrics/output in addition to graphics, semantic type labels in addition to colors, and `prefers-reduced-motion`.

## Validation

The PR contains API/CORS bootstrap coverage plus a static native-frontend contract covering favicon, script pipeline, real catalog/simulate endpoints and supplied SVG usage. Human visual review of dense official maps remains the acceptance gate before deciding whether the SVG templates need a native-primitive fallback.

## Deferred work

Events, SSE, WebSocket, async simulation resources, custom map upload/paste and any frontend framework remain deferred until a concrete requirement appears.
