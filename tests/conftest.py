from dataclasses import replace

import pytest

from diagen import tags


@pytest.fixture(autouse=True)
def reset_tagmaps(mocker):
    mocker.patch.dict(tags.node._tagmap)
    mocker.patch.dict(tags.edge._tagmap)


def set_scale(mocker, scale: float) -> None:
    mocker.patch(
        'diagen.tags.node.default_props', lambda: replace(tags.node._default_props, scale=scale)
    )
