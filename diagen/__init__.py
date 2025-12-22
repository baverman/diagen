from . import tags
from .nodes import EdgeFactory, NodeFactory

root = NodeFactory(tags.node)['root']
stack = root['dh virtual']
vstack = root['dv virtual']
grid = root['grid virtual']
node = root['w-24 h-12']
group = root['p-4 gap-24']

edge_root = EdgeFactory(tags.edge)['root']
edge = edge_root
