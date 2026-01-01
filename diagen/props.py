from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Protocol, TypedDict

if TYPE_CHECKING:
    from .nodes import Node


BackendStyle = dict[str, int | float | str | list[str]]


class Layout(Protocol):
    def size(self, node: 'Node', axis: int) -> float: ...

    def arrange(self, node: 'Node') -> None: ...


@dataclass
class NodeProps:
    direction: int
    layout: 'Layout'
    scale: float
    size: tuple[float, float]
    padding: tuple[float, float, float, float]
    gap: tuple[float, float]
    virtual: bool
    align: tuple[float | None, float | None]
    items_align: tuple[float, float]

    grid_columns: int | None
    grid_col: tuple[int, int] | None

    # drawio
    link: str | None
    label_formatter: Callable[['NodeProps', list[str]], str]

    drawio_style: BackendStyle


class NodeKeys(TypedDict, total=False):
    direction: int
    layout: 'Layout'
    scale: float
    size: tuple[float, float]
    padding: tuple[float, float, float, float]
    gap: tuple[float, float]
    virtual: bool
    align: tuple[float | None, float | None]
    items_align: tuple[float, float]

    grid_columns: int | None
    grid_col: tuple[int, int] | None

    # drawio
    link: str | None
    label_formatter: Callable[['NodeProps', list[str]], str]

    classes: str
    drawio_style: BackendStyle | str


@dataclass
class EdgeProps:
    scale: float
    label_formatter: Callable[['EdgeProps', list[str]], str]
    label_offset: tuple[float, float]

    drawio_style: BackendStyle


class EdgeKeys(TypedDict, total=False):
    scale: float
    label_formatter: Callable[['EdgeProps', list[str]], str]
    label_offset: tuple[float, float]

    classes: str
    drawio_style: BackendStyle | str
