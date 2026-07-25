# Teaching notes ledger

## M1.2 - Regular hubs and multiple connections

### Problem

Replace the fixed four-line parser with a parser for valid maps containing any number of regular
hubs and connections, without introducing the later validation/error system.

### Example input and observable result

Four drones, start, hubs `alpha` and `beta`, end, and the three declarations `start-alpha`,
`alpha-beta`, and `beta-end` produce two ordered regular hubs and three ordered connections. Every
connection endpoint is the same `Zone` object stored by the parsed map.

### Flow through classes/modules

`MapParser.parse()` separates the drone-count line from declaration lines, then walks declarations
once. Zone declarations create a `Zone`, append regular hubs when applicable, and register every
zone by name. A later connection looks up both names in that dictionary and stores references to
the existing objects. Mutable lists are local construction tools; `ParsedMap` receives tuples.

### Invariant and complexity

A valid connection can only resolve zones already declared in the input, so parsed connections do
not contain detached names or duplicate `Zone` copies. Hub and connection order follows source
order deterministically. For source length `n`, parsing is O(n) expected time with dictionary
lookups and O(n) space across split lines, zone lookup, hubs, connections, and the immutable result.

### Test and deliberate non-goals

`test_parses_regular_hubs_and_multiple_connections` proves multiple drones, two regular hubs,
integer coordinates including a negative value, three connections, source order, and object
identity. Comments, metadata, stable errors, duplicate rules, undirected equality, graph behavior,
and adapters remain later slices.

Learner check pending: explain why `zones` is a dictionary while `hubs` and `connections` preserve
ordered tuples in the returned map.

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
