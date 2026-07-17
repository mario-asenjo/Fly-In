# Ponytail supervision policy

Source: https://github.com/DietrichGebert/ponytail

Ponytail is the “lazy senior developer” minimalism guard. It checks, in order, whether work can be
skipped, reused, solved by standard library/native platform/already installed dependency, reduced
to one line, or implemented with only the minimum necessary code.

For Fly-In, Ponytail is a supervisor of implementation size, not the product owner.

## Use

- Default: `full` for all coding turns.
- After a non-trivial slice: `/ponytail-review` on the diff.
- At M1-M11 milestone gates: `/ponytail-audit` on the repository.
- `lite`: only for exploring an explicitly requested larger design.
- `ultra`: only when Mario explicitly requests an aggressive delete/simplification pass.
- `off`: only temporarily to diagnose a plugin conflict, then document why.

## Fly-In hierarchy

1. User's explicit current request.
2. Fly-In 1.5 subject.
3. Evaluation rubric.
4. Tested domain invariants and safety.
5. Accepted ADRs/architecture boundaries.
6. Ponytail minimalism advice.

Never accept a Ponytail suggestion that removes:

- parser trust-boundary validation;
- line-aware errors;
- zone/link capacity correctness;
- atomic turn behavior;
- restricted future-arrival guarantee;
- independent schedule validation;
- mandatory OOP/type/lint behavior;
- accessibility basics;
- an explicit teaching/evaluation requirement.

When rejecting a review finding, state which higher rule/test requires the code. When accepting a
deliberate simplification with a known ceiling, add a precise `ponytail:` comment and benchmark/risk
upgrade trigger rather than hiding the trade-off.

Do not vendor Ponytail into this repository. Install the upstream Hermes plugin so commands/hooks
stay aligned with its maintained version.
