import pytest

from diagen import drawio, stack, vstack
from diagen.shapes.c4 import (
    Boundary,
    Bus,
    Component,
    Container,
    ExtPerson,
    ExtSystem,
    Person,
    Pod,
    Storage,
    System,
    edge,
)


@pytest.fixture
def render(tmp_path_factory):
    def inner(fname, s):
        with open(tmp_path_factory.getbasetemp() / fname, 'w') as f:
            f.write(drawio.render(s, compress=False))

    return inner


def test_full(render):
    with stack['p-12 gap-24'] as s:
        with vstack['gap-40']:
            ext_user = ExtPerson('Customer')
            ext_host = ExtSystem("Customer's\nserver")

        with Boundary['dv']('Some Company'):
            portal = System('Portal', 'portal.company.com', 'Control panel for customers')
            packages = System('Packages', 'packages.company.com')
            cdn = System('File storage', 'cdn.company.com')

    edge(ext_user.t, portal.l, 'Creates registration keys', 'Browser')
    edge(ext_host.r, portal.l, 'Checks registration', 'cli, HTTP')
    edge(ext_host.r, packages, 'Downloads patches', 'cli, HTTP')
    edge(ext_host.b, cdn.l, 'Downloads package updates', 'yum, apt, HTTP')
    edge(packages.t, portal.b, 'Pushes usage data', 'Postgres')
    edge(portal.b, packages.t, 'Pushes license updates', 'python script, SSH')

    render('showcase.drawio', s)


def test_c4_shapes(render):
    with Boundary['dv gap-8 grid-3 items-align-start items-valign-end']('Boundary') as s:
        with stack['col-1: gap-8']:
            Person('Person')
            ExtPerson('Ext person')

        System('System')
        ExtSystem['col-3']('Ext System')
        Container['col-2']('Container')

        Storage['col-1']('DB')
        Pod('Pod')
        Bus['valign-start']('Bus')

        Component['col-1: align-end']('Component')

    render('c4-shapes.drawio', s)
