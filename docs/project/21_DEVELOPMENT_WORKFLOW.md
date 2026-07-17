# Development and Git workflow

## Branch/change discipline

- Keep `main` demonstrably runnable.
- Use one small branch/change set per vertical slice when practical.
- Commit tested coherent behavior, not arbitrary end-of-day state.
- Do not mix generated artifacts, formatting churn, and algorithm behavior.
- Review diff and source provenance before commit.
- Never commit secrets, virtual environments, caches, node modules, or local Hermes state.

## Commit message shape

Prefer imperative, scoped messages:

```text
parser: accept terminal capacities without enforcing them
scheduler: reserve restricted arrivals one turn ahead
api: expose line-aware map validation errors
ui: project completed turns onto SVG graph
docs: record link-capacity interpretation
```

## Review checklist

- Does the change implement only approved behavior?
- Is there a failing-then-passing test for non-trivial logic?
- Are dependency directions correct?
- Is iteration/tie-breaking deterministic?
- Did a forbidden/speculative dependency appear?
- Can code be deleted/reused per Ponytail?
- Do all gates pass?
- Are progress/evidence/risks updated without stale duplication?

## Dirty working tree

Hermes must inspect and preserve existing user changes. Never reset, checkout-overwrite, clean, or
delete unrelated files. If a requested change overlaps unexplained edits, stop and ask.

## Clean-clone rehearsal

Before milestone M6/final defense:

1. Clone to an empty directory.
2. Follow README instructions only.
3. Install dependencies in a fresh environment.
4. Run quality gates and representative maps.
5. Confirm no hidden local files/config are required.
