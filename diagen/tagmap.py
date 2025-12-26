import re
from dataclasses import dataclass
from typing import Callable, Generic, Iterable, Mapping, TypeVar

from .props import EdgeProps, EdgeTag, EdgeTagDefault, NodeProps, NodeTag, NodeTagDefault

__all__ = [
    'AnyNodeTag',
    'AnyEdgeTag',
    'NodeProps',
    'EdgeProps',
    'EdgeTagDefault',
    'NodeTagDefault',
    'NodeTag',
    'EdgeTag',
]

RawTag = Mapping[str, object]
AnyNodeTag = NodeTag | NodeTagDefault
AnyEdgeTag = EdgeTag | EdgeTagDefault

TagT = TypeVar('TagT', bound=AnyNodeTag | AnyEdgeTag)
PropsT = TypeVar('PropsT', bound=NodeProps | EdgeProps)
TagDefaultT = TypeVar('TagDefaultT', bound=NodeTagDefault | EdgeTagDefault)

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


RuleValue = Callable[[str, TagDefaultT], TagT]
NodeRuleValue = RuleValue[NodeTagDefault, NodeTag]
EdgeRuleValue = RuleValue[EdgeTagDefault, EdgeTag]


@dataclass
class rule(Generic[TagDefaultT, TagT]):
    prefix: str
    fn: RuleValue[TagDefaultT, TagT]
    has_value: bool = True


class TagMap(Generic[PropsT, TagDefaultT, TagT]):
    _tagmap: dict[str, TagT]
    _rules: list[rule[TagDefaultT, TagT]]
    _rules_re: re.Pattern[str]
    _rules_map: dict[str, rule[TagDefaultT, TagT]]

    def __init__(self) -> None:
        self._tagmap = {}
        self._rules = []
        self._rule_cache: dict[str, tuple[RuleValue[TagDefaultT, TagT], str]] = {}
        self._process_rules()

    def update(self, tags: Mapping[str, TagT]) -> None:
        self._tagmap.update(tags)

    def add_rules(self, rules: Iterable[rule[TagDefaultT, TagT]]) -> None:
        self._rules.extend(rules)
        self._process_rules()

    def _process_rules(self) -> None:
        vparts = [it.prefix for it in self._rules if it.has_value]
        self._rules_re = re.compile(rf'({"|".join(vparts)})-(.+)')
        self._rules_map = {it.prefix: it for it in self._rules}

    def _rule_value(self, tag: str) -> tuple[RuleValue[TagDefaultT, TagT], str] | None:
        try:
            return self._rule_cache[tag]
        except KeyError:
            pass

        m = self._rules_re.match(tag)
        if not m:
            return None

        prefix, value = m.group(1, 2)
        result = self._rule_cache[tag] = self._rules_map[prefix].fn, value
        return result

    def resolve_tags(self, tags: list[str] | str, result: PropsT) -> None:
        if type(tags) is str:
            tags = [it.strip() for it in tags.split()]

        for it in tags:
            match = self._rule_value(it)
            if match:
                self.merge(result, match[0](match[1], result))  # type: ignore[arg-type]
            else:
                self.resolve_props(result, self._tagmap[it])

    def merge(self, result: PropsT, data: RawTag) -> None:
        style = {**get_style(result.get('style')), **get_style(data.get('style'))}  # type: ignore[arg-type]
        result.update(data, style=style)
        result.pop('tag', None)

    def resolve_props(self, result: PropsT, *props: RawTag) -> None:
        for p in props:
            ttag: str | list[str]
            if ttag := p.get('tag'):  # type: ignore[assignment]
                self.resolve_tags(ttag, result)
            self.merge(result, p)
