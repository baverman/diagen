from typing import TYPE_CHECKING, Callable, TypedDict

if TYPE_CHECKING:
    from .tags import Layout


class NodeProps(dict[str, object]):
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

    id: str
    style: dict[str, object]
    __getattr__ = dict.__getitem__


class NodeTagDefault(TypedDict):
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

    style: dict[str, object]


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

    id: str
    tag: str
    style: dict[str, object] | str | None


class EdgeProps(dict[str, object]):
    scale: float
    label_formatter: Callable[['EdgeProps', list[str]], str]
    label_offset: tuple[float, float]

    id: str
    style: dict[str, object]
    __getattr__ = dict.__getitem__


class EdgeTagDefault(TypedDict):
    scale: float
    label_formatter: Callable[['EdgeProps', list[str]], str]
    label_offset: tuple[float, float]

    style: dict[str, object]


class EdgeTag(TypedDict, total=False):
    scale: float
    label_formatter: Callable[['EdgeProps', list[str]], str]
    label_offset: tuple[float, float]

    id: str
    tag: str
    style: dict[str, object] | str | None
