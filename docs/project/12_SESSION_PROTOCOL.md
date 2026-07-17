# Hermes session protocol

## Start of every session

Hermes must:

1. Read root `AGENTS.md` automatically and acknowledge relevant constraints internally.
2. Read `docs/progress/CURRENT.md`.
3. Read open questions, recent decision log, and risk entries relevant to the request.
4. Inspect Git status/diff and last commits if a repository exists.
5. Verify current files/tests rather than trusting the previous session narrative.
6. State a four-line orientation:
   - current milestone;
   - verified completed behavior;
   - blocker/risk;
   - proposed smallest next slice.
7. Wait for approval when only planning was requested.

## Before editing

- Activate the relevant Fly-In skill or bundle.
- Confirm acceptance criteria in observable terms.
- Identify affected source/rubric rows.
- Search existing code and tests.
- Ask only questions that materially change behavior; otherwise state a reversible assumption.
- Define commands that will prove completion.

## During work

- Keep a task checklist.
- Make the smallest coherent patch.
- Run the narrowest useful test after each meaningful step.
- Do not combine refactor, feature, dependency, and formatting churn without necessity.
- Preserve user changes and inspect unexpected dirty files.
- Explain non-obvious algorithm steps while they are fresh.

## Before completion

1. Run focused tests.
2. Run full tests, mypy, flake8, and context validation as applicable.
3. Run schedule validation/benchmark if algorithm behavior changed.
4. Inspect `git diff --check` and the actual diff.
5. Run `/ponytail-review`.
6. Apply safe simplifications and rerun evidence.
7. Update progress, evaluation matrix, benchmark/risk/ADR records.
8. Provide a self-contained handoff.

## End-of-session handoff format

```markdown
## Outcome
## Files changed
## Verification evidence
## Requirement/rubric coverage
## Ponytail review
## Decisions and assumptions
## Remaining risk/blocker
## Next smallest slice
```

Append one dated row/section to `docs/progress/SESSION_LOG.md`. Keep `CURRENT.md` as a compact
replacement snapshot, not a diary.

## Memory policy

Hermes global memory is bounded and loaded only at session start. Store only:

- the project path and pointer to `docs/progress/CURRENT.md`;
- stable user preferences;
- stable environment/tool facts;
- a small reminder that Fly-In 1.5/evaluation outrank old maps.

Never store large architecture prose, code state, benchmark tables, or task lists in MEMORY.
Those belong in the repository.
