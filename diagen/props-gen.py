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
    style: dict[str, object] | str | None
    label_formatter: Callable[['Props', list[str]], str]
""".rstrip()

BODY = f"""\
from typing import TYPE_CHECKING, Callable, TypedDict

if TYPE_CHECKING:
    from .tags import Layout


class Props(dict[str, object]):
{NODE_PROPS}

    id: str
    __getattr__ = dict.__getitem__


class TagTotal(TypedDict):
{NODE_PROPS}


class Tag(TypedDict, total=False):
{NODE_PROPS}

    id: str
    tag: str
"""

if __name__ == '__main__':
    import os.path

    with open(os.path.join(os.path.dirname(__file__), 'props.py'), 'w') as f:
        f.write(BODY)
