# ADR-0007: Prefer native web technologies before React

- Status: Accepted
- Date: 2026-08-12
- Supersedes: ADR-0002 for the current UI milestone

## Context

Fly-In now exposes an ordinary synchronous HTTP boundary: the official map catalog and a completed
simulation response can be obtained with one request each. The browser does not currently need to
own authoritative simulation state, keep a long-lived resource lifecycle, reconnect to a stream, or
coordinate complex component-local state.

The earlier UI decision selected React + TypeScript mainly to support API/event learning and a future
SSE projection. ADR-0006 later established that the real system can remain synchronous until a
consumer demonstrates a need for events. Introducing React, Vite, Node.js and a separate development
origin before that need exists would make the first HTTP lesson harder to see and would add CORS,
build and dependency concerns unrelated to Fly-In correctness.

## Decision

Start the browser UI with native HTML, CSS, JavaScript, `fetch()` and browser-native SVG.

FastAPI serves the UI and `/api/v1` from the same origin. The initial frontend stays flat:

```text
frontend/
├── index.html
├── style.css
├── app.js
└── img/
```

The frontend is a thin visualization adapter. It must consume structured HTTP DTOs and must never
reimplement parsing, pathfinding, capacity rules, restricted-transit semantics or scheduling.

React remains a possible future upgrade only if measured UI complexity makes native browser code
materially harder to understand or maintain.

## Consequences

Positive:

- the client/server lesson is visible directly as DOM event -> `fetch()` -> HTTP -> JSON -> DOM;
- no Node/npm/Vite/build step is needed;
- no CORS configuration is required for the supported local flow;
- the UI can still use SVG, animation, keyboard controls and completed-turn playback;
- deployment and evaluator demonstration require one API process rather than two development servers.

Trade-offs:

- JavaScript does not have the compile-time guarantees previously planned with strict TypeScript;
- DOM code must stay intentionally small and separated by responsibility as the UI grows;
- if playback/inspection becomes large enough, a component framework may become justified later.

## Asset decision

Use the supplied drone/zone/connection artwork as SVG files rather than PNG for the first UI slices.
SVG keeps the visual language crisp at different sizes, accepts CSS opacity/filter treatment, and
preserves the option to expose runtime labels in later graph work. Runtime graph rendering may still
switch to SVG primitives if template assets make coordinates, capacities or labels less readable.

## Revisit trigger

Reconsider React or another framework only when one or more of these are demonstrated in real code:

- UI state/DOM coordination becomes difficult to reason about;
- repeated visual components create significant manual synchronization;
- completed playback plus inspection creates unmanageable native state transitions;
- a real streaming/reconnection consumer requires a more structured client projection.

A framework must solve an observed problem, not anticipate one.
