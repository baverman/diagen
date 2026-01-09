import pytest
from pytest_mock.plugin import MockerFixture

from diagen import styles

__all__ = ['MockerFixture']


@pytest.fixture(autouse=True)
def reset_stylemaps(mocker: MockerFixture) -> None:
    mocker.patch.dict(styles.node._styles)
    mocker.patch.dict(styles.edge._styles)
