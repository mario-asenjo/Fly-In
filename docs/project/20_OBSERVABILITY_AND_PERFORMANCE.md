# Observability and performance discipline

## Developer observability

Collect only what answers a development/evaluation question:

- parse/path/plan/simulate duration;
- graph zone/edge count;
- candidate path count;
- explored states/relaxations where meaningful;
- planned waits/conflicts;
- zone/link utilization;
- total turns and weighted path cost;
- validator outcome.

Do not put metrics on mandatory stdout. Use explicit developer command/flag, structured result, or
logging to stderr.

## Benchmark reproducibility

- Record map SHA-256 and drone count.
- Use deterministic tie-breaks/configuration.
- Warm-up/interpreter noise makes tiny runtime differences unreliable; turns are primary.
- Run multiple timing samples only when compute speed is under investigation.
- Compare the complete map suite after each scheduler optimization.
- Keep correctness validation outside timing when reporting both clearly.

## Profiling policy

Profile before caching or replacing a clear algorithm with a complex one. Measure a representative
hard map and enough repetition to distinguish noise. Optimize total useful work, not a function that
is fast but produces a poor schedule.

## Logging policy

- Library/domain code does not configure global logging.
- Adapters/configuration choose level/handler.
- Never log full untrusted input by default.
- Include simulation/correlation ID in API/worker logs when those phases exist.
- Avoid one log per inner-loop state unless debug mode is explicit.

## Future distributed observability

If a broker/worker is introduced, add command/event IDs, retry count, queue age, worker duration,
and terminal outcome. Do not add tracing infrastructure before the distributed boundary exists.
