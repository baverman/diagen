import pytest

from diagen import tags
from diagen.props import NodeProps

resolve_tags = tags.node.resolve_tags


@pytest.fixture(autouse=True)
def setup(mocker):
    mocker.patch.dict(tags.node._tagmap['root'])
    tags.node._tagmap['root']['scale'] = 4


def test_resolve_rules():
    result = NodeProps({})
    resolve_tags('root p-1 px-2', result)
    assert result.padding == (8, 4, 8, 4)


def test_resolve_tags(mocker):
    mocker.patch.dict(tags.node._tagmap)
    tags.node.update({'some': {'tag': 'root p-1 px-2', 'gap': 20}})
    result = NodeProps({})
    resolve_tags('some', result)
    assert result.padding == (8, 4, 8, 4)
    assert result.gap == 20


def test_grid_col_setter():
    assert tags.setGridCol('grid_col')('1', {}) == {'grid_col': (1, 2)}
    assert tags.setGridCol('grid_col')('1:', {}) == {'grid_col': (1, 0)}
    assert tags.setGridCol('grid_col')('1:-2', {}) == {'grid_col': (1, -2)}

    assert tags.setGridCol('grid_col')('1/2', {}) == {'grid_col': (1, 3)}
    assert tags.setGridCol('grid_col')('1/0', {}) == {'grid_col': (1, 1)}
    assert tags.setGridCol('grid_col')('1/-1', {}) == {'grid_col': (1, 0)}
