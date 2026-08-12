# Native web UI plan

Status: active target design from M8.1 onward.

## Purpose

Visualize Fly-In so topology, occupancy, restricted transit, bottlenecks and parallel movement are
easier to understand while keeping the client/server boundary transparent for learning.

The browser is a projection adapter. Python remains authoritative for parsing, pathfinding,
scheduling, capacity semantics, restricted transit and validation.

## Technology decision

ADR-0007 supersedes the React-first plan for the current architecture.

Use first:

- semantic HTML;
- plain CSS;
- native JavaScript and `fetch()`;
- browser-native SVG for graph work;
- FastAPI same-origin static serving.

Do not add React, Vite, TypeScript, a UI kit, graph library, animation framework, client state library,
CORS middleware or Node tooling until a measured problem justifies it.

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

CSS and JavaScript stay at the frontend root by design. Assets are the only nested UI files.

## M8.1 - catalog selector (#71)

The first slice proves the simplest real HTTP consumer:

```text
browser load
    |
    v
GET /api/v1/maps
    |
    v
JSON catalog
    |
    v
<select>
```

Required behavior:

- FastAPI serves `/`, `/style.css`, `/app.js` and `/img/*` from the same origin as `/api/v1`;
- the selector populates from the real official-map catalog;
- loading, ready, empty and failure states are explicit;
- selection changes update a visible summary;
- **Simulate** logs intent only and does not call the solve endpoint yet;
- meaningful browser actions use the `[Fly-In UI]` console prefix;
- the layout uses clear grouping, hierarchy, proximity, figure/ground separation and responsive
  spacing rather than a framework-generated default appearance.

The drone SVGs can be decorative at low opacity. `zone.svg` and `conn.svg` are included as future
runtime-visualization candidates, not as a commitment to template-based graph rendering.

## M8.2 - completed synchronous simulation (#72)

After the selector is proven:

1. `POST /api/v1/maps/{map_index}/simulate`.
2. Store the complete structured `SolveResponse` in browser memory.
3. Render the static map from `map.zones` and `map.connections`.
4. Project turn state from `turns[].movements` rather than parsing `movement_lines`.
5. Add step/reset before automatic playback.
6. Add play/pause/speed after deterministic stepping works.
7. Add metrics, capacities and selected-zone/link inspection.

If `zone.svg` or `conn.svg` makes coordinate placement, scaling or runtime labels awkward, use native
SVG primitives for the graph. The supplied assets remain useful decorative/reference material; data
readability wins over asset reuse.

## Drone visual states

The supplied visual language maps naturally to eventual playback:

- `sad.svg`: drone still at the starting area / not yet dispatched;
- `normal.svg`: active or in-progress drone;
- `happy.svg`: delivered drone.

The exact runtime representation must follow backend state, not client inference.

## State model

For the synchronous UI, keep only the state that exists:

1. official-map catalog;
2. selected map index;
3. completed solve response, once M8.2 starts;
4. local playback cursor/speed/selection;
5. transient loading/error state.

Do not invent simulation IDs, lifecycle states or an event log before the backend produces them.

## Events and streaming

Typed events and SSE are no longer prerequisites for completed playback. Revisit them only when a
real requirement needs live ordered updates, reconnection, replay or work that outlives the HTTP
request. ADR-0006 still requires typed immutable events before any SSE/asynchronous resource is
introduced.

## Accessibility

- Native controls must remain keyboard accessible with visible focus.
- Buttons use explicit labels and status changes use restrained live regions.
- Do not rely on map metadata color alone to express zone meaning.
- Zone/link information should eventually have a textual alternative to the graph.
- Respect `prefers-reduced-motion` for visual transitions/animation.
- Decorative artwork uses empty alternative text and does not enter the accessibility tree.

## Tests

M8.1:

- same-origin index/CSS/JS/SVG delivery;
- API/OpenAPI regressions remain green.

M8.2 and later:

- coordinate-to-viewport transform;
- completed-turn state projection;
- playback cursor behavior;
- API error rendering;
- critical keyboard controls.

Avoid broad snapshots that fail on harmless SVG or CSS changes.
