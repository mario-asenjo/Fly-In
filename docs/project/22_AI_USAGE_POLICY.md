# AI assistance and disclosure policy

Fly-In explicitly requires learners to understand and defend their work. AI may accelerate
learning, planning, testing ideas, documentation, and review, but cannot replace comprehension.

## Allowed workflow

- Ask for alternative designs and trade-offs.
- Convert requirements into acceptance examples.
- Generate a small proposed test/patch, then inspect and explain it.
- Debug from evidence and trace root cause.
- Review types, complexity, edge cases, and over-engineering.
- Draft documentation that is verified against real code/results.

## Rejected workflow

- Generate the entire solution and copy it unexplained.
- Claim benchmark/test results not run locally.
- Hide AI-written key algorithms from the teammate/evaluator.
- Allow AI memory to become the only project record.
- Paste source-prohibited libraries/implementations.

## Understanding gate

Before accepting important generated code, Mario should be able to:

1. state the behavior/invariant;
2. predict one example;
3. trace the code path;
4. explain why the test fails without the change;
5. explain complexity/trade-off;
6. modify a small related behavior unaided.

## README disclosure draft

Adapt truthfully near completion:

> AI tools were used as a learning and review assistant for requirement analysis, test-case ideas,
> architecture trade-off discussion, documentation structure, and code review. Every accepted
> implementation was developed incrementally, tested locally, inspected, and retained only after
> the team could explain its behavior and trade-offs. AI was not used as a substitute for the
> custom graph/pathfinding implementation or peer-evaluation understanding.

Update this statement to match actual usage; never include capabilities/tasks that did not occur.
