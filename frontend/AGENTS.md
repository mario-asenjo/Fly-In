# Frontend context

The UI milestone uses native browser technologies per ADR-0007.

Rules:

- Use plain HTML, CSS and JavaScript. Add a framework only after a later ADR proves a measured need.
- FastAPI/OpenAPI owns the transport contract; Python owns parsing, routing, capacity, restricted transit and scheduling.
- Keep frontend source files directly under `frontend/`; only `frontend/img/` is nested.
- Keep frontend hosting separate from the API. Serve `frontend/` on port 8080 with Python's standard static server; the API remains on port 8000 with narrow CORS.
- Log meaningful browser actions with the `[Fly-In UI]` prefix.
- Consume structured DTOs. Never derive simulation state by parsing evaluator `movement_lines`.
- Try the supplied zone, connection and drone SVG assets first. Use native SVG primitives only after a real visual test proves the supplied assets hurt readability or scaling.
- Keep completed backend results separate from local playback state.
- Keep native controls keyboard accessible, show visible focus, and do not rely on color alone.
- Respect reduced-motion preferences.
- Separate scripts only for real responsibilities: transport, graph rendering, turn projection, output rendering and playback.

PR #73 covers the catalog selector plus the synchronous solve/playback scope originally planned for #72.

Read `docs/project/07_UI_PLAN.md` and `docs/decisions/ADR-0007-native-web-before-react.md` before UI work.
