# Frontend context

This directory is intentionally empty until the UI milestone is approved. Do not scaffold
React during parser/pathfinding/scheduler work.

When the UI phase begins:

- Use React with TypeScript strict mode and Vite unless an ADR changes the choice.
- Treat the FastAPI OpenAPI contract as the transport authority.
- Keep authoritative routing and simulation decisions in the backend.
- Render coordinates, connections, metadata colors, capacities, drones, transit, and turns.
- Provide keyboard-accessible run/pause/step/reset/speed controls.
- Keep view state separate from server simulation state.
- Start with a static completed simulation response; add SSE after the projection works.
- Add a dependency only after checking browser-native SVG/CSS and installed packages.
- Test pure transformations and critical interaction behavior; avoid snapshot-test noise.

Read `docs/project/07_UI_PLAN.md` and activate the `flyin-ui-implementation` skill before work.
