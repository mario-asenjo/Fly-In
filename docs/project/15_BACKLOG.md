# Prioritized backlog

This is a planning inventory, not permission to implement everything. Move only the approved
smallest item into `docs/progress/CURRENT.md`.

## Now - M0/M1

- [ ] Confirm team logins and Python 3.12 availability.
- [ ] Initialize Git repository if needed and establish clean baseline.
- [ ] Install dev extras and run empty gates.
- [ ] Define minimal valid map fixture.
- [ ] Write first parser acceptance test.
- [ ] Implement only drone count/start/end/connection needed by that test.
- [ ] Add physical-line error representation.

## Next - parser/graph

- [ ] Metadata tokenizer and defaults.
- [ ] Zone uniqueness and terminal count.
- [ ] Connection prior definition and reversed duplicate.
- [ ] Types/capacity/terminal ignore behavior.
- [ ] Blocked traversability.
- [ ] Reachability and weighted path.

## Later - simulation/scheduler

- [ ] Drone state machine.
- [ ] Atomic one-turn movement.
- [ ] Restricted transit timeline.
- [ ] Independent schedule validator.
- [ ] Zone/link reservation table.
- [ ] Multi-path route allocation.
- [ ] Deadlock detection/prevention.

## Later - product/evaluation

- [ ] Exact CLI.
- [ ] Colored terminal view.
- [ ] Benchmark harness and table.
- [ ] Full README/resource/AI-use statement.
- [ ] Capacity-info live-coding rehearsal.

## Future - learning expansion

- [ ] Typed in-process events.
- [ ] FastAPI validation/solve endpoints.
- [ ] Simulation resource and SSE.
- [ ] React graph/playback.
- [ ] Optional broker ADR and experiment.
- [ ] Teammate onboarding workshop.

## Explicit parking lot

- Database/history.
- Authentication.
- WebSocket.
- NATS/RabbitMQ.
- Deployment.
- Challenger-specific research.

Parking-lot items require evidence and an ADR before promotion.
