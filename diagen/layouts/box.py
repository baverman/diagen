from typing import TYPE_CHECKING

from ..utils import dtup2

if TYPE_CHECKING:
    from ..nodes import Node


class BoxLayout:
    @staticmethod
    def size(node: 'Node', axis: int) -> float:
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
    def arrange(node: 'Node') -> None:
        a = node.props.direction
        o = [1, 0][a]

        origin = node.origin
        oc = origin[o]
        c = origin[a] + node.props.padding[a]

        for it in node.children:
            align = it.align(node)
            it.position = dtup2(a, c, oc + (node.size[o] - it.size[o]) / 2 * (align[0] + 1))
            c += node.props.gap[a] + it.size[a]
