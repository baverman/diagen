from typing import Iterable, Literal, TypeVar, overload

from .layouts.box import BoxLayout
from .layouts.grid import GridLayout
from .stylemap import (
    BackendStyle,
    EdgeKeys,
    EdgeProps,
    EdgeRuleValue,
    NodeKeys,
    NodeProps,
    NodeRuleValue,
    StyleMap,
    rule,
)
from .utils import kebab_case, mux2

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


@overload
def setDashed(value: str, current: EdgeProps) -> EdgeKeys: ...


@overload
def setDashed(value: str, current: NodeProps) -> NodeKeys: ...


def setDashed(value: str, current: NodeProps | EdgeProps) -> NodeKeys | EdgeKeys:
    h, sep, t = value.partition('-')
    if not sep:
        t = h
    return {'drawio_style': {'dashed': 1, 'dashPattern': f'{h} {t}'}}


def setShadow(value: str, current: EdgeProps) -> EdgeKeys:
    h, _, t = value.partition('/')

    style: BackendStyle = {
        'shadow': 1,
        'shadowBlur': h,
    }

    if t:
        style['shadowOpacity'] = t

    return {'drawio_style': style}


def setEdgeEndFill(prefix: str) -> EdgeRuleValue:
    def setter(value: str, current: EdgeProps) -> EdgeKeys:
        return {'drawio_style': {prefix + 'Fill': 1, prefix + 'FillColor': value}}

    return setter


def setEdgeEndSize(prefix: str) -> EdgeRuleValue:
    def setter(value: str, current: EdgeProps) -> EdgeKeys:
        return {'drawio_style': {prefix + 'Size': value}}

    return setter


def setEdgeArrowShape(prefix: str, name: str) -> EdgeRuleValue:
    def setter(value: str, current: EdgeProps) -> EdgeKeys:
        return {'drawio_style': {prefix + 'Size': value, prefix + 'Arrow': name}}

    return setter


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
        # Dash style
        'dashed': {'drawio_style': {'dashed': 1}},
        'solid': {'drawio_style': {'dashed': 0}},
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
        rule('dashed', setDashed),
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

EDGE_CURVE_TYPES = ['rounded', 'curved']
EDGE_MODES = ['comic', 'sketch']
ARROW_TYPES = [
    'none',
    'classic',
    'classicThin',
    'block',
    'blockThin',
    'open',
    'openThin',
    'oval',
    'diamond',
    'diamondThin',
    'async',
    'openAsync',
    'halfCircle',
    'dash',
    'cross',
    'circlePlus',
    'circle',
    'baseDash',
    'ERone',
    'ERmandOne',
    'ERmany',
    'ERoneToMany',
    'ERzeroToOne',
    'ERzeroToMany',
    'doubleBlock',
]


def cstyle(conflict_keys: list[str], **style: int | str) -> BackendStyle:
    style['@pop'] = conflict_keys  # type: ignore[assignment]
    return style  # type: ignore[return-value]


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
        'rounded': {'drawio_style': cstyle(EDGE_CURVE_TYPES, rounded=1)},
        'curved': {'drawio_style': cstyle(EDGE_CURVE_TYPES, curved=1)},
        'sharp': {'drawio_style': cstyle(EDGE_CURVE_TYPES, rounded=0)},
        # Edge modes
        'comic': {'drawio_style': cstyle(EDGE_MODES, comic=1)},
        'sketch': {'drawio_style': cstyle(EDGE_MODES, sketch=1)},
        'plain': {'drawio_style': cstyle(EDGE_MODES)},
        # Dash style
        'dashed': {'drawio_style': {'dashed': 1}},
        'solid': {'drawio_style': {'dashed': 0}},
        # Shadow
        'shadow': {'drawio_style': {'shadow': 1}},
        'shadow-none': {'drawio_style': {'shadow': 0}},
        # Shapes
        'shape-link': {'drawio_style': {'shape': 'link'}},
        'shape-flex-arrow': {'drawio_style': {'shape': 'flexArrow'}},
        'shape-arrow': {'drawio_style': {'shape': 'arrow'}},
        'shape-filled': {'drawio_style': {'shape': 'filledEdge'}},
        'shape-pipe': {'drawio_style': {'shape': 'pipe'}},
        'shape-wire': {'drawio_style': {'shape': 'wire', 'fillColor': 'default', 'dashed': 1}},
    }
)

edge.add_rules(
    [
        rule('label', setEdgeLabelOffset),
        rule(
            'rounded',
            lambda value, current: {
                'drawio_style': cstyle(
                    EDGE_CURVE_TYPES, rounded=1, arcSize=int(current.scale * float(value))
                )
            },
        ),
        rule(
            'comic',
            lambda value, current: {'drawio_style': cstyle(EDGE_MODES, comic=1, jiggle=int(value))},
        ),
        rule(
            'sketch',
            lambda value, current: {
                'drawio_style': cstyle(EDGE_MODES, sketch=1, jiggle=int(value))
            },
        ),
        rule('w', lambda value, current: {'drawio_style': {'strokeWidth': float(value)}}),
        rule('color', lambda value, current: {'drawio_style': {'strokeColor': value}}),
        rule('dashed', setDashed),
        rule('shadow', setShadow),
    ]
)


def addArrowStyles(arrows: Iterable[str]) -> None:
    classes: dict[str, EdgeKeys] = {}
    rules = []

    for class_prefix, style_prefix in ('start-', 'start'), ('end-', 'end'):
        for name in arrows:
            kc_name = kebab_case(name)
            classes[class_prefix + kc_name] = {'drawio_style': {style_prefix + 'Arrow': name}}
            rules.append(rule(class_prefix + kc_name, setEdgeArrowShape(style_prefix, name)))

        classes[class_prefix + 'fill'] = {'drawio_style': {style_prefix + 'Fill': 1}}
        classes[class_prefix + 'fill-none'] = {'drawio_style': {style_prefix + 'Fill': 0}}
        rules.append(rule(class_prefix + 'fill', setEdgeEndFill(style_prefix)))
        rules.append(rule(class_prefix + 'size', setEdgeEndSize(style_prefix)))

    edge.update(classes)
    edge.add_rules(rules)


addArrowStyles(ARROW_TYPES)
