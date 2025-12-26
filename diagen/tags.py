from typing import TYPE_CHECKING, Literal, Protocol, TypeVar

from .layouts.box import BoxLayout
from .layouts.grid import GridLayout
from .tagmap import (
    AnyEdgeTag,
    AnyNodeTag,
    EdgeProps,
    EdgeTag,
    EdgeTagDefault,
    NodeProps,
    NodeRuleValue,
    NodeTag,
    NodeTagDefault,
    TagMap,
    rule,
)

if TYPE_CHECKING:
    from .nodes import Node


AlignLiteral = TypeVar('AlignLiteral', Literal['align'], Literal['items_align'])


class Layout(Protocol):
    def size(self, node: 'Node', axis: int) -> float: ...

    def arrange(self, node: 'Node') -> None: ...


def default_label_formatter(props: NodeProps | EdgeProps, label: list[str]) -> str:
    return '\n'.join(label)


def setScale(
    name: Literal['padding', 'size', 'gap'], scale_name: Literal['scale'], *pos: int
) -> NodeRuleValue:
    def inner(value: str, current: NodeTagDefault) -> NodeTag:
        v = float(value) * current[scale_name]
        if pos:
            result = list(current[name])
            for p in pos:
                result[p] = v
            return {name: tuple(result)}  # type: ignore[misc]
        else:
            return {name: v}  # type: ignore[misc]

    return inner


def setGridCol(name: Literal['grid_col']) -> NodeRuleValue:
    def inner(value: str, current: NodeTagDefault) -> NodeTag:
        if '/' in value:
            h, sep, t = value.partition('/')
            start = int(h)
            end = start + int(t)
        else:
            h, sep, t = value.partition(':')

            start = int(h)
            if sep:
                if t:
                    end = int(t)
                else:
                    end = 0
            else:
                end = start + 1

        return {name: (start, end)}

    return inner


def setAlign(name: AlignLiteral, pos: int) -> NodeRuleValue:
    def inner(value: str, current: NodeTagDefault) -> NodeTag:
        if value == 'start':
            v = -1.0
        elif value == 'center':
            v = 0.0
        elif value == 'end':
            v = 1.0
        else:
            v = float(value)

        if pos == 0:
            return {name: (v, current[name][1])}
        else:
            return {name: (current[name][0], v)}

    return inner


def setEdgeLabelOffset(value: str, current: EdgeTagDefault) -> EdgeTag:
    c = current['label_offset']
    h, _, t = value.partition('/')

    v0 = float(h) if h else c[0]
    v1 = (float(t) * current['scale']) if t else c[1]
    return {'label_offset': (v0, v1)}


node = TagMap[NodeProps, NodeTagDefault, AnyNodeTag]()

node.update(
    {
        'root': NodeTagDefault(
            direction=0,
            layout=BoxLayout,
            size=(-1, -1),
            padding=(0, 0, 0, 0),
            gap=(0, 0),
            scale=4.0,
            virtual=False,
            link=None,
            style={},
            label_formatter=default_label_formatter,
            items_align=(0, 0),
            align=(None, None),
            grid_columns=None,
            grid_col=None,
        ),
        'dh': {'direction': 0},
        'dv': {'direction': 1},
        'virtual': {'virtual': True},
        'non-virtual': {'virtual': False},
        'grid': {'layout': GridLayout},
    }
)

node.add_rules(
    [
        rule('p', setScale('padding', 'scale', 0, 1, 2, 3)),
        rule('px', setScale('padding', 'scale', 0, 2)),
        rule('py', setScale('padding', 'scale', 1, 3)),
        rule('pl', setScale('padding', 'scale', 0)),
        rule('pr', setScale('padding', 'scale', 2)),
        rule('pt', setScale('padding', 'scale', 1)),
        rule('pb', setScale('padding', 'scale', 3)),
        rule('size', setScale('size', 'scale', 0, 1)),
        rule('w', setScale('size', 'scale', 0)),
        rule('h', setScale('size', 'scale', 1)),
        rule('gap', setScale('gap', 'scale', 0, 1)),
        rule('gapx', setScale('gap', 'scale', 0)),
        rule('gapy', setScale('gap', 'scale', 1)),
        rule('grid', lambda value, _: {'layout': GridLayout, 'grid_columns': int(value)}),
        rule('col', setGridCol('grid_col')),
        rule('align', setAlign('align', 0)),
        rule('valign', setAlign('align', 1)),
        rule('items-align', setAlign('items_align', 0)),
        rule('items-valign', setAlign('items_align', 1)),
    ]
)


edge = TagMap[EdgeProps, EdgeTagDefault, AnyEdgeTag]()

edge.update(
    {
        'root': EdgeTagDefault(
            scale=4.0,
            style={},
            label_formatter=default_label_formatter,
            label_offset=(0, 0),
        )
    }
)

edge.add_rules([rule('label', setEdgeLabelOffset)])
