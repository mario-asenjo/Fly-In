# Teaching notes ledger

## M3.4 - Restricted two-turn transit

### Problem and observable behavior

Restricted destinations cost two turns. A drone cannot appear in a restricted hub on the same turn it
departs; it first occupies an in-flight state and emits a connection token, then it must arrive on the
next turn. This slice makes that timeline explicit without adding the M4 capacity scheduler.

### Flow and involved classes

`simulation.model` keeps the immutable drone states and turn facts, `simulation.engine` handles
departures plus due in-flight arrivals, and `simulation.formatting` owns evaluator-safe token
joining. When a known route's next destination has `ZoneType.RESTRICTED`, the drone becomes
`InTransit(connection, origin, destination, arrival_turn)`. The emitted `TransitFact` formats as the
current internal proposal `D<ID>-<origin>-<destination>`. On the following turn, the same drone is
forced to `AtZone` for the restricted hub, and a regular `MovementFact` emits `D<ID>-<zone>`.

### Invariant and complexity

The key invariant is that an in-flight restricted drone has exactly one required arrival turn and
cannot wait on the connection or also depart onward in that same turn. Complexity remains O(D * L)
for D drones and route length L in this pre-scheduler seam.

### Example and tests

For `start-restricted-end`, turn one emits `D1-start-restricted` and stores `arrival_turn == 2`;
turn two emits `D1-restricted` and leaves the drone at the restricted hub; turn three can then emit
`D1-end`. `tests/test_simulation_foundation.py` covers departure, forced arrival, connection identity,
arrival turn, and no same-turn onward departure.

### Deliberate non-goals

This slice does not reserve future capacity, validate external schedules, choose routes for multiple
drones, optimize benchmarks, wire CLI stdout, or settle evaluator confirmation for the in-transit
token spelling beyond the documented internal convention.

## M3.1-M3.3 - Drone state, normal turns, and formatter

### Problem and observable behavior

M2 returns a `Route`, but the project still needed a deterministic simulation seam before any
capacity-aware scheduler. This slice proves the first observable turn flow: create drones at the
start hub, advance them one normal/priority step along known routes, mark arrivals at the end as
delivered, and format only movement tokens such as `D1-middle`.

### Flow and involved classes

`SimulationState.initial(parsed_map)` creates one `Drone` per parsed drone count with stable IDs
starting at one. A drone carries exactly one location object: `AtZone`, `InTransit`, or `Delivered`.
`SimulationEngine.advance_one_turn(state, routes_by_drone_id)` reads the whole input snapshot,
builds the next drone tuple and `MovementFact` tuple, then returns a `TurnResult`; it does not mutate
the previous state. `format_turn()` sorts facts by drone ID and joins their mandatory tokens.

### Invariant and complexity

The active invariant is state exclusivity: a drone cannot be both at a zone and delivered. The turn
transition is atomic at the slice boundary because all facts are derived from the input state before
the returned `SimulationState` is exposed. For D drones and route length L, this simple route lookup
is O(D * L), which is fine for this pre-scheduler seam; M4 can optimize once route allocation exists.

### Example and tests

For `start-middle-end`, turn one emits `D1-middle` and leaves the drone at `middle`; turn two emits
`D1-end` and stores the drone as `Delivered`; turn three emits an empty fact tuple. With two drones,
facts are formatted as `D1-first D2-second` even when route input order is `{2: ..., 1: ...}`.
`tests/test_simulation_foundation.py` protects the initial snapshot, atomic transition, priority as a
one-turn destination, delivered omission, and formatter ordering.

### Deliberate non-goals

Restricted two-turn transit is deliberately blocked until #29. This slice also does not validate
external schedules, reserve capacities, choose fleet routes, optimize benchmarks, wire CLI stdout,
or add API/UI/visualization.

## M2.6 - Pathfinding closure and dead-branch guard

### Problem and observable behavior

M2 needed to prove the full one-drone pathfinding matrix before simulation. A supervisor also noted
that A* should not fail just because a candidate neighbor lacks a reverse-hop entry while another
valid route exists. The observable behavior is simple: unreachable branches are ignored, while true
no-route maps still raise `NoRouteError`.

### Flow and involved classes

