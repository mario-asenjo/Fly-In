# M8 native UI kickoff

Date: 2026-08-12
Active slice: #71 - native web shell and official-map selector
Follow-up: #72 - completed synchronous simulation playback

## Why the UI plan changed

The old roadmap assumed the browser would arrive after typed events and would use React + TypeScript.
The implemented architecture disproved the need for that ordering: M7 now exposes a synchronous map
catalog and completed solve response through a stable FastAPI boundary. The first browser consumer
can therefore teach the actual HTTP interaction directly with native `fetch()` and DOM updates.

ADR-0007 records the new decision and ADR-0002 is retained as superseded history rather than deleted.
Issue #59 remains open but deferred: events become relevant only if the real client later needs live
updates, replay, reconnection, or work that outlives one request.

## M8.1 implementation

```text
GET /
 |
 v
index.html + style.css + app.js
 |
 v
GET /api/v1/maps
 |
 v
MapCatalogResponse
 |
 v
<select>
```

FastAPI also serves `/img/*` from the same origin. This deliberately avoids a second development
server and CORS configuration.

The page provides:

- a responsive, Gestalt-oriented selector card with clear hierarchy and grouping;
- API status, loading, ready, empty and error states;
- selection summary;
- a **Simulate** action that intentionally logs intent only;
- consistent `[Fly-In UI]` console traces for bootstrap, catalog request/result, selection and
  simulation intent;
- low-opacity decorative drone SVGs that do not compete with the interaction surface;
- keyboard focus treatment, live-region status text and reduced-motion support.

## Assets

The user supplied PNG references plus hand-converted SVG equivalents. M8.1 versions the SVGs:

- `sad.svg`: eventual not-dispatched/start-state visual language;
- `normal.svg`: eventual active/in-progress state;
- `happy.svg`: eventual delivered state;
- `zone.svg`: candidate runtime zone template;
- `conn.svg`: candidate runtime connection template.

SVG was chosen over PNG because it scales cleanly, is easy to fade/decorate with CSS, and preserves
runtime text/template possibilities. This is not a commitment to use the zone/connection templates
for the actual graph. M8.2 must prefer readable coordinate/capacity visualization; native SVG
primitives are the fallback if template assets become awkward.

## Protected boundaries

M8.1 does not change:

- parser/domain/pathfinding/scheduler/validator logic;
- the CLI or evaluator stdout contract;
- the public catalog/simulation DTOs;
- simulation execution behavior;
- event/SSE/resource lifecycle behavior.

The browser does not parse `movement_lines`, infer capacities, or calculate routes.

## Non-goals intentionally rejected

- React, TypeScript, Vite, npm and Node.js;
- CORS middleware;
- UI/graph/state libraries;
- calling `POST /simulate` in this slice;
- graph rendering and playback;
- custom map upload/paste;
- events, SSE, WebSocket, persistence, cache or broker.

## Next proof

#72 should turn the logged **Simulate** intent into one synchronous POST, retain the completed
`SolveResponse`, render the map from structured DTOs and prove deterministic local stepping before
adding automatic playback.
