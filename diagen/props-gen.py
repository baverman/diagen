NODE_PROPS = """\
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
""".rstrip()


EDGE_PROPS = """\
    scale: float
    arc_size: float | None
    label_formatter: Callable[['EdgeProps', list[str]], str]
    label_offset: tuple[float, float]
    spacing: tuple[float | None, float | None]
    spacing_both: float | None
""".rstrip()

BODY = f"""\
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Protocol, TypedDict

if TYPE_CHECKING:
    from .nodes import Node


BackendStyle = dict[str, int | float | str | list[str]]
ClassList = str | list[str]


class Layout(Protocol):
    def size(self, node: 'Node', axis: int) -> float: ...

    def arrange(self, node: 'Node') -> None: ...


@dataclass(frozen=True, kw_only=True)
class NodeProps:
{NODE_PROPS}

    drawio_style: BackendStyle


class NodeKeys(TypedDict, total=False):
{NODE_PROPS}

    classes: ClassList
    drawio_style: BackendStyle | str


@dataclass(frozen=True, kw_only=True)
class EdgeProps:
{EDGE_PROPS}

    drawio_style: BackendStyle


class EdgeKeys(TypedDict, total=False):
{EDGE_PROPS}

    classes: ClassList
    drawio_style: BackendStyle | str
"""

if __name__ == '__main__':
    import os.path

    with open(os.path.join(os.path.dirname(__file__), 'props.py'), 'w') as f:
        f.write(BODY)
