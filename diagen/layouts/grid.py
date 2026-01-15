from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..props import Span
from ..utils import dtup2

if TYPE_CHECKING:
    from ..nodes import Node


@dataclass
class Cell:
    pos: tuple[int, int]
    size: tuple[int, int]
    node: 'Node'


def next_span(current: int, span: Span, max_size: int | None = None) -> tuple[int, int]:
    start = span.start
    if span.rel_start:
        start += current

    end = span.end
    if span.rel_end:
        end += start
    elif max_size and end <= 0:
        end += max_size + 1

    end = max(end, start + 1)
    return start, end


class GridLayout:
    @staticmethod
    def size(node: 'Node', axis: int) -> float:
        _, crow, ccol = GridLayout.cells(node)

        if axis == 0:
            dim = ccol[-1]
        else:
            dim = crow[-1]

        p = node.props.padding
        g = node.props.gap
        return dim + p[axis + 2] - g[axis]

    @staticmethod
    def cells(node: 'Node') -> tuple[list[Cell], list[float], list[float]]:
        try:
            return node._grid_cells  # type: ignore[no-any-return,attr-defined]
        except AttributeError:
            pass

        d = node.props.direction
        o = [1, 0][d]

        max_size = node.props.grid_size[d]
        imax_size = 0
        cells = []
        rows: dict[int, list[Cell]] = {}
        cols: dict[int, list[Cell]] = {}
        rc = (cols, rows)
        r = c = 1  # rows and cols are 1-base indexed
        for it in node.children:
            cs, ce = next_span(c, it.props.grid_cell[d], max_size or imax_size)
            imax_size = max(imax_size, ce - 1)
            if cs < c:
                r += 1
            c = ce

            rs, re = next_span(r, it.props.grid_cell[o])
            r = rs

            # for cells we convert 1-base into 0-base as more convenient to handle
            cell = Cell(dtup2(d, cs - 1, rs - 1), dtup2(d, ce - cs, re - rs), it)
            cells.append(cell)
            for cc in range(cell.size[d]):
                rc[d].setdefault(cell.pos[d] + cc, []).append(cell)
            for rr in range(cell.size[o]):
                rc[o].setdefault(cell.pos[o] + rr, []).append(cell)

            if max_size is not None and c > max_size:
                c = 1
                r += 1

        col_count = max(it.pos[0] + it.size[0] for it in cells)
        row_count = max(it.pos[1] + it.size[1] for it in cells)
        row_heights = [
            max((it.node.size[1] / it.size[1] for it in rows.get(i, [])), default=0)
            for i in range(row_count)
        ]
        col_widths = [
            max((it.node.size[0] / it.size[0] for it in cols.get(j, [])), default=0)
            for j in range(col_count)
        ]

        p = node.props.padding

        g = node.props.gap
        crow = [p[1]]
        for h in row_heights:
            crow.append(crow[-1] + h + g[1])

        ccol = [p[0]]
        for w in col_widths:
            ccol.append(ccol[-1] + w + g[0])

        result = cells, crow, ccol
        node._grid_cells = result  # type: ignore[attr-defined]
        return result

    @staticmethod
    def arrange(node: 'Node') -> None:
        cells, crow, ccol = GridLayout.cells(node)
        c = node.origin
        g = node.props.gap

        for it in cells:
            align = it.node.align(node)
            s = ccol[it.pos[0]], crow[it.pos[1]]
            bw = ccol[it.pos[0] + it.size[0]] - s[0] - g[0]
            bh = crow[it.pos[1] + it.size[1]] - s[1] - g[1]
            pos = (
                c[0] + s[0] + (bw - it.node.size[0]) / 2 * (align[0] + 1),
                c[1] + s[1] + (bh - it.node.size[1]) / 2 * (align[1] + 1),
            )
            it.node.position = pos
