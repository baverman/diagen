import re
from typing import TypeVar

T = TypeVar('T')


def dtup2(direction: int, v1: T, v2: T) -> tuple[T, T]:
    if direction == 0:
        return v1, v2
    else:
        return v2, v1


def mux2(pos: int, value: T, current: tuple[T, T]) -> tuple[T, T]:
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
