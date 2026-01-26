from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, Iterator, Mapping, Optional

if TYPE_CHECKING:
    from ..nodes import Node
    from ..stylemap import NodeProps

NodeMap = Mapping['Node', 'LayoutNode']


@dataclass
class LayoutNode:
    parent: Optional['LayoutNode']
    node: 'Node'
    props: 'NodeProps'
    children: list['LayoutNode']
    position: tuple[float, float] = (0, 0)

    @cached_property
    def size(self) -> tuple[float, float]:
        return self.props.layout.size(self)

    @cached_property
    def real_parent(self) -> 'LayoutNode':
        result = self.parent
        if result:
            if result.props.virtual:
                return result.real_parent
            return result
        raise RuntimeError('Node tree has no common non-virtual parent')  # pragma: no cover


def _make_layout_tree(parent: LayoutNode | None, node: 'Node') -> LayoutNode:
    children: list[LayoutNode]
    result = LayoutNode(parent, node, node.props, children := [])
    children.extend(_make_layout_tree(result, it) for it in node.children)
    return result


def _arrange(node: LayoutNode) -> None:
    if not node.children:
        return

    node.props.layout.arrange(node)
    for it in node.children:
        _arrange(it)


def arrange(node: 'Node') -> LayoutNode:
    root = _make_layout_tree(None, node)
    _arrange(root)
    return root


def walk(node: LayoutNode) -> Iterator[LayoutNode]:
    for it in node.children:
        yield it
        yield from walk(it)


def node_map(node: LayoutNode) -> NodeMap:
    result = {it.node: it for it in walk(node)}
    result[node.node] = node
    return result
