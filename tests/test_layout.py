import pytest

from diagen import grid, node, stack, vstack

from .conftest import set_scale


@pytest.fixture(autouse=True)
def setup(mocker):
    set_scale(mocker, 1)


def test_hstack():
    s = stack['gap-2 p-1'](n1 := node['w-1 h-1'](), n2 := node['w-2 h-3']())
    assert s.size[0] == 2 + 2 + 1 + 2
    assert s.size[1] == 5

    s.arrange()
    assert s.position == (0, 0)
    assert n1.position == (1, 2)
    assert n2.position == (4, 1)


def test_vstack():
    s = vstack['gap-2 p-1'](n1 := node['w-1 h-1'](), n2 := node['w-2 h-3']())
    assert s.size[1] == 2 + 2 + 1 + 3
    assert s.size[0] == 4

    s.arrange()
    assert s.position == (0, 0)
    assert n1.position == (1.5, 1)
    assert n2.position == (1, 4)


def test_stack_items_align():
    s = stack['items-align-start'](n1 := node['w-1 h-1'](), n2 := node['w-1 h-3']())

    s.arrange()
    assert n1.position == (0, 0)
    assert n2.position == (1, 0)


def test_stack_align():
    s = stack['items-align-start'](n1 := node['w-1 h-1 align-end'](), n2 := node['w-1 h-3']())

    s.arrange()
    assert n1.position == (0, 2)
    assert n2.position == (1, 0)


def test_grid():
    with grid['p-1 gap-1'] as s:
        n11 = node['w-1 h-1']()
        n12 = node['w-1 h-3']()
        n21 = node['col-1 w-3 h-1']()
        n22 = node['w-3 h-3']()

    s.arrange()
    assert n11.position == (2, 2)
    assert n12.position == (6, 1)
    assert n21.position == (1, 6)
    assert n22.position == (5, 5)


def test_context_manager():
    with stack as s:
        n1 = node()
        n2 = stack(n3 := node())

    assert s.children == [n1, n2]
    assert n2.children == [n3]
