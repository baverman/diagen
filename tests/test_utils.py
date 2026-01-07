from diagen import styles
from diagen.utils import kebab_case


def test_arrow_classes():
    result = set(kebab_case(it) for it in styles.ARROW_TYPES)
    assert result == {
        'none',
        'classic',
        'classic-thin',
        'block',
        'block-thin',
        'open',
        'open-thin',
        'oval',
        'diamond',
        'diamond-thin',
        'async',
        'open-async',
        'half-circle',
        'dash',
        'cross',
        'circle-plus',
        'circle',
        'base-dash',
        'er-one',
        'er-mand-one',
        'er-many',
        'er-one-to-many',
        'er-zero-to-one',
        'er-zero-to-many',
        'double-block',
    }
