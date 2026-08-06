"""Filesystem-backed map input helpers shared by adapters."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class MapFileOption:
    """One selectable map file under a catalog root."""

    index: int
    path: Path
    display_path: str


class FileReader:
    """Retrieve UTF-8 source text from a filesystem path."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def retrieve_text(self) -> str:
        """Return the file content expected by the application solver."""
        return self.path.read_text(encoding="utf-8")


class MapCatalog:
    """Discover selectable map text files below one directory."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def available_maps(self) -> tuple[MapFileOption, ...]:
        """Return deterministic one-based map options."""
        paths = sorted(
            path for path in self.root.rglob("*.txt") if path.is_file()
        )
        return tuple(
            MapFileOption(
                index=index,
                path=path,
                display_path=path.relative_to(self.root).as_posix(),
            )
            for index, path in enumerate(paths, start=1)
        )

    def option_for_index(self, index: int) -> MapFileOption | None:
        """Return the selected option or None when the number is invalid."""
        for option in self.available_maps():
            if option.index == index:
                return option
        return None
