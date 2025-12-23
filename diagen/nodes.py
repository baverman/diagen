from dataclasses import dataclass
from functools import cached_property
from typing import Any, Iterable, Self, Union

from .props import EdgeProps, EdgeTag, NodeProps, NodeTag
from .tagmap import AnyEdgeTag, AnyNodeTag, TagMap

_children_stack: list[list['Node']] = []


class Node:
    children: list['Node']
    parent: Union['Node', None]
    edges: list['Edge']

    def __init__(self, props: NodeProps, *children: Union['Node', str]) -> None:
        self.parent = None
        self.props = props
        self.label = list(it for it in children if isinstance(it, str))
        self.children = list(it for it in children if isinstance(it, Node))
        self.position: tuple[float, float] = (0, 0)
        self.edges = []

        self._added = False

        for it in self.children:
            it._added = True

        if _children_stack:
            _children_stack[-1].append(self)

    @property
    def origin(self) -> tuple[float, float]:
        if self.props.virtual:
            return self.position
        else:
            return (0, 0)

    def align(self, parent: 'Node') -> tuple[float, float]:
        a0, a1 = self.props.align
        if a0 is None:
            a0 = parent.props.items_align[0]
        if a1 is None:
            a1 = parent.props.items_align[1]
        return a0, a1

    def __enter__(self) -> Self:
        _children_stack.append([])
        return self

    def __exit__(self, *args: Any) -> None:
        children = _children_stack.pop()
        self.children.extend(it for it in children if isinstance(it, Node) and not it._added)

    @cached_property
    def size(self) -> tuple[float, float]:
        return (
            self.props.layout.size(self, 0) if self.props.size[0] < 0 else self.props.size[0],
            self.props.layout.size(self, 1) if self.props.size[1] < 0 else self.props.size[1],
        )

    def arrange(self) -> None:
        if not self.children:
            return

        self.props.layout.arrange(self)
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

    def __repr__(self) -> str:
        return f'Node(size={self.size})'

    @property
    def l(self) -> 'Port':
        return Port(self, side=0)

    @property
    def t(self) -> 'Port':
        return Port(self, side=1)

    @property
    def r(self) -> 'Port':
        return Port(self, side=2)

    @property
    def b(self) -> 'Port':
        return Port(self, side=3)

    @property
    def node_ref(self) -> 'Node':
        return self

    @cached_property
    def edge_order(self) -> list[dict['Edge', int]]:
        result: list[dict['Edge', int]] = [{}, {}, {}, {}]
        counter = [0, 0, 0, 0]
        for it in self.edges:
            for port in it.node_ports(self):
                c = counter[port.side]
                counter[port.side] += 1
                result[port.side][it] = c
        return result


@dataclass
class Port:
    node: Node
    side: int

    @property
    def node_ref(self) -> Node:
        return self.node

    @property
    def parent(self) -> Node | None:
        return self.node.parent

    @property
    def props(self) -> NodeProps:
        return self.node.props


AnyEdgePort = Node | Port


class Edge:
    def __init__(
        self, props: EdgeProps, source: AnyEdgePort, target: AnyEdgePort, *label: str
    ) -> None:
        self.props = props
        self.source = source
        self.target = target
        self.label = list(label)

        source.node_ref.edges.append(self)
        target.node_ref.edges.append(self)

    def get_label(self) -> str:
        return self.props.label_formatter(self.props, self.label)

    def node_ports(self, node: Node) -> Iterable[Port]:
        for it in (self.source, self.target):
            if isinstance(it, Port) and it.node_ref is node:
                yield it


class NodeFactory:
    def __init__(self, tagmap: TagMap[NodeProps, AnyNodeTag], props: tuple[NodeTag, ...] = ()):
        self.props = props
        self.tagmap = tagmap
        self._cm_stack: list[Node] = []

    def __getitem__(self, tags: str) -> 'NodeFactory':
        return NodeFactory(self.tagmap, self.props + ({'tag': tags},))

    def __call__(self, *args: Any) -> Node:
        props: NodeTag | None
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

        fprops = NodeProps({} if props is None else props)
        self.tagmap.resolve_props(fprops, *self.props)
        return Node(fprops, *children)

    def __enter__(self) -> Node:
        node = self()
        self._cm_stack.append(node)
        return node.__enter__()

    def __exit__(self, *args: Any) -> None:
        node = self._cm_stack.pop()
        return node.__exit__(*args)


class EdgeFactory:
    def __init__(self, tagmap: TagMap[EdgeProps, AnyEdgeTag], props: tuple[EdgeTag, ...] = ()):
        self.tagmap = tagmap
        self.props = props

    def __getitem__(self, tags: str) -> 'EdgeFactory':
        return EdgeFactory(self.tagmap, self.props + ({'tag': tags},))

    def __call__(self, *args: Any) -> Edge:
        props: EdgeTag | None
        rest: tuple[Any, ...]
        if not args:
            props = None
            rest = ()
        elif isinstance(args[0], dict):
            props = args[0]  # type: ignore[assignment]
            rest = args[1:]
        else:
            props = None
            rest = args

        fprops = EdgeProps({} if props is None else props)
        self.tagmap.resolve_props(fprops, *self.props)
        return Edge(fprops, *rest)
