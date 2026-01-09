import re
from dataclasses import dataclass, replace
from typing import Callable, Generic, Iterable, Mapping, TypeVar

from .props import BackendStyle, ClassList, EdgeKeys, EdgeProps, NodeKeys, NodeProps

__all__ = [
    'NodeProps',
    'EdgeProps',
    'NodeKeys',
    'EdgeKeys',
    'BackendStyle',
    'ClassList',
    'KeysT',
    'PropsT',
]

KeysT = TypeVar('KeysT', NodeKeys, EdgeKeys)
PropsT = TypeVar('PropsT', NodeProps, EdgeProps)

_smap_cache: dict[str, BackendStyle] = {}


def get_style(style: str | BackendStyle | None) -> BackendStyle:
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


RuleValue = Callable[[str, PropsT], KeysT]
NodeRuleValue = RuleValue[NodeProps, NodeKeys]
EdgeRuleValue = RuleValue[EdgeProps, EdgeKeys]


@dataclass
class rule(Generic[PropsT, KeysT]):
    prefix: str
    fn: RuleValue[PropsT, KeysT]
    has_value: bool = True


def merge_drawio_style(old: BackendStyle, new: BackendStyle) -> BackendStyle:
    result = old.copy()
    if '@pop' in new:
        new = new.copy()
        todelete: list[str] = new.pop('@pop')  # type: ignore[assignment]
        for it in todelete:
            result.pop(it, None)
    result.update(new)
    return result


class StyleMap(Generic[PropsT, KeysT]):
    _styles: dict[str, KeysT]
    _rules: list[rule[PropsT, KeysT]]
    _rules_re: re.Pattern[str]
    _rules_map: dict[str, rule[PropsT, KeysT]]
    _default_props: PropsT

    def __init__(self, default_props: PropsT) -> None:
        self._styles = {}
        self._rules = []
        self._rule_cache: dict[str, tuple[RuleValue[PropsT, KeysT], str]] = {}
        self._process_rules()
        self._default_props = default_props

    def update(self, styles: Mapping[str, KeysT]) -> None:
        self._styles.update(styles)

    def add_rules(self, rules: Iterable[rule[PropsT, KeysT]]) -> None:
        self._rules.extend(rules)
        self._process_rules()

    def _process_rules(self) -> None:
        vparts = [it.prefix for it in self._rules if it.has_value]
        self._rules_re = re.compile(rf'({"|".join(vparts)})-(.+)')
        self._rules_map = {it.prefix: it for it in self._rules}

    def _rule_value(self, cls: str) -> tuple[RuleValue[PropsT, KeysT], str] | None:
        try:
            return self._rule_cache[cls]
        except KeyError:
            pass

        m = self._rules_re.match(cls)
        if not m:
            return None

        prefix, value = m.group(1, 2)
        result = self._rule_cache[cls] = self._rules_map[prefix].fn, value
        return result

    def resolve_classes(self, classes: ClassList, result: PropsT | None = None) -> PropsT:
        if result is None:
            result = self.default_props()

        if type(classes) is str:
            classes = [it.strip() for it in classes.split()]

        for it in classes:
            if it in self._styles:
                self.resolve_props((self._styles[it],), result)
            else:
                match = self._rule_value(it)
                if match:
                    self.merge(result, match[0](match[1], result))
                else:
                    raise ValueError(f'Unknown class or rule: {it}')

        return result

    def merge(self, result: PropsT, data: KeysT) -> None:
        drawio_style = merge_drawio_style(result.drawio_style, get_style(data.get('drawio_style')))
        vars(result).update(data, drawio_style=drawio_style)

    def resolve_props(self, props: Iterable[KeysT], result: PropsT | None = None) -> PropsT:
        if result is None:
            result = self.default_props()

        for p in props:
            classes: ClassList
            if classes := p.get('classes'):  # type: ignore[assignment]
                self.resolve_classes(classes, result)
            self.merge(result, p)

        return result

    def default_props(self) -> PropsT:
        return replace(self._default_props)


NodeStyleMap = StyleMap[NodeProps, NodeKeys]
EdgeStyleMap = StyleMap[EdgeProps, EdgeKeys]
