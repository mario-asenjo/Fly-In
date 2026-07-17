# Defense and peer-evaluation plan

## Ten-minute technical story

1. Problem and constraints: graph, fleet, capacities, turns.
2. Parser/domain model and why terminal capacity is special.
3. Custom graph/pathfinding and destination-weighted cost.
4. Atomic scheduler/reservations, including restricted timeline.
5. One easy-map walkthrough.
6. One hard capacity/restricted walkthrough.
7. Benchmark table and one measured optimization.
8. Visual representation and architecture evolution, if relevant.

## Questions every teammate must answer

- Why is the graph implementation custom?
- Why can an undirected edge still have directional traversal cost?
- How does same-turn release work atomically?
- How do you guarantee a restricted arrival cannot wait?
- How is link capacity shared/enforced?
- How are dead ends/loops/disconnected graphs handled?
- What is the complexity of each major algorithm stage?
- Why can the CLI/API/UI share the same core?
- Why were events/broker introduced or deferred?
- Which optimization improved which maps and what did it cost?

## Demonstrations

- Clean build/run.
- Invalid parser case with line/cause.
- Default exact simulation output.
- Visual view with colors/positions/capacities.
- Easy/medium/hard benchmark evidence.
- `mypy .`, `flake8`, and tests.

## Live coding

Rehearse `--capacity-info` from the current code, under ten minutes, while explaining:

1. CLI flag location;
2. existing turn capacity data;
3. formatter extension;
4. preservation of default output;
5. focused test/demo.

## Failure handling

If a benchmark target is missed, never hide it. Show validity, category expectation, exact gap,
known bottleneck, and next general optimization. If a source ambiguity remains, show the recorded
interpretation and test.
