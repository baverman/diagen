from .. import base_edge, base_node, styles
from ..props import EdgeProps, NodeProps


def c4_label_fmt(props: NodeProps | EdgeProps, label: list[str]) -> str:
    if not label:
        return ''

    title = label[0]
    tech = label[1] if len(label) > 1 else None
    desc = label[2] if len(label) > 2 else None
    return '\n'.join(
        filter(
            None, (f'<b>{title}</b>', tech and f'[{tech}]', desc and f'<br><small>{desc}</small>')
        )
    )


styles.node.update(
    {
        'c4-base': {
            'label_formatter': c4_label_fmt,
            'drawio_style': 'html=1;fontSize=12',
        },
        'c4-base-person': {
            'classes': 'c4-base w-28 h-25',
            'drawio_style': 'shape=mxgraph.c4.person2',
        },
        'c4-person': {
            'classes': 'c4-base-person',
            'drawio_style': 'fillColor=#083F75;strokeColor=#06315C;fontColor=#ffffff',
        },
        'c4-ext-person': {
            'classes': 'c4-base-person',
            'drawio_style': 'fillColor=#6C6477;strokeColor=#4D4D4D;fontColor=#ffffff',
        },
        'c4-base-arcs': {
            'drawio_style': 'arcSize=15;absoluteArcSize=1',
        },
        'c4-base-node': {
            'classes': 'c4-base c4-base-arcs w-40 h-20',
            'drawio_style': 'rounded=1;labelBackgroundColor=none;fontColor=#ffffff',
        },
        'c4-system': {
            'classes': 'c4-base-node',
            'drawio_style': 'fillColor=#1061B0;strokeColor=#0D5091',
        },
        'c4-ext-system': {
            'classes': 'c4-base-node',
            'drawio_style': 'fillColor=#8C8496;strokeColor=#736782',
        },
        'c4-container': {
            'classes': 'c4-base-node',
            'drawio_style': 'fillColor=#23A2D9;strokeColor=#0E7DAD',
        },
        'c4-storage': {
            'classes': 'c4-container h-24',
            'drawio_style': 'shape=cylinder3;size=10;boundedLbl=1',
        },
        'c4-pod': {
            'classes': 'c4-container h-32',
            'drawio_style': 'shape=hexagon;perimeter=hexagonPerimeter;arcSize=15',
        },
        'c4-bus': {
            'classes': 'c4-container',
            'drawio_style': 'shape=cylinder3;direction=south;size=10;boundedLbl=1',
        },
        'c4-boundary': {
            'classes': 'c4-base c4-base-arcs p-12 gap-40 dashed-6-4',
            'drawio_style': 'rounded=1;fillColor=none;strokeColor=#666666;fontColor=#333333;labelBackgroundColor=none;align=left;verticalAlign=bottom;labelBorderColor=none;spacingLeft=4;spacingBottom=0;labelPadding=0;arcSize=10',
        },
        'c4-component': {
            'classes': 'c4-base-node',
            'drawio_style': 'fillColor=#63BEF2;strokeColor=#2086C9;arcSize=7',
        },
    }
)

styles.edge.update(
    {
        'c4-base': {
            'classes': 'ortho rounded-5 color-#828282 end-classic-thin',
            'label_formatter': c4_label_fmt,
            'drawio_style': 'jettySize=auto;html=1;fontSize=12;fontColor=#404040',
        },
        'c4-edge': {
            'classes': 'c4-base',
            'drawio_style': 'perimeterSpacing=4',
        },
    }
)

Person = base_node['c4-person']
ExtPerson = base_node['c4-ext-person']
System = base_node['c4-system']
ExtSystem = base_node['c4-ext-system']
Container = base_node['c4-container']
Component = base_node['c4-component']
Boundary = base_node['c4-boundary']
Storage = base_node['c4-storage']
Pod = base_node['c4-pod']
Bus = base_node['c4-bus']
edge = base_edge['c4-edge']
