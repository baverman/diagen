from . import styles
from .nodes import EdgeFactory, NodeFactory, isolate

__all__ = ['isolate']

base_node = NodeFactory(styles.node)
grid = base_node['virtual']
vgrid = base_node['virtual dv']
node = base_node['size-24/12']
group = base_node['p-4 gap-24']

base_edge = EdgeFactory(styles.edge)
edge = base_edge
