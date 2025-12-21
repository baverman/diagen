import base64
import xml.etree.ElementTree as ET
import zlib
from collections import namedtuple
from itertools import count
from urllib import parse

from .nodes import Node
from .props import NodeProps

element = namedtuple('element', 'tag attrs children')


def style_to_str(style: dict[str, object] | str | None) -> str:
    if not style:
        return ''
    if isinstance(style, str):
        return style
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
        'id': node.props.id,
        'parent': node.parent and node.parent.props.id or '__root__',
        'vertex': '1',
        'style': style_to_str(node.props.style),
    }

    if label := node.get_label():
        attrs['value'] = label

    if node.props.link:
        attrs['link'] = node.props.link

    return element('mxCell', attrs, [make_geom(node)])


def make_model(node: Node) -> element:
    node.arrange()
    root_node = Node(NodeProps(id='__root__', virtual=False), node)
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
    # for it in context.edges:
    #     children.append(it.as_graph())

    idconter = count()
    for it in root_node.walk():
        if not it.props.get('id'):
            it.props['id'] = f'diagen-{next(idconter)}'
        children.append(node_element(it))

    root.children.extend(reversed(children))
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
