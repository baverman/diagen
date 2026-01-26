from textwrap import dedent

import diagen
from diagen.layouts import arrange, node_map
from diagen.layouts.grid import GridLayout
from diagen.nodes import Node

grid = diagen.grid.props(scale=1)
vgrid = diagen.vgrid.props(scale=1)
node = diagen.node.props(scale=1)


def assert_grid(node: Node, expected: str) -> None:
    layout: GridLayout = node.props.layout  # type: ignore[assignment]
    cells = layout.cells(arrange(node)).cells

    col_count = max(it.end[0] for it in cells)
    row_count = max(it.end[1] for it in cells)
    rc = [['.'] * col_count for _ in range(row_count)]
    for idx, it in enumerate(cells):
        for i in range(it.start[1], it.end[1]):
            for j in range(it.start[0], it.end[0]):
                rc[i][j] = str(idx)

    result = '\n'.join(''.join(it) for it in rc)
    assert result == dedent(expected).strip()


def test_hstack() -> None:
    s = grid['gap-2 p-1'](n1 := node['w-1 h-1'](), n2 := node['w-2 h-3']())

    nm = node_map(arrange(s))
    assert nm[s].size[0] == 2 + 2 + 1 + 2
    assert nm[s].size[1] == 5

    assert nm[s].position == (0, 0)
    assert nm[n1].position == (1, 2)
    assert nm[n2].position == (4, 1)


def test_vstack() -> None:
    s = vgrid['gap-2 p-1'](n1 := node['w-1 h-1'](), n2 := node['w-2 h-3']())
    nm = node_map(arrange(s))

    assert nm[s].size[1] == 2 + 2 + 1 + 3
    assert nm[s].size[0] == 4

    assert nm[s].position == (0, 0)
    assert nm[n1].position == (1.5, 1)
    assert nm[n2].position == (1, 4)


def test_stack_items_align() -> None:
    s = grid['items-valign-start'](n1 := node['w-1 h-1'](), n2 := node['w-1 h-3']())
    nm = node_map(arrange(s))

    assert nm[n1].position == (0, 0)
    assert nm[n2].position == (1, 0)


def test_stack_align() -> None:
    s = grid['items-valign-start'](n1 := node['w-1 h-1 valign-end'](), n2 := node['w-1 h-3']())
    nm = node_map(arrange(s))

    assert nm[n1].position == (0, 2)
    assert nm[n2].position == (1, 0)


def test_grid() -> None:
    with grid['p-1 gap-1'] as s:
        n11 = node['w-1 h-1']()
        n12 = node['w-1 h-3']()
        n21 = node['col-1 w-3 h-1']()
        n22 = node['w-3 h-3']()

    nm = node_map(arrange(s))
    assert nm[n11].position == (2, 2)
    assert nm[n12].position == (6, 1)
    assert nm[n21].position == (1, 6)
    assert nm[n22].position == (5, 5)


def test_context_manager() -> None:
    with grid as s:
        n1 = node()
        n2 = grid(n3 := node())

    assert s.children == [n1, n2]
    assert n2.children == [n3]


def test_grid_cells() -> None:
    with grid() as g:
        node()
        node()
    assert_grid(g, '01')

    with grid['dv']() as g:
        node()
        node()
    assert_grid(g, '0\n1')

    with grid['grid-cols-3']() as g:
        node()
        node['col-2:']()
    assert_grid(g, '011')

    with grid['grid-rows-3']() as g:
        node()
        node['row-2:']()
    assert_grid(g, '0\n1\n1')

    with grid() as g:
        node()
        node['col-1']()
    assert_grid(g, '0\n1')


def test_grid_implicit_max_size() -> None:
    with grid['grid-cols-3']() as g:
        node()
        node['col-3']()
        node['col-1:']()
    assert_grid(g, '0.1\n222')

    with grid() as g:
        node()
        node['col-3']()
        node['col-1:']()
    assert_grid(g, '0.1\n222')


def test_grid_positions_and_spans() -> None:
    with grid() as g:
        node()
        node['row-3 col-3']()
        node()

    assert_grid(
        g,
        """\
            0...
            ....
            ..12
        """,
    )

    with grid() as g:
        node()
        node['row-3+2 col-2+2']()
        node()

    assert_grid(
        g,
        """\
            0...
            ....
            .112
            .11.
        """,
    )

    with grid() as g:
        node()
        node['at-2/+2 span-2/:5']()
        node()

    assert_grid(
        g,
        """\
            0...
            ....
            .112
            .11.
        """,
    )


def test_grid_row_wrap() -> None:
    with grid['grid-cols-3'] as g:
        node['col-3']()
        node()

    assert_grid(g, '..0\n1..')


def test_implicit_spans() -> None:
    with grid as g:
        node['row-2']()
        node['col-+3 row-:4']()

    assert_grid(
        g,
        """\
            ....
            0111
            .111
        """,
    )


def test_subgrid() -> None:
    with grid as g:
        with grid['subgrid at-2/2']:
            node['at-2/2']()
        node()

    assert_grid(
        g,
        """\
            ....
            ...1
            ..0.
        """,
    )


def test_nested_subgrid() -> None:
    with grid as g:
        with grid['subgrid at-2/2']:
            with grid['subgrid at-+1/+1']:
                node['at-2/2']()
        node()

    assert_grid(
        g,
        """\
            .....
            ....1
            .....
            ...0.
        """,
    )


def test_nested_subgrid_span() -> None:
    with grid as g:
        with grid['subgrid at-2/2 span-2/2']:
            node()
        node()

    assert_grid(
        g,
        """\
            ....
            .0.1
        """,
    )

    with grid as g:
        with grid['subgrid dv at-2/2 span-2/2']:
            node()
        node()

    assert_grid(
        g,
        """\
            ...
            .01
        """,
    )

    with grid as g:
        with grid['subgrid at-2/2 span-2']:
            node()
        node()

    assert_grid(
        g,
        """\
            ....
            .0.1
        """,
    )

    with grid as g:
        with grid['subgrid at-2/2 span-/2']:
            node()
        node()

    assert_grid(
        g,
        """\
            ...
            .01
        """,
    )
