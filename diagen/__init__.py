from . import styles
from .nodes import EdgeFactory, NodeFactory

base_node = NodeFactory(styles.node)
stack = base_node['dh virtual']
vstack = base_node['dv virtual']
grid = base_node['grid virtual']
node = base_node['size-24/12']
group = base_node['p-4 gap-24']

base_edge = EdgeFactory(styles.edge)
edge = base_edge
