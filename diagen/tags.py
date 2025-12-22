from typing import TYPE_CHECKING, Protocol

from .layouts.box import BoxLayout
from .layouts.grid import GridLayout
from .tagmap import (
    AnyEdgeTag,
    AnyNodeTag,
    EdgeProps,
    EdgeTagDefault,
    NodeProps,
    NodeTagDefault,
    RawTag,
    RuleValue,
    TagMap,
    rule,
)

if TYPE_CHECKING:
    from .nodes import Node


class Layout(Protocol):
    def size(self, node: 'Node', axis: int) -> float: ...

    def arrange(self, node: 'Node') -> None: ...


def default_label_formatter(props: NodeProps | EdgeProps, label: list[str]) -> str:
    return '\n'.join(label)


def setScale(name: str, scale_name: str, *pos: int) -> RuleValue:
    def inner(value: str, current: RawTag) -> RawTag:
        v = float(value) * current[scale_name]  # type: ignore[operator]
        if pos:
            result = list(current[name])  # type: ignore[call-overload]
            for p in pos:
                result[p] = v
            return {name: tuple(result)}
        else:
            return {name: v}

    return inner


def setGrid(name: str) -> RuleValue:
    def inner(value: str, current: RawTag) -> RawTag:
        h, sep, t = value.partition(':')
        start = int(h)
        if sep:
            if t:
                pt = int(t)
                if pt > 0:
                    end = start + pt
                else:
                    end = pt
            else:
                end = 0
        else:
            end = start + 1

        return {f'grid_{name}': (start, end)}

    return inner


def setAlign(name: str, pos: int) -> RuleValue:
    def inner(value: str, current: RawTag) -> RawTag:
        if value == 'start':
            v = -1.0
        elif value == 'center':
            v = 0.0
        elif value == 'end':
            v = 1.0
        else:
            v = float(value)

        if pos == 0:
            return {name: (v, current[name][1])}  # type: ignore[index]
        else:
            return {name: (current[name][0], v)}  # type: ignore[index]

    return inner


node = TagMap[NodeProps, AnyNodeTag]()

node.update(
    {
        'root': NodeTagDefault(
            direction=0,
            layout=BoxLayout,
            size=(-1, -1),
            padding=(0, 0, 0, 0),
            gap=(0, 0),
            scale=4,
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
        rule('col', setGrid('col')),
        rule('align', setAlign('align', 0)),
        rule('valign', setAlign('align', 1)),
        rule('items-align', setAlign('items_align', 0)),
        rule('items-valign', setAlign('items_align', 1)),
    ]
)


edge = TagMap[EdgeProps, AnyEdgeTag]()

edge.update(
    {
        'root': EdgeTagDefault(
            scale=1.0,
            style={},
            label_formatter=default_label_formatter,
        )
    }
)
