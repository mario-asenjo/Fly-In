---
name: flyin-evaluation-audit
description: Audit Fly-In against rubric and defense evidence
version: 1.0.0
metadata:
  hermes:
    category: software-development
    tags: [fly-in, review, evaluation, quality]
    requires_toolsets: [terminal]
---

# Fly-In evaluation audit

## When to use

Use at milestone/final review, before defense, for rubric gaps, clean-clone checks, live-coding
rehearsal, or a read-only code/architecture audit.

## Procedure

1. Read `docs/project/10_EVALUATION_MATRIX.md` and Definition of Done.
2. Inspect actual code/dependencies/tests; do not implement during an audit request.
3. Run fresh context/lint/type/test/validator/benchmark commands that exist.
4. Map each rubric row to concrete evidence or mark it missing.
5. Check parser matrix, movement/capacity/output, termination, visual behavior, README, and
   algorithm explanation.
6. Confirm official/current map provenance before benchmark claims.
7. Run `/ponytail-audit` and separate over-engineering from correctness issues.
8. Classify findings: blocker, high, medium, low.
9. Update evidence statuses only when proven.
10. Propose the minimum ordered closure plan.

## Live-coding rehearsal

Time adding `--capacity-info` through existing CLI/result/formatter seams. The full task and demo
must fit ten minutes. Do not redesign architecture during rehearsal.

## Bonus rule

Mandatory completion must be solid before bonus. “Beat 45” for Challenger means fewer than 45;
never claim bonus from a stale/different drone-count map.

## Verification

An audit ends with evidence paths/commands, reproducible gaps, severity, and no unsupported “all
good” claim.
