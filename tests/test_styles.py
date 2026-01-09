from diagen import styles
from diagen.props import NodeKeys, NodeProps

resolve_classes = styles.node.resolve_classes
edge_resolve_classes = styles.edge.resolve_classes


def nprops(data: NodeKeys) -> NodeProps:
    return data  # type: ignore[return-value]


def test_resolve_rules() -> None:
    result = resolve_classes('p-1 px-2')
    assert result.padding == (8, 4, 8, 4)


def test_resolve_is_immutable() -> None:
    props = styles.node.default_props()

    styles.node.resolve_classes('p-1', props)
    assert props.padding == (0, 0, 0, 0)

    styles.node.resolve_props(({'scale': 42},), props)
    assert props.scale == 4

    styles.node.resolve_classes('p-1', props, inplace=True)
    assert props.padding == (4, 4, 4, 4)

    styles.node.resolve_props(({'scale': 42},), props, inplace=True)
    assert props.scale == 42


def test_resolve_classes() -> None:
    styles.node.update({'some': {'classes': 'p-1 px-2', 'gap': (20, 20)}})
    result = resolve_classes('some')
    assert result.padding == (8, 4, 8, 4)
    assert result.gap == (20, 20)


def test_grid_col_setter() -> None:
    assert styles.setGridCol('grid_col')('1', nprops({})) == {'grid_col': (1, 2)}
    assert styles.setGridCol('grid_col')('1:', nprops({})) == {'grid_col': (1, 0)}
    assert styles.setGridCol('grid_col')('1:-2', nprops({})) == {'grid_col': (1, -2)}

    assert styles.setGridCol('grid_col')('1/2', nprops({})) == {'grid_col': (1, 3)}
    assert styles.setGridCol('grid_col')('1/0', nprops({})) == {'grid_col': (1, 1)}
    assert styles.setGridCol('grid_col')('1/-1', nprops({})) == {'grid_col': (1, 0)}


def test_edge_style() -> None:
    result = edge_resolve_classes('ortho edge-style-none')
    assert '@pop' not in result.drawio_style
    assert 'edgeStyle' not in result.drawio_style
    assert '@pop' in styles.edge._styles['edge-style-none']['drawio_style']