`AStarPathfinder` already receives a `ReverseHopDistances` table. During expansion it now checks
`can_reach_end(destination)` before calculating `hops_from(destination)`. Reachable neighbors proceed
through the same `heapq` ranking; unreachable neighbors are not queued. The returned `Route` remains
the seam for M3 simulation.

### Invariant and complexity

The guard does not change optimality because any skipped neighbor has no path to `end` according to
the same reverse BFS table that powers the heuristic. The complexity stays O((V + E) log V) for A*
plus O(V + E) for reverse BFS; the guard is an O(1) dictionary membership check per considered edge.

### Example and tests

The closure suite covers official linear input, a lexicographic fork, restricted weighted choice,
priority-only tie-breaks, priority not overriding lower cost, blocked/disconnected maps, loops, and a
lateral branch. Because Fly-In connections are bidirectional, a physically connected lateral branch
can normally reach back to the route; the exact missing-heuristic guard is therefore protected with a
small monkeypatched heuristic-table regression in `tests/test_astar_pathfinding.py`.

### Deliberate non-goals

M2 ends at one immutable route. It still does not schedule multiple drones, reserve capacity, emit
turn stdout, or produce visualization. Those begin in M3+.

## M2.4-M2.5 - Exact A* route and deterministic priority

### Problem and observable behavior

One drone now needs a concrete best path, not only reachability. A route with fewer edges is not
always better because movement cost comes from the destination zone: entering a restricted zone costs
two, while normal and priority destinations cost one. Priority is a preference only after total cost
is tied.

### Flow and involved classes

`AStarPathfinder.shortest_path(parsed_map)` builds the existing `TraversableGraph`, computes
`ReverseHopDistances` to the end, and pushes `_QueueItem` entries into a stdlib `heapq`. Each entry
tracks accumulated cost `g`, estimated total `f = g + h`, the current zone, physical connections, and
the path so far. A successful result is an immutable `Route` with zones, connections, total cost,
priority score, and `zone_names` for tests/adapters.

### Invariant and complexity

A* remains exact because the reverse-hop heuristic never overestimates remaining destination cost;
`use_heuristic=False` is kept as a Dijkstra-equivalent oracle. The search continues past the first
goal while queued candidates can still tie the best cost, so a priority route can win only among
equal-cost routes. Worst-case path search is O((V + E) log V), plus the O(V + E) reverse BFS.

### Example and tests

A three-edge route through two restricted hubs costs `2 + 2 + 1 = 5`, so it loses to a four-edge
normal route costing `4`. Between `start-normal-end` and `start-priority-end`, both cost two, so the
priority route wins. `tests/test_astar_pathfinding.py` proves weighted choice, zero-heuristic oracle
agreement, disconnected `NoRouteError`, deterministic repeatability, and priority not overriding a
cheaper route.

### Deliberate non-goals

M2.4-M2.5 still find one best route only. They do not generate multiple candidate paths, allocate a
fleet, reserve capacities, simulate turns, or format evaluator stdout. Those remain M2.6 hardening
and M3+.

## M2.1-M2.3 - Traversable graph and reverse-hop A* heuristic

### Problem and observable behavior

The parser preserves every valid zone and connection, but pathfinding needs a separate view that
answers “where can a drone legally go?” Blocked zones stay in parsed map data for diagnostics and
future visualization, but they are not traversable. Disconnected starts must fail clearly instead of
letting a planner loop forever.

### Flow and involved classes

`MapParser` still returns a `ParsedMap`. `TraversableGraph.from_parsed_map()` projects that map into
deterministic undirected adjacency: every physical connection contributes two traversals unless one
endpoint is blocked. A `Traversal` carries the destination `Zone` and the original `Connection`, so
future path output can still recover the physical link. `ReverseHopDistances.to_end()` then runs
reverse BFS from the end over this graph and stores remaining hop counts.

### Invariant and complexity

Blocked zones have no traversable neighbors, but their `Zone` objects remain in `ParsedMap.hubs`.
Connection source identity is preserved: traversing `start -> alpha` and `alpha -> start` refers to
the same physical `Connection`. Graph construction is O(V + E) time and space. Reverse BFS is also
O(V + E), and its hop count is an admissible A* heuristic because each remaining move costs at
least one turn.

