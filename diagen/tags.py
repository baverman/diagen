import functools
import re
from dataclasses import dataclass
from typing import Callable, Mapping

Tag = Mapping[str, object]

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


class Props(dict[str, object]):
    direction: int
    layout: str
    size: tuple[float, float]
    padding: tuple[float, float, float, float]
    gap: tuple[float, float]
    virtual: bool
    align: float
    self_align: float | None

    grid_columns: int | None
    grid_col: tuple[int, int] | None

    # drawio
    id: str
    link: str | None
    style: dict[str, object] | str | None
    label_formatter: Callable[['Props', list[str]], str]

    __getattr__ = dict.__getitem__


def default_label_formatter(props: Props, label: list[str]) -> str:
    return '\n'.join(label)


@dataclass
class rule:
    prefix: str
    fn: Callable[[str, Tag], Tag]
    has_value: bool = True


def setScale(name: str, scale_name: str, *pos: int) -> Callable[[str, Tag], Tag]:
    def inner(value: str, current: Tag) -> Tag:
        v = float(value) * current[scale_name]  # type: ignore[operator]
        if pos:
            result = list(current[name])  # type: ignore[call-overload]
            for p in pos:
                result[p] = v
            return {name: tuple(result)}
        else:
            return {name: v}

    return inner


def setGrid(name: str) -> Callable[[str, Tag], Tag]:
    def inner(value: str, current: Tag) -> Tag:
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
    rule('grid', lambda value, _: {'layout': 'grid', 'grid_columns': int(value)}),
    rule('col', setGrid('col')),
]


@functools.cache
def rule_re() -> re.Pattern[str]:
    vparts = [it.prefix for it in rules if it.has_value]
    return re.compile(rf'({"|".join(vparts)})-(.+)')


@functools.cache
def rule_map() -> dict[str, rule]:
    return {it.prefix: it for it in rules}


@functools.cache
def rule_fn_value(tag: str) -> tuple[Callable[[str, Tag], Tag], str] | None:
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


def merge(result: Props, data: Tag) -> None:
    style = {**get_style(result.get('style')), **get_style(data.get('style'))}  # type: ignore[arg-type]
    result.update(data, style=style)
    result.pop('tag', None)


def resolve_props(result: Props, *props: Tag) -> None:
    for p in props:
        ttag: str | list[str]
        if ttag := p.get('tag'):  # type: ignore[assignment]
            resolve_tags(ttag, result)
        merge(result, p)


tagmap: dict[str, Tag] = {
    'root': {
        'direction': 0,
        'layout': 'box',
        'size': (-1, -1),
        'padding': (0, 0, 0, 0),
        'gap': (0, 0),
        'scale': 4,
        'virtual': False,
        'link': None,
        'style': {},
        'label_formatter': default_label_formatter,
        'align': 0,
        'self_align': None,
        'grid_columns': None,
        'grid_col': None,
    },
    'dh': {'direction': 0},
    'dv': {'direction': 1},
    'virtual': {'virtual': True},
    'non-virtual': {'virtual': False},
    'align-start': {'align': -1},
    'align-end': {'align': 1},
    'align-center': {'align': 0},
    'self-align-start': {'self_align': -1},
    'self-align-end': {'self_align': 1},
    'self-align-center': {'self_align': 0},
    'grid': {'layout': 'grid'},
}
