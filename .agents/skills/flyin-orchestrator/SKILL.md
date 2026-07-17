---
name: flyin-orchestrator
description: Orchestrate Fly-In milestones and session continuity
version: 1.0.0
metadata:
  hermes:
    category: software-development
    tags: [fly-in, planning, orchestration]
    requires_toolsets: [terminal]
---

# Fly-In orchestrator

## When to use

Use for session starts, “what next?”, milestone planning, scope control, progress handoff, or any
request spanning more than one Fly-In module.

## Procedure

1. Read `AGENTS.md` and `docs/project/12_SESSION_PROTOCOL.md`.
2. Read `docs/progress/CURRENT.md`, open questions, recent decisions, and relevant risks.
3. Inspect Git status/diff and verify claimed state with files/commands.
4. Locate the current milestone in `docs/project/05_ROADMAP.md`.
5. Load only relevant contract documents; do not load all project prose.
6. Propose one vertical slice with:
   - observable behavior;
   - example/acceptance criteria;
   - first failing test;
   - minimum files/classes;
   - verification commands;
   - explicit non-goals.
7. Wait when approval is needed; otherwise execute only the requested approved slice.
8. At completion, enforce `docs/project/14_DEFINITION_OF_DONE.md`.
9. Update current state and session ledger; update other ledgers only when changed.

## Scope gates

- No API before mandatory core/evaluation readiness unless the user explicitly chooses a spike.
- No React before a tested API contract.
- No SSE before ordinary REST projection works.
- No broker before an accepted ADR with measured need.
- No Challenger optimization before mandatory maps and correctness are stable.

## Ponytail relationship

Keep Ponytail `full` active for coding. Use it to minimize the implementation, not to shrink the
approved behavior, robustness, teaching explanation, or evaluation evidence.

## Verification

A good orchestration response identifies verified state, one next slice, its proof, and a stop
boundary. It does not generate a whole phase or invent completion percentages.
