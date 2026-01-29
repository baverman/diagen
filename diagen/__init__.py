from typing import Collection

from . import styles
from .nodes import EdgeFactory, Node, NodeFactory, node_context

__all__ = ['node_context', 'wrap']

base_node = NodeFactory(styles.node)
grid = base_node['virtual']
vgrid = base_node['virtual dv']
node = base_node['size-24/12']
group = base_node['p-4 gap-24']

base_edge = EdgeFactory(styles.edge)
edge = base_edge


def wrap(nodes: Collection[Node], classes: str | None = None) -> Node:
    if classes:
        f = base_node[classes]
    else:
        f = base_node

    with node_context():
        return f(*nodes)
