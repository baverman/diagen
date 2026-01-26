from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Protocol, TypedDict

if TYPE_CHECKING:
    from .layouts import LayoutNode


BackendStyle = dict[str, int | float | str | list[str]]
ClassList = str | list[str]


class Layout(Protocol):
    def size(self, node: 'LayoutNode') -> tuple[float, float]: ...

    def arrange(self, node: 'LayoutNode') -> None: ...


@dataclass(frozen=True)
class Span:
    start: int = 0
    end: int = 1
    rel_start: bool = field(default=True, kw_only=True)
    rel_end: bool = field(default=True, kw_only=True)


@dataclass(frozen=True, kw_only=True)
class NodeProps:
    direction: int
    layout: 'Layout'
    scale: float
    size: tuple[float | None, float | None]
    padding: tuple[float, float, float, float]
    gap: tuple[float, float]
    virtual: bool
    align: tuple[float | None, float | None]
    items_align: tuple[float, float]

    subgrid: bool
    grid_size: tuple[int | None, int | None]
    grid_cell: tuple[Span, Span]

    # drawio
    link: str | None
    label_formatter: Callable[['NodeProps', list[str]], str]

    drawio_style: BackendStyle


class NodeKeys(TypedDict, total=False):
    direction: int
    layout: 'Layout'
    scale: float
    size: tuple[float | None, float | None]
    padding: tuple[float, float, float, float]
    gap: tuple[float, float]
    virtual: bool
    align: tuple[float | None, float | None]
    items_align: tuple[float, float]

    subgrid: bool
    grid_size: tuple[int | None, int | None]
    grid_cell: tuple[Span, Span]

    # drawio
    link: str | None
    label_formatter: Callable[['NodeProps', list[str]], str]

    classes: ClassList
    drawio_style: BackendStyle | str


@dataclass(frozen=True, kw_only=True)
class EdgeProps:
    scale: float
    arc_size: float | None
    label_formatter: Callable[['EdgeProps', list[str]], str]
    label_offset: tuple[float, float]
    spacing: tuple[float | None, float | None]
    spacing_both: float | None
    jump_size: float | None

    drawio_style: BackendStyle


class EdgeKeys(TypedDict, total=False):
    scale: float
    arc_size: float | None
    label_formatter: Callable[['EdgeProps', list[str]], str]
    label_offset: tuple[float, float]
    spacing: tuple[float | None, float | None]
    spacing_both: float | None
    jump_size: float | None

    classes: ClassList
    drawio_style: BackendStyle | str
