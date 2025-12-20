import functools
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Mapping, Protocol

from .layouts.box import BoxLayout
from .layouts.grid import GridLayout
from .props import Props, Tag, TagTotal

if TYPE_CHECKING:
    from .nodes import Node

RawTag = Mapping[str, object]


class Layout(Protocol):
    def size(self, node: 'Node', axis: int) -> float: ...

    def arrange(self, node: 'Node') -> None: ...


_smap_cache: dict[str, dict[str, object]] = {}


def get_style(style: str | dict[str, object] | None) -> dict[str, object]:
    if style is None:
        return {}

    if isinstance(style, dict):
        return style

    style = style or ''

    try:
        return _smap_cache[style]
    except KeyError:
        pass

    result = _smap_cache[style] = {
        k: v for it in style.split(';') if it for k, _, v in (it.partition('='),)
    }

    return result


def default_label_formatter(props: Props, label: list[str]) -> str:
    return '\n'.join(label)


RuleValue = Callable[[str, RawTag], RawTag]


@dataclass
class rule:
    prefix: str
    fn: RuleValue
    has_value: bool = True


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


rules = [
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


@functools.cache
def rule_re() -> re.Pattern[str]:
    vparts = [it.prefix for it in rules if it.has_value]
    return re.compile(rf'({"|".join(vparts)})-(.+)')


@functools.cache
def rule_map() -> dict[str, rule]:
    return {it.prefix: it for it in rules}


@functools.cache
def rule_fn_value(tag: str) -> tuple[RuleValue, str] | None:
    m = rule_re().match(tag)
    if not m:
        return None

    prefix, value = m.group(1, 2)
    return rule_map()[prefix].fn, value


def resolve_tags(tags: list[str] | str, result: Props | None = None) -> Props:
    if result is None:
        result = Props({})

    if type(tags) is str:
        tags = [it.strip() for it in tags.split()]

    for it in tags:
        match = rule_fn_value(it)
        if match:
            merge(result, match[0](match[1], result))
        else:
            resolve_props(result, tagmap[it])

    return result


def merge(result: Props, data: RawTag) -> None:
    style = {**get_style(result.get('style')), **get_style(data.get('style'))}  # type: ignore[arg-type]
    result.update(data, style=style)
    result.pop('tag', None)


def resolve_props(result: Props, *props: RawTag) -> None:
    for p in props:
        ttag: str | list[str]
        if ttag := p.get('tag'):  # type: ignore[assignment]
            resolve_tags(ttag, result)
        merge(result, p)


tagmap: dict[str, Tag | TagTotal] = {
    'root': TagTotal(
        {
            'direction': 0,
            'layout': BoxLayout,
            'size': (-1, -1),
            'padding': (0, 0, 0, 0),
            'gap': (0, 0),
            'scale': 4,
            'virtual': False,
            'link': None,
            'style': {},
            'label_formatter': default_label_formatter,
            'items_align': (0, 0),
            'align': (None, None),
            'grid_columns': None,
            'grid_col': None,
        }
    ),
    'dh': {'direction': 0},
    'dv': {'direction': 1},
    'virtual': {'virtual': True},
    'non-virtual': {'virtual': False},
    'grid': {'layout': GridLayout},
}
