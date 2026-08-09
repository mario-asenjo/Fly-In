"""Official-map catalog and synchronous simulation routes."""

from fastapi import APIRouter, status

from ...files import FileReader, MapCatalog, default_map_root
from ....application import FlyInSolver
from ..errors import ApiError
from ..mappers import result_to_solve_response
from ..schemas import (
    ErrorResponse,
    MapCatalogOptionResponse,
    MapCatalogResponse,
    SolveResponse,
)

_ERROR_RESPONSES: dict[int | str, dict[str, object]] = {
    404: {"model": ErrorResponse},
    422: {"model": ErrorResponse},
    500: {"model": ErrorResponse},
}

maps_router = APIRouter(prefix="/maps", tags=["maps"])


@maps_router.get("", response_model=MapCatalogResponse)
def list_maps() -> MapCatalogResponse:
    """List deterministic one-based official map selections."""
    catalog = MapCatalog(default_map_root()).available_maps()
    return MapCatalogResponse(
        maps=[
            MapCatalogOptionResponse(
                index=option.index,
                display_path=option.display_path,
            )
            for option in catalog
        ]
    )


@maps_router.post(
    "/{map_index}/simulate",
    response_model=SolveResponse,
    responses=_ERROR_RESPONSES,
)
def simulate_map_by_index(map_index: int) -> SolveResponse:
    """Solve one server-known official map selected by catalog index."""
    option = MapCatalog(default_map_root()).option_for_index(map_index)
    if option is None:
        raise ApiError(
            status.HTTP_404_NOT_FOUND,
            "MAP_NOT_FOUND",
            f"map index {map_index} was not found.",
            {"map_index": map_index},
        )

    source_map = FileReader(option.path).retrieve_text()
    return result_to_solve_response(FlyInSolver.solve_text(source_map))
