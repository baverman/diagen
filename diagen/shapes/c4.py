from .. import root
from ..tags import Props, Tag, tagmap


def c4_label_fmt(props: Props, label: list[str]) -> str:
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


TAGS: dict[str, Tag] = {
    'c4-base': {
        'label_formatter': c4_label_fmt,
        'style': 'html=1;fontSize=12',
    },
    'c4-base-person': {
        'tag': 'c4-base w-28 h-25',
        'style': 'shape=mxgraph.c4.person2',
    },
    'c4-person': {
        'tag': 'c4-base-person',
        'style': 'fillColor=#083F75;strokeColor=#06315C;fontColor=#ffffff',
    },
    'c4-ext-person': {
        'tag': 'c4-base-person',
        'style': 'fillColor=#6C6477;strokeColor=#4D4D4D;fontColor=#ffffff',
    },
    'c4-base-arcs': {
        'style': 'arcSize=15;absoluteArcSize=1',
    },
    'c4-base-node': {
        'tag': 'c4-base c4-base-arcs w-40 h-20',
        'style': 'rounded=1;labelBackgroundColor=none;fontColor=#ffffff',
    },
    'c4-system': {
        'tag': 'c4-base-node',
        'style': 'fillColor=#1061B0;strokeColor=#0D5091',
    },
    'c4-ext-system': {
        'tag': 'c4-base-node',
        'style': 'fillColor=#8C8496;strokeColor=#736782',
    },
    'c4-container': {
        'tag': 'c4-base-node',
        'style': 'fillColor=#23A2D9;strokeColor=#0E7DAD',
    },
    'c4-storage': {
        'tag': 'c4-container h-24',
        'style': 'shape=cylinder3;size=10;boundedLbl=1',
    },
    'c4-pod': {
        'tag': 'c4-container h-32',
        'style': 'shape=hexagon;perimeter=hexagonPerimeter;arcSize=15',
    },
    'c4-bus': {
        'tag': 'c4-container',
        'style': 'shape=cylinder3;direction=south;size=10;boundedLbl=1',
    },
    'c4-boundary': {
        'tag': 'c4-base c4-base-arcs p-12 gap-40',
        'style': 'rounded=1;dashed=1;fillColor=none;strokeColor=#666666;fontColor=#333333;labelBackgroundColor=none;align=left;verticalAlign=bottom;labelBorderColor=none;spacingLeft=4;spacingBottom=0;dashPattern=6 4;labelPadding=0;arcSize=10',
    },
    'c4-component': {
        'tag': 'c4-base-node',
        'style': 'fillColor=#63BEF2;strokeColor=#2086C9;arcSize=7',
    },
    'c4-edge': {
        'tag': 'edge-default c4-base',
        'style': 'fontColor=#404040;strokeColor=#828282',
    },
}

tagmap.update(TAGS)

Person = root['c4-person']
ExtPerson = root['c4-ext-person']
System = root['c4-system']
ExtSystem = root['c4-ext-system']
Container = root['c4-container']
Component = root['c4-component']
Boundary = root['c4-boundary']
Storage = root['c4-storage']
Pod = root['c4-pod']
Bus = root['c4-bus']
