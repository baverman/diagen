from dataclasses import dataclass
from functools import cached_property
from typing import Any, Iterable, Protocol, Self, TypeVar, TypeVarTuple, Union

from .tags import Props, Tag, resolve_props

T = TypeVar('T')
Ts = TypeVarTuple('Ts')


def dtup2(direction: int, v1: float, v2: float) -> tuple[float, float]:
    if direction == 0:
        return v1, v2
    else:
        return v2, v1


class Layout(Protocol):
    def size(self, node: 'Node', axis: int) -> float: ...

    def arrange(self, node: 'Node') -> None: ...


class Node:
    children: list['Node']
    parent: Union['Node', None]

    def __init__(self, props: Props, *children: Union['Node', str]) -> None:
        self.parent = None
        self.props = props
        self.label = list(it for it in children if isinstance(it, str))
        self.children = list(it for it in children if isinstance(it, Node))
        self.position: tuple[float, float] = (0, 0)

        for it in self.children:
            it._added = True  # type: ignore[attr-defined]

        if _children_stack:
            _children_stack[-1].append(self)

    @property
    def layout(self) -> Layout:
        if self.props.layout == 'grid':
            return GridLayout
        else:
            return BoxLayout

    def __enter__(self) -> Self:
        _children_stack.append([])
        return self

    def __exit__(self, *args: Any) -> None:
        children = _children_stack.pop()
        self.children.extend(
            it for it in children if isinstance(it, Node) and not hasattr(it, '_added')
        )

    @cached_property
    def size(self) -> tuple[float, float]:
        return (
            self.layout.size(self, 0) if self.props.size[0] < 0 else self.props.size[0],
            self.layout.size(self, 1) if self.props.size[1] < 0 else self.props.size[1],
        )

    def arrange(self) -> None:
        if not self.children:
            return

        self.layout.arrange(self)
        for it in self.children:
            it.arrange()

    def walk(self) -> Iterable['Node']:
        parent = self.parent if self.props.virtual else self
        for it in self.children:
            it.parent = parent
            if not it.props.virtual:
                yield it
            yield from it.walk()

    def get_label(self) -> str:
        return self.props.label_formatter(self.props, self.label)


class NodeFactory:
    def __init__(self, props: tuple[Tag, ...] = ()):
        self.props = props
        self._cm_stack: list[Node] = []

    def __getitem__(self, tags: str) -> 'NodeFactory':
        return NodeFactory(self.props + ({'tag': tags},))

    def __call__(self, *args: Any) -> Node:
        props: Tag | None
        children: tuple[Node | str, ...]
        if not args:
            props = None
            children = ()
        elif isinstance(args[0], (Node, str)):
            props = None
            children = args
        else:
            props = args[0]
            children = args[1:]

        fprops = Props({} if props is None else props)
        resolve_props(fprops, *self.props)
        return Node(fprops, *children)

    def __enter__(self) -> Node:
        node = self()
        self._cm_stack.append(node)
        return node.__enter__()

    def __exit__(self, *args: Any) -> None:
        node = self._cm_stack.pop()
        return node.__exit__(*args)


class BoxLayout:
    @staticmethod
    def size(node: Node, axis: int) -> float:
        d = node.props.direction
        p = node.props.padding
        g = node.props.gap
        if d == axis:
            return (
                p[d]
                + p[d + 2]
                + g[d] * max(0, len(node.children) - 1)
                + sum(it.size[d] for it in node.children)
            )
        else:
            return p[axis] + p[axis + 2] + max(it.size[axis] for it in node.children)

    @staticmethod
    def arrange(node: Node) -> None:
        a = node.props.direction
        o = [1, 0][a]

        if node.props.virtual:
            c = node.position[a]
            oc = node.position[o]
        else:
            oc = c = 0

        c += node.props.padding[a]
        for it in node.children:
            align = it.props.self_align
            if align is None:
                align = node.props.align

            it.position = dtup2(a, c, oc + (node.size[o] - it.size[o]) / 2 * (align + 1))
            c += node.props.gap[a] + it.size[a]


@dataclass
class Cell:
    pos: tuple[int, int]
    size: tuple[int, int]
    node: Node


class GridLayout:
    @staticmethod
    def size(node: Node, axis: int) -> float:
        _, crow, ccol = GridLayout.cells(node)

        if axis == 0:
            dim = ccol[-1]
        else:
            dim = crow[-1]

        p = node.props.padding
        g = node.props.gap
        return dim + p[axis + 2] - g[axis]

    @staticmethod
    def cells(node: Node) -> tuple[list[Cell], list[float], list[float]]:
        try:
            return node._grid_cells  # type: ignore[no-any-return,attr-defined]
        except AttributeError:
            pass

        max_cols = node.props.grid_columns
        cells = []
        rows: dict[int, list[Cell]] = {}
        cols: dict[int, list[Cell]] = {}
        r = c = 0
        for it in node.children:
            cs, ce = it.props.grid_col if it.props.grid_col else (c + 1, c + 2)
            if ce <= 0:
                ce = (max_cols or 0) + 1 + ce
            ce = max(cs + 1, min(ce, (max_cols or 0) + 1))
            if ce <= (c + 1):
                r += 1

            cell = Cell((cs - 1, r), (ce - cs, 1), it)
            cells.append(cell)
            for cc in range(cell.size[0]):
                cols.setdefault(c + cc, []).append(cell)
            for rr in range(cell.size[1]):
                rows.setdefault(r + rr, []).append(cell)

            c = ce - 1
            if max_cols is not None and c >= max_cols:
                c = 0
                r += 1

        col_count = max(it.pos[0] + it.size[0] for it in cells)
        row_count = max(it.pos[1] + it.size[1] for it in cells)
        row_heights = [
            max((it.node.size[1] / it.size[1] for it in rows.get(i, [])), default=0)
            for i in range(row_count)
        ]
        col_widths = [
            max((it.node.size[0] / it.size[0] for it in cols.get(j, [])), default=0)
            for j in range(col_count)
        ]

        p = node.props.padding

        g = node.props.gap
        crow = [p[1]]
        for h in row_heights:
            crow.append(crow[-1] + h + g[1])

        ccol = [p[0]]
        for w in col_widths:
            ccol.append(ccol[-1] + w + g[0])

        result = cells, crow, ccol
        node._grid_cells = result  # type: ignore[attr-defined]
        return result

    @staticmethod
    def arrange(node: Node) -> None:
        cells, crow, ccol = GridLayout.cells(node)
        c = node.position if node.props.virtual else (0, 0)
        g = node.props.gap

        for it in cells:
            s = ccol[it.pos[0]], crow[it.pos[1]]
            bw = ccol[it.pos[0] + it.size[0]] - s[0] - g[0]
            bh = crow[it.pos[1] + it.size[1]] - s[1] - g[1]
            pos = (
                c[0] + s[0] + (bw - it.node.size[0]) / 2,
                c[1] + s[1] + (bh - it.node.size[1]) / 2,
            )
            it.node.position = pos


_children_stack: list[list[Node]] = []

root = NodeFactory()['root']
stack = root['dh virtual']
vstack = root['dv virtual']
node = root['w-24 h-12']
group = root['p-4 gap-24']
