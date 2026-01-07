import pytest

from diagen import drawio, stack, vstack
from diagen.shapes import c4


@pytest.fixture
def render(tmp_path_factory):
    def inner(fname, s):
        with open(tmp_path_factory.getbasetemp() / fname, 'w') as f:
            f.write(drawio.render(s, compress=False))

    return inner


def test_full(render):
    with stack['p-12 gap-24'] as s:
        with vstack['gap-40']:
            ext_user = c4.ExtPerson('Customer')
            ext_host = c4.ExtSystem("Customer's\nserver")

        with c4.Boundary['dv']('Some Company'):
            portal = c4.System('Portal', 'portal.company.com', 'Control panel for customers')
            packages = c4.System('Packages', 'packages.company.com')
            cdn = c4.System('File storage', 'cdn.company.com')

    c4.edge['label--0.2/12'](ext_host.r, portal.l[2], 'Checks registration', 'cli, HTTP')
    c4.edge['label-0.2'](ext_user.t, portal.l, 'Creates registration keys', 'Browser')
    c4.edge['label--0.3'](ext_host.r, packages, 'Downloads patches', 'cli, HTTP')
    c4.edge['label-0.2'](ext_host.b, cdn.l, 'Downloads package updates', 'yum, apt, HTTP')
    c4.edge['label-0.2/6'](
        portal.b[1], packages.t[1], 'Pushes license updates', 'python script, SSH'
    )
    c4.edge['label-0.3'](packages.t[0.2], portal.b[0.2], 'Pushes usage data', 'Postgres')

    render('showcase.drawio', s)


def test_c4_shapes(render):
    with c4.Boundary['dv gap-8 grid-3 items-align-start items-valign-end']('Boundary') as s:
        with stack['col-1: gap-8']:
            c4.Person('Person')
            c4.ExtPerson('Ext person')

        c4.System('System')
        c4.ExtSystem['col-3']('Ext System')
        c4.Container['col-2']('Container')

        c4.Storage['col-1']('DB')
        c4.Pod('Pod')
        c4.Bus['valign-start']('Bus')

        c4.Component['col-1: align-end']('Component')

    render('c4-shapes.drawio', s)
