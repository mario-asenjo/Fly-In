# Active risk register

| ID | Risk | Probability | Impact | Trigger | Mitigation | Status |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | Official maps change or are replaced | Low | High | New verified package arrives | Preserve current package hash; add a named snapshot and update benchmarks/provenance together | CONTROLLED |
| R2 | Restricted transit/output ambiguity | Medium | High | Conflicting example/evaluator behavior | Explicit timeline/tests; seek clarification | ACTIVE |
| R3 | Valid planner misses hard targets | Medium | High | M5 benchmark gaps | Baseline, profile, bottleneck/fleet allocation | WATCH |
| R4 | API/UI/broker begins before mandatory core | Low | High | Framework commit before M6 | M6 is complete; ADR-0006 permits synchronous REST while events/SSE/UI/broker remain gated | CONTROLLED |
| R5 | Sequential mutation creates collision/order bugs | Medium | High | Result changes with drone order | Atomic plans and permutation tests | ACTIVE |
| R6 | Learner cannot defend generated code | Medium | Critical | Large unexplained patch | Small slices, walkthrough, prediction/tests | ACTIVE |
| R7 | Diagnostics corrupt CLI stdout | Medium | High | `print` below adapter | Exact stdout tests, stderr/flags | ACTIVE |
| R8 | Ponytail removes required robustness | Low | High | Suggested deletion breaks invariant | Spec/tests outrank plugin | CONTROLLED |
| R9 | Global Hermes files become project dump | Medium | Medium | Oversized MEMORY/SOUL | Compact seeds; repo progress files | CONTROLLED |
| R10 | Solo knowledge blocks teammate later | Medium | Medium | Missing teaching notes | Teaching gate/workshop | WATCH |
| R11 | API adapter leaks solver/filesystem failures as generic 500 responses | High | High | `SolveError` or `OSError` reaches FastAPI unhandled | Stable error mapper plus integration tests for each application failure class | ACTIVE |
| R12 | Numeric catalog indices are mistaken for durable map IDs | Medium | Medium | Map order changes between versions | Document indices as version-local selection keys; introduce stable slugs only when a consumer needs persistence | ACTIVE |

Review at each milestone. Close only when the condition can no longer occur or a permanent control
is evidenced.
