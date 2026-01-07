import re
from typing import TypeVar

OptFloat = TypeVar('OptFloat', float, float | None)


def dtup2(direction: int, v1: float, v2: float) -> tuple[float, float]:
    if direction == 0:
        return v1, v2
    else:
        return v2, v1


def mux2(pos: int, value: float, current: tuple[OptFloat, OptFloat]) -> tuple[OptFloat, OptFloat]:
    if pos == 0:
        return value, current[1]
    else:
        return current[0], value


capital_re = re.compile('[A-Z]+')


def _replace(match: re.Match[str]) -> str:
    m = match.group(0).lower()
    if len(m) > 1:
        return '-' + m + '-'
    return '-' + m


def kebab_case(string: str) -> str:
    return capital_re.sub(_replace, string).lstrip('-')
