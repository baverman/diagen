from diagen import edge, isolate, node


def type_check_edge_factory_invalid_signature() -> None:
    n = node()
    edge()  # type: ignore[call-arg]
    edge(n)  # type: ignore[call-arg]


def type_check_props_chain_signature() -> None:
    node.props(invalid=10)  # type: ignore[call-arg]


def test_node_factory_signatures() -> None:
    node()

    n = node(c := node())
    assert n.children == [c]

    n = node(props={'scale': 10})
    assert n.props.scale == 10
    assert n.children == []

    n = node(c := node(), props={'scale': 10})
    assert n.props.scale == 10
    assert n.children == [c]


def test_edge_factory_signatures() -> None:
    s = node()
    t = node()

    result = edge(s, t)
    assert result.source == s
    assert result.target == t

    result = edge(s, t, props={'scale': 10})
    assert result.source == s
    assert result.target == t
    assert result.props.scale == 10


def test_props_builder() -> None:
    fancy = node.props(scale=1, size=(42, 42))

    n = fancy()
    assert n.props.size == (42, 42)

    s = node()
    t = node()
    e = edge.props(scale=2, arc_size=10)(s, t)
    e.props.drawio_style['arcSize'] == 20


def test_repr() -> None:
    repr(node())


def test_grid_classes() -> None:
    n = node['at-2']()
    assert n.props.grid_cell[0].start == 2


def test_align_classes() -> None:
    n = node['valign-start']['valign-center']['items-align-start']['align-75']()
    assert n.props.align == (0.5, 0)
    assert n.props.items_align == (-1, 0)


def test_node_size_classes() -> None:
    n = node['size-5']()
    assert n.props.size == (20, 20)

    n = node['size-5/3']()
    assert n.props.size == (20, 12)


def test_edge_label_classes() -> None:
    s, t = node(), node()
    e = edge['label-75/10 label-/20'](s, t)
    assert e.props.label_offset == (0.5, 80)


def test_function_should_populate_parent_nodes() -> None:
    def fn() -> None:
        node('inner')

    with node as s:
        fn()

    assert s.children[0].label == ['inner']


def test_isolated_function_should_not_populate_parent_nodes() -> None:
    @isolate()
    def fn() -> None:
        node('inner')

    with node as s:
        fn()

    assert not s.children
