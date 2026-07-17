---
name: flyin-spec-guardian
description: Enforce Fly-In 1.5 rules and source precedence
version: 1.0.0
metadata:
  hermes:
    category: software-development
    tags: [fly-in, specification, evaluation]
---

# Fly-In specification guardian

## When to use

Use for parser/domain/simulation/output decisions, source conflicts, map updates, evaluation
questions, edge cases, or review of requirement compliance.

## Procedure

1. Read `docs/project/02_SOURCE_OF_TRUTH.md`.
2. Read the relevant section of `docs/project/03_DOMAIN_CONTRACT.md`.
3. If claims remain uncertain, inspect the exact supplied PDF/source page rather than memory.
4. Label each conclusion `FACT`, `INTERPRETATION`, `DECISION`, or `ASSUMPTION`.
5. For contradictions, apply the documented protocol and update `OPEN_QUESTIONS.md`.
6. Express the conclusion as an executable acceptance example/test.
7. Reject a code/design change that violates a higher-priority source.

## Always guard

- Custom graph; no NetworkX/graphlib graph logic.
- OOP and full type safety with mypy/flake8.
- Unlimited start/end and ignored terminal `max_drones`.
- Bidirectional duplicate/link-capacity semantics.
- Destination-based costs and blocked zones.
- Atomic same-turn releases/entries.
- Mandatory next-turn restricted arrival.
- Exact evaluator-safe stdout and termination.
- 1.5 benchmarks, not stale map README values.

## Map snapshot rule

Never edit `maps/provided-v12-snapshot`. Derived fixtures state provenance and delta. When fresh
official maps arrive, compare and update all dependent evidence together.

## Verification

Return the source rank, exact rule/ambiguity, chosen interpretation, risk, and test proving it.
