from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Protocol, TypedDict

if TYPE_CHECKING:
    from .nodes import Node


Style = dict[str, int | float | str]


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

    style: Style


class NodeTag(TypedDict, total=False):
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

    tag: str
    style: Style | str


@dataclass
class EdgeProps:
    scale: float
    label_formatter: Callable[['EdgeProps', list[str]], str]
    label_offset: tuple[float, float]
    port_position: tuple[float | None, float | None]

    style: Style


class EdgeTag(TypedDict, total=False):
    scale: float
    label_formatter: Callable[['EdgeProps', list[str]], str]
    label_offset: tuple[float, float]
    port_position: tuple[float | None, float | None]

    tag: str
    style: Style | str
