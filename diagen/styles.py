from typing import Literal, TypeVar

from .layouts.box import BoxLayout
from .layouts.grid import GridLayout
from .stylemap import (
    BackendStyle,
    EdgeKeys,
    EdgeProps,
    NodeKeys,
    NodeProps,
    NodeRuleValue,
    StyleMap,
    rule,
)
from .utils import mux2

AlignLiteral = TypeVar('AlignLiteral', Literal['align'], Literal['items_align'])


def default_label_formatter(props: NodeProps | EdgeProps, label: list[str]) -> str:
    return '\n'.join(label)


def setScale(
    name: Literal['padding', 'size', 'gap'], scale_name: Literal['scale'], *pos: int
) -> NodeRuleValue:
    def inner(value: str, current: NodeProps) -> NodeKeys:
        dyn: NodeKeys = vars(current)  # type: ignore[assignment]
        v = float(value) * dyn[scale_name]
        if pos:
            result = list(dyn[name])
            for p in pos:
                result[p] = v
            return {name: tuple(result)}  # type: ignore[misc]
        else:
            return {name: v}  # type: ignore[misc]

    return inner


def setGridCol(name: Literal['grid_col']) -> NodeRuleValue:
    def inner(value: str, current: NodeProps) -> NodeKeys:
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
    def inner(value: str, current: NodeProps) -> NodeKeys:
        dyn: NodeKeys = vars(current)  # type: ignore[assignment]
        if value == 'start':
            v = -1.0
        elif value == 'center':
            v = 0.0
        elif value == 'end':
            v = 1.0
        else:
            v = float(value)

        return {name: mux2(pos, v, dyn[name])}

    return inner


def setEdgeLabelOffset(value: str, current: EdgeProps) -> EdgeKeys:
    c = current.label_offset
    h, _, t = value.partition('/')

    v0 = float(h) if h else c[0]
    v1 = (float(t) * current.scale) if t else c[1]
    return {'label_offset': (v0, v1)}


node = StyleMap[NodeProps, NodeKeys](
    NodeProps(
        direction=0,
        layout=BoxLayout,
        size=(-1, -1),
        padding=(0, 0, 0, 0),
        gap=(0, 0),
        scale=4.0,
        virtual=False,
        link=None,
        drawio_style={},
        label_formatter=default_label_formatter,
        items_align=(0, 0),
        align=(None, None),
        grid_columns=None,
        grid_col=None,
    )
)

node.update(
    {
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


edge = StyleMap[EdgeProps, EdgeKeys](
    EdgeProps(
        scale=4.0,
        drawio_style={},
        label_formatter=default_label_formatter,
        label_offset=(0, 0),
    )
)

EDGE_CURVE_TYPES = {'rounded', 'curved'}


def conflictStyle(name: str, value: int | str, cnames: set[str]) -> BackendStyle:
    return {name: value, '@pop': list(cnames - {name})}


edge.update(
    {
        # Edge styles
        'edge-style-none': {'drawio_style': {'@pop': ['edgeStyle']}},
        'elbow': {'drawio_style': 'edgeStyle=elbowEdgeStyle'},
        'elbow-v': {'drawio_style': 'edgeStyle=elbowEdgeStyle;elbow=vertical'},
        'elbow-h': {'drawio_style': 'edgeStyle=elbowEdgeStyle;elbow=horizontal'},
        'entity-rel': {'drawio_style': 'edgeStyle=entityRelationEdgeStyle'},
        'ortho': {'drawio_style': 'edgeStyle=orthogonalEdgeStyle'},
        # Edge curve types
        'rounded': {'drawio_style': conflictStyle('rounded', 1, EDGE_CURVE_TYPES)},
        'curved': {'drawio_style': conflictStyle('curved', 1, EDGE_CURVE_TYPES)},
        'sharp': {'drawio_style': conflictStyle('rounded', 0, EDGE_CURVE_TYPES)},
    }
)

edge.add_rules(
    [
        rule('label', setEdgeLabelOffset),
        rule(
            'rounded',
            lambda value, current: {
                'drawio_style': {
                    **conflictStyle('rounded', 1, EDGE_CURVE_TYPES),
                    'arcSize': current.scale * float(value),
                }
            },
        ),
    ]
)
