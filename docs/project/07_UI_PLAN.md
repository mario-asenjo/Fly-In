# React UI plan

Status: target design for milestone M9.

## Purpose

Visualize the map and simulation so topology, occupancy, restricted transit, bottlenecks, and
parallel movement are easier to understand. The UI is also the concrete API/event-learning
consumer.

## Technology decision

- React + TypeScript strict mode.
- Vite for development/build.
- SVG for graph rendering first.
- Native browser controls/CSS before component libraries.
- Generated or schema-checked API types after the OpenAPI contract stabilizes.
- No client state framework until React state/reducer is demonstrably insufficient.

Ponytail should strongly challenge graph libraries, UI kits, animation libraries, and global
state dependencies. A visualization library must never provide graph/pathfinding logic.

## Main screen

### Input panel

- Select or paste map text.
- Validate.
- Show line-aware errors.
- Submit simulation.

### Graph canvas

- Position zones from integer coordinates using a deterministic viewport transform.
- Draw bidirectional connections and capacity labels.
- Show zone name/type/color/effective capacity.
- Show start/end as unlimited regardless of declared metadata.
- Show blocked zones distinctly.
- Show drones at zones and on restricted links.
- Avoid relying on color alone for meaning.

### Playback controls

- Run/pause playback.
- Step forward.
- Step backward through already received/projected events.
- Reset to turn zero.
- Speed control.
- Current turn and completion status.

Playback controls usually affect local visualization time, not authoritative backend computation.
This distinction should be taught explicitly.

### Inspection panel

- Selected zone occupancy/capacity.
- Selected link use/capacity.
- Drone state and route/history if available.
- Makespan, delivered count, path cost, moved drones per turn.
- Benchmark target and delta for recognized developer fixtures only; do not hard-code map logic
  into the production solver.

## State model

Separate:

1. Server resource state: simulation ID/status/result.
2. Ordered event log received.
3. Deterministic projection at each sequence/turn.
4. Local playback cursor/speed/selection.
5. Transient request/error state.

One reducer can project events initially. Do not duplicate backend rules; reject/impossible event
sequences should surface as client errors rather than be “fixed” in React.

## Delivery slices

1. Render one hard-coded API response, no network.
2. Fetch a completed synchronous result.
3. Input and validation errors.
4. Basic graph and turn stepping.
5. Capacity/transit details.
6. SSE append and live projection.
7. Reconnect using last event ID/sequence.
8. Accessibility, empty/loading/error/responsive states.

## Accessibility

- All controls keyboard accessible with visible focus.
- Buttons have explicit labels.
- Status changes use an appropriate live region without excessive announcements.
- Zone information is available in text/list form as well as SVG.
- Color contrast is sufficient; arbitrary map colors may require a safe display treatment.
- Animation respects reduced-motion preference.

## Tests

- Coordinate-to-viewport transform.
- Event reducer/projection.
- Playback cursor behavior.
- API error rendering including line number.
- Critical keyboard controls.
- One end-to-end happy path only after the real API exists.

Avoid broad snapshots that fail on harmless SVG markup changes.
