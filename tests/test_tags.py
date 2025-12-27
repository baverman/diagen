import pytest

from diagen import tags

from .conftest import set_scale

resolve_tags = tags.node.resolve_tags


@pytest.fixture(autouse=True)
def setup(mocker):
    set_scale(mocker, 4)


def test_resolve_rules():
    result = resolve_tags('p-1 px-2')
    assert result.padding == (8, 4, 8, 4)


def test_resolve_tags(mocker):
    tags.node.update({'some': {'tag': 'p-1 px-2', 'gap': 20}})
    result = resolve_tags('some')
    assert result.padding == (8, 4, 8, 4)
    assert result.gap == 20


def test_grid_col_setter():
    assert tags.setGridCol('grid_col')('1', {}) == {'grid_col': (1, 2)}
    assert tags.setGridCol('grid_col')('1:', {}) == {'grid_col': (1, 0)}
    assert tags.setGridCol('grid_col')('1:-2', {}) == {'grid_col': (1, -2)}

    assert tags.setGridCol('grid_col')('1/2', {}) == {'grid_col': (1, 3)}
    assert tags.setGridCol('grid_col')('1/0', {}) == {'grid_col': (1, 1)}
    assert tags.setGridCol('grid_col')('1/-1', {}) == {'grid_col': (1, 0)}
