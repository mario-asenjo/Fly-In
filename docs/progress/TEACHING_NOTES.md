# Teaching notes ledger

## M1.1 - Smallest linear-map parser

### Problem

Turn the smallest comment-free Fly-In map into typed objects without adding graph or simulation
behavior.

### Example input and observable result

`nb_drones: 1`, a `start_hub`, an `end_hub`, and `connection: start-end` produce a `ParsedMap`
with one drone, the two named zones, and one connection referencing those zones.

### Flow through classes/modules

`MapParser.parse()` splits the four source lines, converts numeric fields, creates immutable
`Zone` objects, resolves the connection endpoint names, and returns an immutable `ParsedMap`
containing one `Connection`. `parsing` depends on `domain`; the domain imports no parser or adapter.

### Invariant and complexity

The connection endpoints are resolved to zones defined by the parsed start and end names instead
of becoming unrelated strings. For input length `n`, parsing is O(n) time and O(n) temporary space
because `splitlines()` materializes the lines; the fixed M1.1 result contains constant-size state.

### Test and deliberate non-goals

`tests/test_minimal_map_parsing.py` proves the public import, drone count, terminal names and
coordinates, one connection whose endpoints are the parsed zone objects, and immutable parsed
state. Comments, regular hubs, metadata, malformed-input errors, graph behavior, file I/O, and CLI
output remain later slices.

Learner check pending: predict the three domain objects and trace which module creates each one.

After each accepted slice, record whether Mario can:

- predict the behavior before running it;
- trace the request/data flow;
- name the protected invariant;
- explain the test and failure mode;
- explain the main trade-off/complexity.

Do not paste generated tutorials here before behavior exists. Use the template in
`docs/project/11_TEACHING_TRACK.md`.
