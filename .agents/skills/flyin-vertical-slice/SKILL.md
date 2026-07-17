---
name: flyin-vertical-slice
description: Implement one Fly-In behavior with tests and evidence
version: 1.0.0
metadata:
  hermes:
    category: software-development
    tags: [fly-in, tdd, implementation]
    requires_toolsets: [terminal]
---

# Implement a Fly-In vertical slice

## When to use

Use after one parser, graph, simulation, scheduler, CLI, API, event, or UI behavior has explicit
scope and acceptance criteria.

## Procedure

1. Re-state the approved observable behavior and non-goals.
2. Read the relevant nested `AGENTS.md`, domain contract, and Definition of Done.
3. Search existing implementation/tests before creating files or abstractions.
4. Write the smallest test that fails for the expected missing behavior.
5. Run it and capture the expected failure.
6. Implement the minimum correct solution with explicit types and deterministic behavior.
7. Run focused test, relevant regression suite, `flake8`, and `mypy`.
8. Run independent schedule validation/benchmark if planner/simulation changed.
9. Inspect diff and run `/ponytail-review`.
10. Apply safe simplifications, rerun evidence, and update progress/teaching/evaluation records.
11. Stop at the slice boundary.

## Guardrails

- Do not create future module scaffolding.
- Do not mix feature implementation with unrelated formatting/refactors.
- Do not make a Pydantic/React/framework type a domain type.
- Do not use output text as authoritative internal state.
- Do not weaken tests to fit implementation.
- Do not claim passing commands not freshly executed.

## Handoff

Use the outcome/evidence/rubric/Ponytail/risks/next-step format in root `AGENTS.md`.
