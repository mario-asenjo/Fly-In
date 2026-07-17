# Test context

Tests are executable requirements, not an implementation mirror.

- Prefer behavior-oriented tests through public boundaries.
- Unit-test parser rules, value-object invariants, reservation logic, and turn transitions.
- Add integration tests for CLI and later API contracts.
- For each fixed bug, first reproduce it with one regression test.
- Preserve supplied maps unchanged; put derived fixtures under `tests/fixtures/`.
- Every derived fixture starts with comments recording source, change, and reason.
- Avoid mocks for pure domain collaborators; use small real objects.
- Do not assert internal call counts unless they are the behavior.
- Validate full schedules independently from the planner so a planner cannot grade itself.
- Benchmark tests report turn counts but mandatory correctness tests do not depend on timing.

When official maps are replaced, update the provenance manifest and expected benchmark table
in the same change.
