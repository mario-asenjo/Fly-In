from flyin.parsing import MapParser
from flyin.pathfinding import CandidateRouteFinder
from flyin.scheduling import RouteAllocator
from flyin.simulation import ScheduleValidator


NON_PREFIX_MAP = "\n".join(
    (
        "nb_drones: 6",
        "start_hub: start 0 0",
        "hub: a 1 0",
        "hub: b 1 1",
        "hub: c 2 0",
        "hub: d 1 2",
        "hub: e 2 1",
        "hub: f 2 2",
        "end_hub: end 3 0",
        "connection: start-a",
        "connection: a-c",
        "connection: c-end",
        "connection: start-b",
        "connection: b-c",
        "connection: b-e",
        "connection: e-end",
        "connection: start-d",
        "connection: d-f",
        "connection: f-end",
    )
)

RENAMED_NON_PREFIX_MAP = "\n".join(
    (
        "nb_drones: 6",
        "start_hub: start 0 0",
        "hub: u 1 0",
        "hub: v 1 1",
        "hub: w 2 0",
        "hub: x 1 2",
        "hub: y 2 1",
        "hub: z 2 2",
        "end_hub: end 3 0",
        "connection: start-u",
        "connection: u-w",
        "connection: w-end",
        "connection: start-v",
        "connection: v-w",
        "connection: v-y",
        "connection: y-end",
        "connection: start-x",
        "connection: x-z",
        "connection: z-end",
    )
)


def test_route_allocator_considers_non_prefix_route_combinations() -> None:
    parsed_map = MapParser().parse(NON_PREFIX_MAP)
    candidates = CandidateRouteFinder.find_candidates(parsed_map, max_routes=6)

    assert candidates[0].zone_names == ("start", "a", "c", "end")
    assert candidates[1].zone_names == ("start", "b", "c", "end")
    assert candidates[2].zone_names == ("start", "b", "e", "end")
    assert candidates[3].zone_names == ("start", "d", "f", "end")

    schedule = RouteAllocator.schedule(parsed_map, max_routes=6)
    validation = ScheduleValidator.validate(parsed_map, schedule)

    assert validation.is_valid, validation.errors
    assert len(schedule) == 4


def test_route_allocator_result_is_stable_under_zone_renaming() -> None:
    original = MapParser().parse(NON_PREFIX_MAP)
    renamed = MapParser().parse(RENAMED_NON_PREFIX_MAP)

    original_schedule = RouteAllocator.schedule(original, max_routes=6)
    renamed_schedule = RouteAllocator.schedule(renamed, max_routes=6)

    assert ScheduleValidator.validate(original, original_schedule).is_valid
    assert ScheduleValidator.validate(renamed, renamed_schedule).is_valid
    assert len(original_schedule) == len(renamed_schedule) == 4
