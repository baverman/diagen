from contextlib import contextmanager
from contextvars import ContextVar, Token
from dataclasses import dataclass, replace
from functools import cached_property
from typing import Any, Collection, Generic, Iterable, Iterator, Self, Union, Unpack

from .stylemap import (
    ClassList,
    EdgeKeys,
    EdgeProps,
    EdgeStyleMap,
    KeysT,
    NodeKeys,
    NodeProps,
    NodeStyleMap,
    PropsT,
    StyleMap,
)

_children_stack = ContextVar[list['Node']]('_children_stack')

AnyNode = Union['Node', str]


class Node:
    children: list['Node']
    edges: list['Edge']
    _cs_token: list[Token[list['Node']]]

    def __init__(
        self, props: NodeProps, children: Collection[AnyNode], stylemap: NodeStyleMap
    ) -> None:
        self.id = ''
        self.props = stylemap.eval_props(props)
        self.label = list(it for it in children if isinstance(it, str))
        self.children = list(it for it in children if isinstance(it, Node))
        self.stylemap = stylemap
        self.edges = []

        self._added = False
        self._cs_token = []

        for it in self.children:
            it._added = True

        if (cs := _children_stack.get(None)) is not None:
            cs.append(self)

    def align(self, parent_align: tuple[float, float]) -> tuple[float, float]:
        a0, a1 = self.props.align
        if a0 is None:
            a0 = parent_align[0]
        if a1 is None:
            a1 = parent_align[1]
        return a0, a1

    def __enter__(self) -> Self:
        self._cs_token.append(_children_stack.set([]))
        return self

    def __exit__(self, *args: Any) -> None:
        children = _children_stack.get()
        _children_stack.reset(self._cs_token.pop())
        for it in children:
            if isinstance(it, Node) and not it._added:
                it._added = True
                self.children.append(it)

    def get_label(self) -> str:
        return self.props.label_formatter(self.props, self.label)

    def __repr__(self) -> str:
        return f'Node#{id(self):X}(size={self.props.size}, label={self.label})'

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
    def edge_positions(self) -> list[dict['Edge', float]]:
        result: list[dict['Edge', float]] = [{}, {}, {}, {}]

        count = [0, 0, 0, 0]
        maxidx1 = [0, 0, 0, 0]
        reserved: list[set[int]] = [set(), set(), set(), set()]
        for it in self.edges:
            for port in it.node_ports(self):
                s = port.side
                count[s] += 1
                if port.index is not None:
                    reserved[s].add(port.index)
                    maxidx1[s] = max(maxidx1[s], port.index + 1)

        counter = [0, 0, 0, 0]
        for it in self.edges:
            for port in it.node_ports(self):
                s = port.side
                if port.position is not None:
                    result[s][it] = port.position
                else:
                    if port.index is None:
                        c = counter[s]
                        while c in reserved[s]:
                            c += 1
                        counter[s] = c + 1
                    else:
                        c = port.index
                    result[s][it] = (c + 1) / (max(count[s], maxidx1[s]) + 1)
        return result


@dataclass
class Port:
    node: Node
    side: int
    position: float | None = None
    index: int | None = None
    classes: list[str] | None = None

    @property
    def node_ref(self) -> Node:
        return self.node

    def __getitem__(self, pos: int | float | ClassList) -> 'Port':
        if isinstance(pos, int):
            return replace(self, index=pos)
        elif isinstance(pos, float):
            return replace(self, position=pos)

        clist = (self.classes or []).copy()
        if isinstance(pos, str):
            pos = [it.strip() for it in pos.split()]
        clist.extend(pos)
        return replace(self, classes=clist)


AnyEdgePort = Node | Port


class Edge:
    def __init__(
        self,
        props: EdgeProps,
        source: AnyEdgePort,
        target: AnyEdgePort,
        label: Collection[str],
        stylemap: EdgeStyleMap,
    ) -> None:
        self.id = ''
        self.props = props
        self.source = source
        self.target = target
        self.label = list(label)
        self.stylemap = stylemap

        source.node_ref.edges.append(self)
        self._apply_port_styles(source, 'start-')

        target.node_ref.edges.append(self)
        self._apply_port_styles(target, 'end-')

        self.props = stylemap.eval_props(self.props)

    def _apply_port_styles(self, port: AnyEdgePort, prefix: str) -> None:
        if isinstance(port, Port):
            if port.classes:
                self.props = self.stylemap.resolve_classes(
                    [prefix + it for it in port.classes], self.props
                )

    def get_label(self) -> str:
        return self.props.label_formatter(self.props, self.label)

    def node_ports(self, node: Node) -> Iterable[Port]:
        for it in (self.source, self.target):
            if isinstance(it, Port) and it.node_ref is node:
                yield it


class BaseFactory(Generic[PropsT, KeysT]):
    stylemap: StyleMap[PropsT, KeysT]
    factory_props: PropsT

    def __init__(self, stylemap: StyleMap[PropsT, KeysT], props: PropsT | None = None):
        self.factory_props = props if props is not None else stylemap.default_props()
        self.stylemap = stylemap

    def __getitem__(self, classes: ClassList) -> Self:
        nprops = self.stylemap.resolve_classes(classes, self.factory_props)
        return type(self)(self.stylemap, nprops)

    def _make_props(self, props: KeysT | None) -> PropsT:
        if props is not None:
            return self.stylemap.resolve_props((props,), self.factory_props)
        return self.factory_props

    def _add_props(self, props: KeysT) -> Self:
        return type(self)(self.stylemap, self._make_props(props))


class NodeFactory(BaseFactory[NodeProps, NodeKeys]):
    def __init__(self, stylemap: NodeStyleMap, props: NodeProps | None = None):
        super().__init__(stylemap, props)
        self._cm_stack: list[Node] = []

    def __call__(self, *rest: AnyNode, props: NodeKeys | None = None) -> Node:
        return Node(self._make_props(props), rest, self.stylemap)

    def __enter__(self) -> Node:
        node = self()
        self._cm_stack.append(node)
        return node.__enter__()

    def __exit__(self, *args: Any) -> None:
        node = self._cm_stack.pop()
        return node.__exit__(*args)

    def props(self, **kwargs: Unpack[NodeKeys]) -> Self:
        return self._add_props(kwargs)


class EdgeFactory(BaseFactory[EdgeProps, EdgeKeys]):
    def __call__(
        self, source: AnyEdgePort, target: AnyEdgePort, /, *rest: str, props: EdgeKeys | None = None
    ) -> Edge:
        return Edge(self._make_props(props), source, target, rest, self.stylemap)

    def props(self, **kwargs: Unpack[EdgeKeys]) -> Self:
        return self._add_props(kwargs)


@contextmanager
def isolate() -> Iterator[None]:
    token = _children_stack.set([])
    try:
        yield
    finally:
        _children_stack.reset(token)
