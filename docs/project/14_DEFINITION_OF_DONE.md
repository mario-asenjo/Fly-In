# Definitions of done

## Vertical slice

- Observable scope and acceptance examples were approved.
- Failing test was seen for non-trivial behavior.
- Minimum implementation passes focused and regression tests.
- Types and lint pass for affected scope; full gates pass before handoff.
- No forbidden dependency or boundary violation.
- Relevant invariant/complexity/tie-break is documented.
- Diff was inspected and Ponytail review completed.
- Progress/evaluation/decision/risk records were updated.
- Learner can explain the flow and predict one example.
- Next work was not silently included.

## Parser milestone

- Valid and invalid matrix covered.
- Physical line/cause errors proven.
- Terminal capacity ignore behavior proven.
- Old snapshot parses under documented comment interpretation.
- No pathfinding/simulation concern in parser.

## Simulation milestone

- Explicit state machine and atomic turns.
- Normal/priority/restricted/blocked semantics proven.
- Zone/link capacity and same-turn release proven.
- Independent validator rejects invalid schedules.
- Exact output and termination proven.

## Optimization milestone

- All schedules remain independently valid.
- Baseline and new results recorded for every map.
- Improvement generalizes beyond a map name.
- Complexity/memory trade-off documented.
- Category/individual target gaps explicit.

## Mandatory project

- Clean clone installs/runs.
- README meets every requirement.
- OOP/type/custom graph requirements defensible.
- Full tests, mypy, flake8 pass.
- Visual feedback meaningful.
- Rubric evidence matrix complete.
- Live-coding modification rehearsed in under ten minutes.

## API milestone

- Core works without FastAPI.
- OpenAPI/status/error contract tested.
- DTO/domain mapping explicit.
- Limits/trust-boundary validation present.
- Swagger/curl teaching walkthrough complete.

## UI milestone

- Routes are never computed client-side.
- Graph, capacities, transit, and playback match backend.
- Loading/empty/error/reconnect states handled.
- Keyboard/text alternatives/reduced motion covered.
- Critical reducer and interaction tests pass.

## External EDA milestone

- Written ADR justifies broker.
- At-least-once duplicate/order/retry/dead-letter behavior tested.
- Local development and removal path documented.
- Mandatory CLI remains unaffected.
