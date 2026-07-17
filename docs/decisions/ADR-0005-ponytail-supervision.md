# ADR-0005: Use Ponytail as a minimalism supervisor

- Status: Accepted
- Date: 2026-07-10

## Context

AI-assisted projects tend to add speculative layers and dependencies. Fly-In benefits from a
clean evolutionary design but has non-negotiable correctness and evaluation constraints.

## Decision

Install the official `DietrichGebert/ponytail` Hermes plugin in full mode. Run its diff review
after non-trivial slices and audit at milestones. Treat it as a complexity guard, subordinate to
the subject, tests, type safety, parser validation, capacity correctness, and explicit requests.

## Alternatives considered

- No supervisor: higher over-engineering risk.
- Ultra mode always: may reject deliberate teaching/architecture phases.
- Copying its rules into this repo: duplicates upstream and loses plugin lifecycle/commands.

## Consequences

Smaller diffs/dependency pressure. Review findings still require engineering judgment.

## Revisit trigger

Plugin conflicts with mandatory correctness or becomes unavailable/incompatible.
