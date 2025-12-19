import pytest

from diagen.tags import resolve_tags, tagmap


@pytest.fixture(autouse=True)
def setup(mocker):
    mocker.patch.dict(tagmap['root'])
    tagmap['root']['scale'] = 4


def test_resolve_rules():
    result = resolve_tags('root p-1 px-2')
    assert result.padding == (8, 4, 8, 4)


def test_resolve_tags(mocker):
    mocker.patch.dict(tagmap, {'some': {'tag': 'root p-1 px-2', 'gap': 20}})
    result = resolve_tags('some')
    assert result.padding == (8, 4, 8, 4)
    assert result.gap == 20
