# Simulation timeline examples

These examples establish reasoning vocabulary. Final tokens for restricted connection names remain
an open question and may be updated after official clarification.

## One-turn normal movement

Map: `start -- middle -- goal`, one drone.

```text
Initial: D1 at start
Turn 1: D1-middle      -> D1 at middle
Turn 2: D1-goal        -> D1 delivered; simulation ends
```

## Capacity-one pipeline

Same map, two drones, all links/zones default capacity one.

```text
Initial: D1,D2 at start
Turn 1: D1-middle
Turn 2: D1-goal D2-middle
Turn 3: D2-goal
```

Turn 2 proves outgoing D1 frees `middle` for incoming D2 in the same atomic turn.

## Restricted destination

Map: `start -- restricted_hub -- goal`, one drone.

```text
Initial: D1 at start
Turn 1: D1-start-restricted_hub  -> D1 in transit, arrival fixed for turn 2
Turn 2: D1-restricted_hub        -> D1 at restricted_hub
Turn 3: D1-goal                  -> delivered
```

The departure on turn 1 must reserve the destination slot for turn 2. The drone cannot remain in
transit on turn 2 because another drone filled the zone.

## Zone capacity two

If `middle max_drones=2` and both links allow two simultaneous traversals:

```text
Turn 1: D1-middle D2-middle
Turn 2: D1-goal D2-goal
```

Zone capacity alone is insufficient if the incoming connection still defaults to one.

## Shared bidirectional link

Two drones on opposite endpoints of the same capacity-one link cannot traverse it simultaneously
under the current interpretation, even if the post-turn zones have capacity. Capacity two permits
both subject to destination occupancy.

## Atomic validation rule

Build a complete `TurnPlan` of intents/reservations, validate its aggregate effects, then apply it.
Never make these examples depend on whether D1 or D2 appears first in a loop.
