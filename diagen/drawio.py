import base64
import xml.etree.ElementTree as ET
import zlib
from collections import namedtuple
from itertools import count
from typing import Literal
from urllib import parse

from . import base_node
from .nodes import Edge, Node, Port
from .props import NodeTag, Style
from .utils import dtup2

element = namedtuple('element', 'tag attrs children')


def style_to_str(style: Style) -> str:
    if not style:
        return ''
    return ';'.join(f'{k}={v}' for k, v in style.items())


def make_geom(node: Node) -> element:
    x, y = node.position
    w, h = node.size
    return element(
        'mxGeometry',
        {'as': 'geometry', 'x': str(x), 'y': str(y), 'width': str(w), 'height': str(h)},
        [],
    )


def node_element(node: Node) -> element:
    attrs = {
        'id': node.id,
        'parent': node.parent and node.parent.id or '__root__',
        'vertex': '1',
        'style': style_to_str(node.props.style),
    }

    if label := node.get_label():
        attrs['value'] = label

    if node.props.link:
        attrs['link'] = node.props.link

    return element('mxCell', attrs, [make_geom(node)])


def port_element(
    edge: Edge, port: Port, axis: int, align: float, offset: tuple[float, float]
) -> element:
    node = port.node
    o = [1, 0][axis]
    attrs = {
        'id': edge.id + '-' + node.id,
        'parent': node.id,
        'vertex': '1',
        'style': 'container=0;fillColor=none;strokeColor=none',
    }
    port_node = base_node(NodeTag(size=(3, 3)))
    ac = node.origin[axis] + offset[0] * node.size[axis] - 1.5
    oc = node.origin[o] + (node.size[o] - 3) / 2.0 * (align + 1) + offset[1]
    port_node.position = dtup2(axis, ac, oc)
    return element('mxCell', attrs, [make_geom(port_node)])


def arrange_port(edge: Edge, port: Port) -> element:
    edges = port.node.edge_positions[port.side]
    pos = edges[edge]
    axis = 1 if port.side in (0, 2) else 0
    align = -1 if port.side in (0, 1) else 1
    return port_element(edge, port, axis, align, (pos, 0))


CONSTRAINT = ['west', 'north', 'east', 'south']


def port_style(port: Port, kind: Literal['source'] | Literal['target']) -> Style:
    return {f'{kind}PortConstraint': CONSTRAINT[port.side]}


def edge_element(edge: Edge) -> list[element]:
    geom = element('mxGeometry', {'as': 'geometry', 'relative': '1'}, [])
    attrs = {
        'edge': '1',
        'id': edge.id,
        'parent': edge.source.parent and edge.source.parent.id or '__root__',
        'source': edge.source.node_ref.id,
        'target': edge.target.node_ref.id,
    }

    if label := edge.get_label():
        attrs['value'] = label

    style = edge.props.style.copy()

    result: list[element | None] = []

    if isinstance(edge.source, Port):
        style.update(port_style(edge.source, 'source'))
        result.append(el := arrange_port(edge, edge.source))
        attrs['source'] = el.attrs['id']

    if isinstance(edge.target, Port):
        style.update(port_style(edge.target, 'target'))
        result.append(el := arrange_port(edge, edge.target))
        attrs['target'] = el.attrs['id']

    attrs['style'] = style_to_str(style)

    if edge.props.label_offset != (0, 0):
        geom.attrs['x'] = str(edge.props.label_offset[0])
        geom.attrs['y'] = str(edge.props.label_offset[1])
        geom.children.append(element('mxPoint', {'as': 'offset'}, []))

    # if edge.points:
    #     # points = [element('mxPoint', {'x': str(edge.source.absx + x), 'y':
    #         # str(edge.source.absy + y)}, [])
    #     #           for x, y in edge.points]
    #     points = [element('mxPoint', {'x': str(x), 'y': str(y)}, [])
    #               for x, y in edge.points]
    #     geom.kids.append(element('Array', {'as': 'points'}, points))
    #     print(edge.source.x, points)

    result.append(element('mxCell', attrs, [geom]))
    return list(filter(None, result))


def make_model(node: Node) -> element:
    node.arrange()
    root_node = base_node(node)
    root_node.id = '__root__'
    root_node.position = (0, 0)

    root = element(
        'root',
        {},
        [
            element('mxCell', {'id': '0'}, []),
            element('mxCell', {'id': '__root__', 'parent': '0'}, []),
        ],
    )

    children = []

    idconter = count()
    edges = set()
    for it in root_node.walk():
        edges.update(it.edges)
        if not it.id:
            it.id = f'diagen-{next(idconter)}'
        children.append(node_element(it))

    children.reverse()

    for edge in edges:
        if not edge.id:
            edge.id = f'diagen-{next(idconter)}'
        children.extend(edge_element(edge))

    root.children.extend(children)
    attrs = {
        'arrows': '1',
        'connect': '1',
        'fold': '0',
        'grid': '1',
        'gridSize': '10',
        'guides': '1',
        'math': '0',
        'page': '1',
        'pageScale': '1',
        'tooltips': '1',
    }
    attrs['pageWidth'] = str(node.size[0])
    attrs['pageHeight'] = str(node.size[1])
    result = element('mxGraphModel', attrs, [root])
    return result


def to_element_tree(el: element) -> ET.Element:
    e = ET.Element(el.tag, el.attrs)
    e.extend(to_element_tree(it) for it in el.children)
    return e


def raw_deflate(data: bytes) -> bytes:
    cobj = zlib.compressobj(wbits=-zlib.MAX_WBITS)
    return cobj.compress(data) + cobj.flush()


def decode(data: bytes) -> str:
    return parse.unquote_plus(
        zlib.decompress(base64.b64decode(data), wbits=-zlib.MAX_WBITS).decode()
    )


def encode(mx_graph: ET.Element) -> str:
    return base64.b64encode(
        raw_deflate(parse.quote(ET.tostring(mx_graph, encoding='utf-8')).encode('latin1'))
    ).decode()


def render(node: Node, compress: bool = True) -> str:
    et = to_element_tree(make_model(node))
    if compress:
        data = encode(et)
    else:
        data = ET.tostring(et, encoding='utf-8').decode()
    return f'<mxfile><diagram id="some-id" name="Page-1">{data}</diagram></mxfile>'
