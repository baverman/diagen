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
    label_formatter: Callable[['EdgeProps', list[str]], str]
    label_offset: tuple[float, float]
""".rstrip()

BODY = f"""\
from typing import TYPE_CHECKING, Callable, TypedDict

if TYPE_CHECKING:
    from .tags import Layout


class NodeProps(dict[str, object]):
{NODE_PROPS}

    id: str
    style: dict[str, object]
    __getattr__ = dict.__getitem__


class NodeTagDefault(TypedDict):
{NODE_PROPS}

    style: dict[str, object]


class NodeTag(TypedDict, total=False):
{NODE_PROPS}

    id: str
    tag: str
    style: dict[str, object] | str | None


class EdgeProps(dict[str, object]):
{EDGE_PROPS}

    id: str
    style: dict[str, object]
    __getattr__ = dict.__getitem__


class EdgeTagDefault(TypedDict):
{EDGE_PROPS}

    style: dict[str, object]


class EdgeTag(TypedDict, total=False):
{EDGE_PROPS}

    id: str
    tag: str
    style: dict[str, object] | str | None
"""

if __name__ == '__main__':
    import os.path

    with open(os.path.join(os.path.dirname(__file__), 'props.py'), 'w') as f:
        f.write(BODY)
