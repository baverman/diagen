import re
from dataclasses import dataclass, replace
from typing import Callable, Generic, Iterable, Mapping, TypeVar

from .props import EdgeProps, EdgeTag, NodeProps, NodeTag, Style

__all__ = ['NodeProps', 'EdgeProps', 'NodeTag', 'EdgeTag', 'Style']

RawTag = Mapping[str, object]
TagT = TypeVar('TagT', bound=NodeTag | EdgeTag)
PropsT = TypeVar('PropsT', bound=NodeProps | EdgeProps)

_smap_cache: dict[str, Style] = {}


def get_style(style: str | Style | None) -> Style:
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


RuleValue = Callable[[str, PropsT], TagT]
NodeRuleValue = RuleValue[NodeProps, NodeTag]
EdgeRuleValue = RuleValue[EdgeProps, EdgeTag]


@dataclass
class rule(Generic[PropsT, TagT]):
    prefix: str
    fn: RuleValue[PropsT, TagT]
    has_value: bool = True


class TagMap(Generic[PropsT, TagT]):
    _tagmap: dict[str, TagT]
    _rules: list[rule[PropsT, TagT]]
    _rules_re: re.Pattern[str]
    _rules_map: dict[str, rule[PropsT, TagT]]

    def __init__(self, default_props: PropsT) -> None:
        self._tagmap = {}
        self._rules = []
        self._rule_cache: dict[str, tuple[RuleValue[PropsT, TagT], str]] = {}
        self._process_rules()
        self._default_props = default_props

    def update(self, tags: Mapping[str, TagT]) -> None:
        self._tagmap.update(tags)

    def add_rules(self, rules: Iterable[rule[PropsT, TagT]]) -> None:
        self._rules.extend(rules)
        self._process_rules()

    def _process_rules(self) -> None:
        vparts = [it.prefix for it in self._rules if it.has_value]
        self._rules_re = re.compile(rf'({"|".join(vparts)})-(.+)')
        self._rules_map = {it.prefix: it for it in self._rules}

    def _rule_value(self, tag: str) -> tuple[RuleValue[PropsT, TagT], str] | None:
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

    def resolve_tags(self, tags: list[str] | str, result: PropsT | None = None) -> PropsT:
        if result is None:
            result = self.default_props()

        if type(tags) is str:
            tags = [it.strip() for it in tags.split()]

        for it in tags:
            match = self._rule_value(it)
            if match:
                self.merge(result, match[0](match[1], result))
            else:
                self.resolve_props((self._tagmap[it],), result)

        return result

    def merge(self, result: PropsT, data: TagT) -> None:
        style = {**result.style, **get_style(data.get('style'))}  # type: ignore[arg-type]
        vars(result).update(data, style=style)

    def resolve_props(self, props: Iterable[TagT], result: PropsT | None = None) -> PropsT:
        if result is None:
            result = self.default_props()

        for p in props:
            ttag: str | list[str]
            if ttag := p.get('tag'):  # type: ignore[assignment]
                self.resolve_tags(ttag, result)
            self.merge(result, p)

        return result

    def default_props(self) -> PropsT:
        return replace(self._default_props)
