# Prioritized backlog

This is a planning inventory, not permission to implement everything. Move only the approved
smallest item into `docs/progress/CURRENT.md`.

## Completed mandatory foundation - M0-M6

- [x] Parser, custom graph/pathfinding, deterministic simulation, capacity scheduler, benchmarks,
  application service, evaluator CLI, terminal visualization, and defense hardening.

## Now - M7 synchronous FastAPI

- [x] CLI/API launcher, FastAPI factory, health, and OpenAPI bootstrap.
- [ ] Close official-map catalog and synchronous simulation with stable errors and full gates.
- [ ] Complete Swagger/curl teaching walkthrough.

## Next - M8 events and streaming readiness

- [ ] Typed immutable in-process events for a real playback/stream consumer.
- [ ] Ordered/idempotent projection tests.
- [ ] SSE only after ordinary REST and event ordering are proven.

## Later - M9 product UI

- [ ] React graph/playback over the backend contract.
- [ ] Loading, empty, error, accessibility, and reconnection states.

## Future - learning expansion

- [ ] Content validation/upload only after the server-map flow is closed.
- [ ] Simulation resource only if lifecycle or asynchronous work becomes real.
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
