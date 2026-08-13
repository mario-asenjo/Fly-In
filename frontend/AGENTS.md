# Frontend context

The UI milestone is active and starts with native browser technologies per ADR-0007.

Rules for frontend work:

- Use plain HTML, CSS and JavaScript first; no React/Vite/TypeScript unless a later ADR proves a need.
- Treat the FastAPI HTTP/OpenAPI contract as the transport authority.
- Keep authoritative routing and simulation decisions in the backend.
- Keep `frontend/` flat (`index.html`, `style.css`, `app.js`) except for `frontend/img/` assets.
- Keep frontend hosting separate from `flyin.adapters.api`; the API must not serve frontend files.
- Serve `frontend/` independently on port 8080 with Python's standard-library static HTTP server.
- Call the API at `http://127.0.0.1:8000`; FastAPI permits only the documented local frontend origins through narrow CORS.
- Log meaningful browser actions with the `[Fly-In UI]` prefix while the teaching client is small.
- Consume structured API DTOs; never reconstruct simulation semantics by parsing evaluator stdout.
- Use browser-native SVG/CSS before graph, UI, animation or state-management dependencies.
- Keep local playback state separate from authoritative backend simulation data.
- Provide keyboard-accessible controls and visible focus; do not rely on color alone for meaning.
- Respect `prefers-reduced-motion` when animation is introduced.
- Test API/CORS integration and pure transformations; avoid snapshot-test noise.

Current slice (#71): load the official catalog into a polished selector. **Simulate** logs intent only.
Next slice (#72): call the completed synchronous simulation endpoint and project its result locally.

Read `docs/project/07_UI_PLAN.md` and `docs/decisions/ADR-0007-native-web-before-react.md` before UI work.
