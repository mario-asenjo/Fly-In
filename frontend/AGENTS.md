# Frontend context

The UI milestone uses native browser technologies per ADR-0007.

Rules:

- Use plain HTML, CSS and JavaScript. Add a framework only after a later ADR proves a measured need.
- FastAPI/OpenAPI owns the transport contract; Python owns parsing, routing, capacity, restricted transit and scheduling.
- Keep frontend source files directly under `frontend/`; only `frontend/img/` is nested.
- Serve `frontend/` independently on port 8080; keep the API on port 8000 with narrow CORS.
- Log meaningful browser actions with the `[Fly-In UI]` prefix.
- Consume structured DTOs. Never derive simulation state by parsing evaluator `movement_lines`.
- Render runtime zones and connections with compact native SVG primitives. Challenger testing showed the card-shaped `zone.svg` and `conn.svg` assets overlap too much in dense graphs.
- Keep `sad.svg`, `normal.svg` and `happy.svg` for drone states and visual identity.
- Preserve map coordinate relationships while assigning enough visual spacing per coordinate unit. Dense maps grow the virtual surface instead of compressing nodes into a fixed viewport.
- Aggregate large drone groups at the same location rather than stacking dozens of icons.
- Keep completed backend results separate from local playback state.
- Keep native controls keyboard accessible, show visible focus, and do not rely on color alone.
- Respect reduced-motion preferences.

The UI supports catalog selection, synchronous solve, native SVG graph projection, local playback, pan/zoom/fit and lightweight inspection.

Read `docs/project/07_UI_PLAN.md` and `docs/decisions/ADR-0007-native-web-before-react.md` before UI work.
