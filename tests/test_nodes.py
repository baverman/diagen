from diagen import edge, node


def type_check_edge_factory_invalid_signature() -> None:
    n = node()
    edge()  # type: ignore[call-arg]
    edge(n)  # type: ignore[call-arg]


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
