from typing import Iterator

import pytest

from diagen import drawio, grid, vgrid
from diagen.nodes import Node, _children_stack
from diagen.shapes import c4


@pytest.fixture
def render(
    request: pytest.FixtureRequest, tmp_path_factory: pytest.TempPathFactory
) -> Iterator[None]:
    marker = request.node.get_closest_marker('fname')
    nodes: list[Node]
    token = _children_stack.set(nodes := [])

    yield

    if marker:
        fname = marker.args[0]
    else:
        fname = request.node.name.removeprefix('test_') + '.drawio'

    with open(tmp_path_factory.getbasetemp() / fname, 'w') as f:
        f.write(drawio.render(nodes[0], compress=False))

    _children_stack.reset(token)


def test_showcase(render: None) -> None:
    with grid['p-12 gap-24']:
        with vgrid['gap-40']:
            ext_user = c4.ExtPerson('Customer')
            ext_host = c4.ExtSystem("Customer's\nserver")

        with c4.Boundary['dv']('Some Company'):
            portal = c4.System('Portal', 'portal.company.com', 'Control panel for customers')
            packages = c4.System('Packages', 'packages.company.com')
            cdn = c4.System('File storage', 'cdn.company.com')

    c4.edge['label-40/12'](
        ext_host.r, portal.l[2]['circle fill-#a44 size-3'], 'Checks registration', 'cli, HTTP'
    )
    c4.edge['label-60'](ext_user.t, portal.l['async-10'], 'Creates registration keys', 'Browser')
    c4.edge['label-33'](ext_host.r, packages, 'Downloads patches', 'cli, HTTP')
    c4.edge['label-60'](ext_host.b, cdn.l, 'Downloads package updates', 'yum, apt, HTTP')
    c4.edge['label-66/6'](
        portal.b[1], packages.t[1], 'Pushes license updates', 'python script, SSH'
    )
    c4.edge['label-66'](packages.t[0.2], portal.b[0.2], 'Pushes usage data', 'Postgres')


def test_c4_shapes(render: None) -> None:
    with c4.Boundary['gap-8 grid-cols-3 items-align-start items-valign-end']('Boundary'):
        with grid['col-1: gap-8']:
            c4.Person('Person')
            c4.ExtPerson('Ext person')

        c4.System('System')
        c4.ExtSystem['col-3']('Ext System')
        c4.Container['col-2']('Container')

        c4.Storage['col-1']('DB')
        c4.Pod('Pod')
        c4.Bus['valign-start']('Bus')

        c4.Component['col-1: align-end']('Component')


def test_c4_shapes_t(render: None) -> None:
    with c4.Boundary['gap-8 grid-rows-3 items-align-start items-valign-end']('Boundary'):
        with vgrid['row-1: gap-8']:
            c4.Person('Person')
            c4.ExtPerson('Ext person')

        c4.System('System')
        c4.ExtSystem['row-3']('Ext System')
        c4.Container['row-2']('Container')

        c4.Storage['row-1']('DB')
        c4.Pod('Pod')
        c4.Bus['valign-start']('Bus')

        c4.Component['row-1: align-end']('Component')


def test_subgrids(render: None) -> None:
    with grid['gap-8']:
        c4.Component('(1, 1)')
        c4.Component('(2, 1)')
        c4.Component('(3, 1)')
        with c4.Boundary['subgrid at-2/2 gap-8']('B1'):
            c4.Component('(2, 2)')
            with c4.Boundary['subgrid at-2/2 p-2 gap-8']('B2'):
                c4.Component('(3, 3)')
                c4.Component['at-2/2']('(4, 4)')
        c4.Component('(4, 2)')
