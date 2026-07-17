# Source of truth and contradiction protocol

## Authority order

1. `docs/sources/flyin_1.5.pdf`
   - Normative functional specification, including Makefile rules.
   - Current parser, movement, output, README, and benchmark requirements.
2. `docs/sources/Intra-Projects-Fly-in-Edit.pdf`
   - Normative evaluation behavior and evidence expected during defense.
   - Includes the `--capacity-info` live-coding request.
3. `maps/maps-v1.5-added-before-m0/`
   - Official Fly-In 1.5 maps, confirmed by the project owner on 2026-07-17.
   - Authoritative topology and benchmark inputs where the subject refers to provided maps.
4. `maps/provided-v12-snapshot/`
   - Exact historical v1.2 snapshot retained as immutable comparison evidence only.
5. `docs/sources/fly-in_1.2.pdf`
   - Historical delta only.
6. `maps/provided-v12-snapshot/README_maps.md`
   - Helpful historical context, not a binding requirement.
7. Project architecture documents and ADRs.
   - Interpret and implement the sources; cannot override them.

## Contradiction protocol

When two sources disagree:

1. Quote or identify both exact sections/files.
2. Classify the conflict as normative, fixture, wording, or implementation choice.
3. Apply the authority order.
4. Prefer an interpretation that is strict, testable, and reversible.
5. Record the issue in `docs/progress/OPEN_QUESTIONS.md`.
6. Add a test that names the interpretation when code depends on it.
7. Ask project staff only if the interpretation changes public behavior or evaluation risk.
8. Update the record when an official clarification arrives.

Never silently normalize a source file and never fabricate an “official” corrected map.

## Fact, interpretation, decision

Use these labels in documentation:

- **FACT**: directly stated by the 1.5 subject or evaluation rubric.
- **INTERPRETATION**: behavior inferred to reconcile wording/examples.
- **DECISION**: an engineering choice among compliant alternatives.
- **ASSUMPTION**: temporary belief awaiting official confirmation.
- **NON-GOAL**: intentionally deferred scope.

## Source immutability

Files in `docs/sources/`, `maps/maps-v1.5-added-before-m0/`, and
`maps/provided-v12-snapshot/` are immutable evidence. Validation scripts compare their manifest
hashes. If a new official package arrives:

1. Add it as a new named snapshot or deliberately replace the provisional snapshot.
2. Regenerate the manifest.
3. Diff semantics, not only bytes.
4. Update delta, open questions, fixtures, benchmarks, and tests in one reviewable change.

## Evaluation precedence nuance

The subject defines the product. The rubric reveals how peers will test it. If the rubric is
less strict than the subject, implement the subject. If the rubric requests additional
demonstration behavior such as `--capacity-info`, design boundaries so the change is easy and
rehearse it without permanently corrupting mandatory output.
