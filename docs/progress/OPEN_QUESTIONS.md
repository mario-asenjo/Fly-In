# Open questions and ambiguities

| ID | Question | Current interpretation | Needs staff confirmation? | Status |
| --- | --- | --- | --- | --- |
| Q1 | Subject says drone count is first line, maps may start with comments | A leading comment is optional; `nb_drones` is the first significant line | User clarification + both variants tested, 2026-07-26 | RESOLVED |
| Q2 | Are inline comments supported or only full-line comments? | Support `#` comments after declarations | User approval and tests, 2026-07-25 | RESOLVED |
| Q3 | Are unknown metadata keys invalid? | Reject with line-aware error so typos cannot silently alter behavior | Parser-lock decision, 2026-07-26 | RESOLVED |
| Q4 | Are duplicate metadata keys invalid? | Reject because tag order must not determine effective semantics | Parser-lock decision, 2026-07-26 | RESOLVED |
| Q5 | Are connection self-loops legal? | Reject as invalid topology under the strict parser policy | Parser-lock decision, 2026-07-26 | RESOLVED |
| Q6 | Does undirected link capacity aggregate both directions? | Yes, shared physical connection | Useful before scheduler lock | OPEN |
| Q7 | Exact output text for a drone in restricted transit | Proposed directed `origin-destination` | Yes if sample/moulinette exists | OPEN |
| Q8 | Exact turn/link reservation window for restricted traversal | Enter link on turn t, arrive on t+1; reserve safely | Validate against examples/evaluator | OPEN |
| Q9 | Can start/end specify `zone=blocked/restricted/priority`? | Preserve the valid declaration, but terminal role wins and effective type is normal | Parser-lock decision + regression test, 2026-07-26 | RESOLVED |
| Q10 | Official v1.5 maps differ from supplied snapshot? | Yes; `maps/maps-v1.5-added-before-m0/` is the official 1.5 package | User confirmation, 2026-07-17 | RESOLVED |
| Q11 | Challenger record is 41 in map README vs 45 in subject/rubric | 45 is official evaluation reference; 41 is stronger informal target | No | RESOLVED |
| Q12 | Actual team 42 logins | `masenjo` | User confirmation, 2026-07-17 | RESOLVED |
| Q13 | Must an invalid terminal `max_drones` value be ignored or rejected syntactically? | Preserve any non-empty raw value and do not validate it numerically; terminal capacity is unlimited | Fly-In 1.5 VII.4 says present metadata is ignored and is not a validation error; locked 2026-07-26 | RESOLVED |

When resolving, add the source/evidence and move the durable engineering decision into an ADR or
domain contract if needed.
