# Native web UI plan

Status: active target design from M8.1 onward.

## Purpose

Visualize Fly-In while keeping the browser as a thin projection adapter. Python remains authoritative
for parsing, pathfinding, scheduling, capacities, restricted transit and validation.

## Technology decision

ADR-0007 supersedes the React-first plan for the current architecture.

Use semantic HTML, plain CSS, native JavaScript with `fetch()`, browser-native SVG, and Python's
standard-library static HTTP server for the frontend. Keep FastAPI focused on the JSON/OpenAPI API.

The local browser UI runs on port 8080 and calls the API on port 8000. FastAPI enables narrow CORS
only for `http://127.0.0.1:8080` and `http://localhost:8080`.

Do not add React, Vite, TypeScript, a UI kit, graph library, animation framework, state library or
reverse proxy until a measured problem justifies it.

## Repository shape

```text
frontend/
├── index.html
├── style.css
├── app.js
└── img/
    ├── sad.svg
    ├── normal.svg
    ├── happy.svg
    ├── zone.svg
    └── conn.svg
```

## Runtime boundary

The frontend and API are separate processes. `flyin.adapters.api` must not serve HTML, CSS,
JavaScript or image assets. The browser calls `http://127.0.0.1:8000/api/v1/...` from the frontend
origin on port 8080.

## M8.1 - catalog selector (#71)

Required behavior:

- the API remains API-only and returns 404 for frontend paths;
- the documented frontend origin is allowed by CORS;
- `GET /api/v1/maps` populates an accessible selector;
- loading, ready, empty and failure states are explicit;
- selection changes update a visible summary;
- **Simulate** logs intent only and does not call the solve endpoint yet;
- meaningful browser actions use the `[Fly-In UI]` console prefix;
- the page uses clear grouping, hierarchy, proximity, figure/ground separation and responsive spacing.

The drone SVGs can be decorative at low opacity. `zone.svg` and `conn.svg` remain candidates for
future runtime visualization, not a commitment.

## M8.2 - completed synchronous simulation (#72)

1. Call `POST /api/v1/maps/{map_index}/simulate` on the API origin.
2. Store the complete structured `SolveResponse` in browser memory.
3. Render the map from `map.zones` and `map.connections`.
4. Project turn state from `turns[].movements`, never from reparsed evaluator stdout.
5. Add step/reset before play/pause/speed.
6. Add metrics, capacities and inspection after projection correctness.

If `zone.svg` or `conn.svg` hurts runtime readability, use native SVG primitives.

## CORS policy

Keep it deliberately narrow:

- origins: local frontend on port 8080 only;
- methods: `GET` and `POST`;
- headers: `Accept` and `Content-Type`;
- no wildcard origin;
- no credentials until a real requirement exists.

## Events and streaming

Typed events and SSE are not prerequisites for completed playback. Revisit them only when the real
client needs live ordered updates, replay, reconnection or work that outlives the HTTP request.

## Accessibility

Keep native controls keyboard accessible, show visible focus, do not rely on color alone, provide
textual alternatives to graph information, and respect `prefers-reduced-motion`.

## Tests

M8.1 tests should prove the API stays API-only, the documented frontend origin receives the CORS
allow-origin header, unknown origins do not, and existing API/OpenAPI behavior remains green.

Later tests cover coordinate transforms, completed-turn projection, playback cursor behavior, API
errors and critical keyboard controls.