### Example and tests

For `start-alpha-end`, the reverse-hop table is `end=0`, `alpha=1`, and `start=2`. If the only path
from start to end passes through `hub: blocked ... [zone=blocked]`, `start` is absent from the table
and `hops_from(start)` raises `NoRouteError`. `tests/test_traversable_graph.py` covers bidirectional
adjacency, blocked exclusion, reachable hop counts, and blocked/dead-end no-route behavior.

### Deliberate non-goals

M2.1-M2.3 do not choose a weighted route, reconstruct a path, rank priority zones, schedule several
drones, simulate turns, or print evaluator stdout. Those remain M2.4-M2.5 and M3+.

## M1.9 - Parser lock and stable errors

### Problem and observable behavior

A parser must reject invalid input deliberately instead of leaking `ValueError`, accepting typos,
or changing behavior based on tag order. The first physical line may be an optional comment; the
first significant line must be `nb_drones: <positive_integer>`.

### Flow and involved classes

`MapParser` first keeps physical line numbers while removing comments and blanks. It then validates
the drone declaration, classifies each declaration, separates one trailing metadata block, validates
tokens and local values, and finally applies cross-line map invariants. `MapParseErrorCode` gives
callers a stable category. `MapParseError` carries that code, line, cause, and a bounded excerpt.

### Invariants and complexity

Metadata keys are supported and unique for their declaration context; coordinates are integers;
regular capacities are positive; names exclude spaces and dashes; endpoints already exist; and an
undirected physical connection occurs once and never links a zone to itself. Terminal `max_drones`
is raw diagnostic metadata only, so its value is not numerically validated and effective capacity
remains unlimited. Parsing remains O(n + sum(k_i log k_i)) time and O(n) space.

### Examples and tests

Both `nb_drones: 1` and `# optional title` followed by `nb_drones: 1` parse. A line such as
`hub: bad 1 0 [color=red color=blue]` raises `DUPLICATE_METADATA` on that physical line. A terminal
`[max_drones=invalid]` is retained raw without limiting occupancy, following Fly-In 1.5 VII.4.
Sixty-four tests cover valid input, malformed syntax, oversized integers, stable errors, both
comment variants, and regressions from M1.1-M1.8; all ten official maps remain compatible.

### Flake8 and connection identity

There is no Flake8 configuration file. The Makefile executes the subject's literal `flake8 .`
command against the default 79-character standard while uv keeps dependencies outside the tree.
`Connection.left` and `right` preserve source endpoint order. `identity` sorts only their names to
create one undirected lookup key, so `a-b` and `b-a` compare as the same physical connection.

Learner check pending: explain why error code and prose are separate, and why endpoint source order
must coexist with an order-independent physical connection key.

## M1.7-M1.8 - Typed metadata and effective capacities

### Problem and observable behavior

Raw `key=value` pairs preserve source fidelity but cannot safely drive routing or scheduling. The
parser now projects supported valid metadata into typed, immutable domain fields: zone behavior,
color, regular-zone capacity, link capacity, and explicit unlimited terminal capacity.

### Flow and involved classes

`MapParser` still produces canonical raw `Metadata`, then converts `zone` to `ZoneType`, projects
`color`, and parses positive capacities. `Zone` stores both raw metadata and effective fields.
`Connection` stores raw metadata and effective link capacity. `CapacityLimit.UNLIMITED` makes the
terminal rule explicit instead of inventing a large numeric sentinel or coupling it to drone count.

### Invariants and complexity

Regular zones and links default to capacity one; explicit values are positive integers. Start/end
remain unlimited when a `max_drones` declaration is retained. Zone type defaults to
normal and is one of four enum values. Each metadata projection scans only the small canonical tuple,
so parsing remains linear in declarations apart from the existing per-block metadata sort.

### Official and derived examples

The permanent official-map test reads `easy/01_linear_path.txt`, asserts its first line is the real
title comment, then passes the complete unmodified text to `MapParser.parse()`. This proves file I/O
can stay outside the parser while real leading comments are accepted. A provenance-commented derived
fixture separately covers blocked/restricted/priority types, colors, explicit capacities, defaults,
and ignored terminal capacity declarations.

