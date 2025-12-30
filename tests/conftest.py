from dataclasses import replace

import pytest

from diagen import styles


@pytest.fixture(autouse=True)
def reset_stylemaps(mocker):
    mocker.patch.dict(styles.node._styles)
    mocker.patch.dict(styles.edge._styles)


def set_scale(mocker, scale: float) -> None:
    mocker.patch(
        'diagen.styles.node.default_props', lambda: replace(styles.node._default_props, scale=scale)
    )
