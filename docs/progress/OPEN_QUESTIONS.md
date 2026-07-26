# Open questions and ambiguities

| ID | Question | Current interpretation | Needs staff confirmation? | Status |
| --- | --- | --- | --- | --- |
| Q1 | Subject says drone count is first line, maps start with comments | First significant line; actual official easy 01 is a permanent regression test | Only if evaluator rejects | OPEN |
| Q2 | Are inline comments supported or only full-line comments? | Support `#` comments after declarations | User approval and tests, 2026-07-25 | RESOLVED |
| Q3 | Are unknown metadata keys invalid? | Reject with line-aware error | Useful if official invalid fixtures clarify | OPEN |
| Q4 | Are duplicate metadata keys invalid? | Reject | No unless contradicted | OPEN |
| Q5 | Are connection self-loops legal? | Reject | Useful before final parser lock | OPEN |
| Q6 | Does undirected link capacity aggregate both directions? | Yes, shared physical connection | Useful before scheduler lock | OPEN |
| Q7 | Exact output text for a drone in restricted transit | Proposed directed `origin-destination` | Yes if sample/moulinette exists | OPEN |
| Q8 | Exact turn/link reservation window for restricted traversal | Enter link on turn t, arrive on t+1; reserve safely | Validate against examples/evaluator | OPEN |
| Q9 | Can start/end specify `zone=blocked/restricted/priority`? | Terminal role wins and effective type remains normal; declaration is preserved | Yes before edge-case lock | OPEN |
| Q10 | Official v1.5 maps differ from supplied snapshot? | Yes; `maps/maps-v1.5-added-before-m0/` is the official 1.5 package | User confirmation, 2026-07-17 | RESOLVED |
| Q11 | Challenger record is 41 in map README vs 45 in subject/rubric | 45 is official evaluation reference; 41 is stronger informal target | No | RESOLVED |
| Q12 | Actual team 42 logins | `masenjo` | User confirmation, 2026-07-17 | RESOLVED |
| Q13 | Must an invalid terminal `max_drones` value be ignored or rejected syntactically? | Require positive-integer syntax, preserve raw value, then use unlimited effect; M1.8 test | Yes before parser lock | OPEN |

When resolving, add the source/evidence and move the durable engineering decision into an ADR or
domain contract if needed.
