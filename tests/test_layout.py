import pytest

from diagen.layout import node, stack, vstack
from diagen.tags import tagmap


@pytest.fixture(autouse=True)
def setup(mocker):
    mocker.patch.dict(tagmap['root'])
    tagmap['root']['scale'] = 1


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
