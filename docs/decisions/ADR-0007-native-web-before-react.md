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
consumer demonstrates a need for events. Introducing React, Vite and Node.js before that need exists
would make the first HTTP lesson harder to see and add build/toolchain concerns unrelated to Fly-In.

A second decision concerns process boundaries. `flyin.adapters.api` should remain the API adapter,
not become a static-file host. The browser UI is therefore served independently and crosses a small,
explicit local CORS boundary.

## Decision

Start the browser UI with native HTML, CSS, JavaScript, `fetch()` and browser-native SVG.

Keep the frontend flat:

```text
frontend/
├── index.html
├── style.css
├── app.js
└── img/
```

Run the two concerns independently during local development:

```text
API:      python -m flyin api              -> http://127.0.0.1:8000
Frontend: python3 -m http.server 8080 --directory frontend
Browser:  http://127.0.0.1:8080
```

The API enables narrow CORS only for the documented local frontend origins on port 8080. It does not
serve `/`, CSS, JavaScript or image assets. The browser calls the API explicitly at
`http://127.0.0.1:8000`.

The frontend remains a thin visualization adapter. It must consume structured HTTP DTOs and must
never reimplement parsing, pathfinding, capacity rules, restricted-transit semantics or scheduling.

React remains a possible future upgrade only if measured UI complexity makes native browser code
materially harder to understand or maintain.

## Alternatives considered

### FastAPI serves frontend and API from one origin

This avoids CORS and uses one process, but makes the API application responsible for static frontend
hosting. Rejected because preserving a clean API-only adapter is more valuable than avoiding a small
local CORS configuration.

### Separate frontend and API plus CORS

Accepted. Two explicit processes make the client/server boundary visible and the required CORS policy
is only a few lines with a narrow origin allow-list.

### Separate processes behind a reverse proxy

Would also avoid CORS, but introduces another runtime/configuration layer with no current benefit.

## Consequences

Positive:

- `flyin.adapters.api` stays focused on HTTP/JSON/OpenAPI;
- frontend hosting is independent from the Fly-In launcher;
- client/server separation is visible during teaching;
- no Node/npm/Vite/build step is needed;
- Python's standard library is sufficient to host the static client;
- CORS is explicit and deliberately narrow rather than wildcard-based.

Trade-offs:

- two local processes must be started for the browser demo;
- the frontend has an explicit API base URL during this local phase;
- CORS becomes one additional web concept to explain;
- JavaScript does not have the compile-time guarantees previously planned with strict TypeScript.

## Asset decision

Use the supplied drone/zone/connection artwork as SVG files rather than PNG for the first UI slices.
SVG keeps the visual language crisp at different sizes, accepts CSS opacity/filter treatment, and
preserves the option to expose runtime labels in later graph work. Runtime graph rendering may still
switch to SVG primitives if template assets make coordinates, capacities or labels less readable.

## Revisit trigger

Reconsider React or another framework only when real UI state/DOM coordination becomes difficult to
reason about, repeated components create significant manual synchronization, or a real streaming
consumer needs a more structured client projection.

Reconsider the two-process/CORS setup only if packaging or deployment becomes a real project goal.
