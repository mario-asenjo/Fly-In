# Active risk register

| ID | Risk | Probability | Impact | Trigger | Mitigation | Status |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | v1.2 map snapshot differs from 1.5 | High | High | Final benchmark uses old counts | Refresh official maps; derived fixtures/provenance meanwhile | ACTIVE |
| R2 | Restricted transit/output ambiguity | Medium | High | Conflicting example/evaluator behavior | Explicit timeline/tests; seek clarification | ACTIVE |
| R3 | Valid planner misses hard targets | Medium | High | M5 benchmark gaps | Baseline, profile, bottleneck/fleet allocation | WATCH |
| R4 | API/UI/broker begins before mandatory core | Medium | High | Framework commit before M6 | Roadmap gates + Ponytail audit | CONTROLLED |
| R5 | Sequential mutation creates collision/order bugs | Medium | High | Result changes with drone order | Atomic plans and permutation tests | ACTIVE |
| R6 | Learner cannot defend generated code | Medium | Critical | Large unexplained patch | Small slices, walkthrough, prediction/tests | ACTIVE |
| R7 | Diagnostics corrupt CLI stdout | Medium | High | `print` below adapter | Exact stdout tests, stderr/flags | ACTIVE |
| R8 | Ponytail removes required robustness | Low | High | Suggested deletion breaks invariant | Spec/tests outrank plugin | CONTROLLED |
| R9 | Global Hermes files become project dump | Medium | Medium | Oversized MEMORY/SOUL | Compact seeds; repo progress files | CONTROLLED |
| R10 | Solo knowledge blocks teammate later | Medium | Medium | Missing teaching notes | Teaching gate/workshop | WATCH |

Review at each milestone. Close only when the condition can no longer occur or a permanent control
is evidenced.