### Tests and non-goals

Tests cover every zone enum, optional/default color, zone/link defaults and explicit values,
terminal unlimited state, raw metadata retention, invalid types, zero/non-numeric regular
capacities, and official text input. M1.9 later completed malformed syntax and stable errors; graph
adjacency, movement costs, occupancy enforcement, pathfinding, simulation, and CLI remain out.

Learner check pending: explain the difference between declared metadata and effective domain state,
and why unlimited is an enum state rather than an arbitrarily large integer.

## M1.5-M1.6 - Structural identity and undirected duplicates

### Problem and observable behavior

A map cannot contain several starts/ends, reuse a zone name, connect to a later/unknown zone, or
declare the same physical link twice in either direction. Inline comments should not alter parsing
or physical diagnostics. Each invalid declaration now raises `MapParseError` at its physical line;
missing terminals fail at the physical end of input.

### Flow and involved classes

`MapParser` strips the suffix beginning at `#`, then keeps the original line number for every
remaining declaration. One `dict[str, Zone]` acts as the symbol table for global name uniqueness and
prior-definition lookup. One `set[tuple[str, str]]` records physical links. `Connection` preserves
directed `left`/`right` objects but exposes a sorted `identity` pair for undirected comparisons.

### Invariants and complexity

There is exactly one start and end; every zone name is registered once; both connection endpoints
already exist; and each unordered connection identity appears once. Dictionary/set operations are
expected O(1), so the parser remains O(n + sum(k_i log k_i)) including metadata canonicalization,
with O(n) space.

### Example and tests

After `connection: start-end`, both another `start-end` and `end-start` fail on their own physical
line because they share identity `("end", "start")`. Parameterized tests cover duplicate terminals,
duplicate names, later endpoints, missing terminals, exact/reversed links, and inline comments.
All previous acceptance tests and all ten official maps remain green.

### Deliberate non-goals

Self-loops, zone/color interpretation, effective zone/link capacities, terminal unlimited behavior,
metadata validity, stable error codes, graph adjacency, pathfinding, and simulation remain later.

Learner check pending: explain why traversal direction and physical connection identity are related
but different concepts, and why the parser uses both a dictionary and a set.

## M1.3-M1.4 - Significant lines and canonical raw metadata

### Problem

Official maps start with comments, contain blanks, and attach optional bracketed `key=value`
metadata in arbitrary tag order. Filtering those lines must not destroy the physical line number
needed by diagnostics, and parsing metadata must not prematurely decide zone/capacity semantics.

### Example input and observable result

A title comment and blank precede `nb_drones`; comments/blanks also appear among declarations.
`[max_drones=2 color=blue]` and `[color=blue max_drones=2]` produce the same canonical immutable
metadata tuple. A declaration on physical line 5 with an unknown prefix raises `MapParseError`
whose `line_number` remains 5 after ignored lines are filtered.

### Flow through classes/modules

`MapParser.parse()` enumerates physical lines before stripping and filtering blanks/full-line
comments. It keeps `(line_number, text)` pairs for significant lines, classifies each exact prefix,
and delegates bracket splitting to `_split_metadata()`. Valid tokens become sorted `(key, value)`
pairs stored immutably on `Zone` or `Connection`; absence of a block yields `()`.

### Invariant and complexity

Ignoring input lines never renumbers diagnostics, and metadata equality is independent of source
tag order. Metadata remains raw source information: later slices interpret `zone`, `color`,
`max_drones`, and `max_link_capacity`. For source length `n` and `k_i` tags in each block, parsing
costs O(n + sum(k_i log k_i)) time due to canonical sorting and O(n) space.

### Tests and deliberate non-goals

The new valid test proves comments/blanks, first significant drone declaration, canonical metadata,
empty defaults, and zone/link metadata. The error test proves a physical line survives filtering.
Inline comments, unknown/duplicate metadata validation, zone-type enums, effective capacities,
terminal capacity ignore semantics, duplicate names/connections, and full error codes remain later.

Learner check pending: explain why line numbers are captured before filtering and why raw metadata
is canonicalized now but not interpreted yet.

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
