# Risk management guide

Track active risks in `docs/progress/RISKS.md` with probability, impact, trigger, mitigation,
owner, and status. A risk is not a vague concern; it must identify a future condition and action.

## Initial high-value risks

### R1 - Official map replacement

The owner confirmed `maps/maps-v1.5-added-before-m0/` as the official 1.5 package on 2026-07-17.
Trigger: a newer verified package arrives. Mitigation: preserve the current hash manifest, add a
named snapshot, then update provenance, fixtures, and benchmark evidence together.

### R2 - Ambiguous restricted transit

Connection occupancy/output timing could be interpreted differently. Trigger: test design or
peer sample disagrees. Mitigation: explicit state timeline, independent validator, request staff
clarification if observable output is affected.

### R3 - Valid but slow planner

A naive shortest-path-per-drone planner may miss strict hard targets. Trigger: M4 schedules valid
but M5 gaps remain. Mitigation: benchmark baseline, bottleneck-aware fleet completion estimate,
multi-path allocation, reservations, profile before caching.

### R4 - Infrastructure before mandatory correctness

API/React/broker work consumes time while CLI rules fail. Trigger: framework code appears before
M6 gate. Mitigation: roadmap gate, no API dependencies in domain, Ponytail audit.

### R5 - Sequential mutation collision bug

Drone iteration order changes legality/results. Trigger: simulator mutates per drone before an
atomic plan. Mitigation: turn intent/validation/apply phases and permutation tests.

### R6 - Agent-generated code not understood

The learner cannot defend algorithm choices. Trigger: large opaque patch or missing walkthrough.
Mitigation: one slice, failing test first, per-slice explanation, learner predicts behavior before
next slice.

### R7 - Mandatory stdout polluted

Visual/debug/API logging breaks evaluation output. Trigger: prints added below adapter boundary.
Mitigation: pure result objects, exact stdout integration test, stderr/explicit visual mode.

### R8 - Ponytail over-simplification

Minimalism removes essential validation or tests. Trigger: review proposes deletion affecting an
invariant. Mitigation: subject and acceptance tests outrank Ponytail; document rejection.

### R9 - Global Hermes context contamination

Project details are placed in SOUL/MEMORY and affect unrelated work or exceed limits. Trigger:
large global files. Mitigation: compact seeds and repository-local AGENTS/progress/skills.

### R10 - Teammate integration debt

Solo development creates undocumented knowledge. Trigger: several milestones lack teaching notes
or runnable examples. Mitigation: teaching gate and regular clean-context explanation rehearsal.
