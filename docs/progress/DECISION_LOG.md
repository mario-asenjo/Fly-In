# Decision log

| Date | Decision | ADR/evidence |
| --- | --- | --- |
| 2026-07-10 | Target Fly-In 1.5; retain 1.2 only for history/fixtures | ADR/source hierarchy |
| 2026-07-10 | Modular monolith before external EDA | ADR-0001 |
| 2026-07-10 | React preferred over Qt for API learning | ADR-0002 |
| 2026-07-10 | SSE before WebSocket | ADR-0003 |
| 2026-07-10 | Terminal capacity represented explicitly as unlimited | ADR-0004 |
| 2026-07-10 | Official Ponytail plugin in full mode supervises minimalism | ADR-0005 |
| 2026-07-10 | Supplied maps stored unchanged as v1.2 snapshot | User instruction + source hierarchy |
| 2026-07-25 | Support full-line and inline `#` comments while preserving physical lines | User approval + M1.5 tests |
| 2026-07-26 | A leading comment is optional; drone count is the first significant line | User clarification + M1.9 tests |
| 2026-07-26 | Reject unknown/duplicate metadata and self-connections at parser lock | Domain contract + M1.9 tests |
| 2026-07-26 | Ignore terminal `max_drones` values without numeric validation | Fly-In 1.5 VII.4 + M1.9 test |
| 2026-07-26 | Run literal `flake8 .` with no Flake8 configuration file | Fly-In 1.5 III.2 + raw gate |

Append concise accepted decisions here. Detailed rationale belongs in ADRs.
