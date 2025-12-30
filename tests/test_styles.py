import pytest

from diagen import styles

from .conftest import set_scale

resolve_classes = styles.node.resolve_classes


@pytest.fixture(autouse=True)
def setup(mocker):
    set_scale(mocker, 4)


def test_resolve_rules():
    result = resolve_classes('p-1 px-2')
    assert result.padding == (8, 4, 8, 4)


def test_resolve_classes(mocker):
    styles.node.update({'some': {'classes': 'p-1 px-2', 'gap': 20}})
    result = resolve_classes('some')
    assert result.padding == (8, 4, 8, 4)
    assert result.gap == 20


def test_grid_col_setter():
    assert styles.setGridCol('grid_col')('1', {}) == {'grid_col': (1, 2)}
    assert styles.setGridCol('grid_col')('1:', {}) == {'grid_col': (1, 0)}
    assert styles.setGridCol('grid_col')('1:-2', {}) == {'grid_col': (1, -2)}

    assert styles.setGridCol('grid_col')('1/2', {}) == {'grid_col': (1, 3)}
    assert styles.setGridCol('grid_col')('1/0', {}) == {'grid_col': (1, 1)}
    assert styles.setGridCol('grid_col')('1/-1', {}) == {'grid_col': (1, 0)}
