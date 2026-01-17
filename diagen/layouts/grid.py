from dataclasses import dataclass, replace
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


@dataclass
class SubGrid:
    direction: int
    max_size: int | None


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


CellsResult = tuple[list[Cell], tuple[list[float], list[float]]]


class GridLayout:
    @staticmethod
    def size(node: 'Node', axis: int) -> float:
        if node.props.subgrid:
            parent: Node = node._parent_grid  # type: ignore[attr-defined]
            cell: Cell = node._grid_subgrid_cell  # type: ignore[attr-defined]
            csize: tuple[list[float], list[float]]
            _, csize = parent._grid_cells  # type: ignore[attr-defined]
            g = parent.props.gap
            p = node.props.padding
            s = csize[axis][cell.pos[axis]]
            return (
                p[axis] + p[axis + 2] + csize[axis][cell.pos[axis] + cell.size[axis]] - s - g[axis]
            )
        else:
            _, csize = GridLayout.cells(node)
            p = node.props.padding
            g = node.props.gap
            return csize[axis][-1] + p[axis + 2] - g[axis]

    @staticmethod
    def cells(node: 'Node', subgrid: SubGrid | None = None) -> CellsResult:
        try:
            return node._grid_cells  # type: ignore[no-any-return,attr-defined]
        except AttributeError:
            pass

        if subgrid:
            d = subgrid.direction
            o = [1, 0][d]
            max_size = subgrid.max_size
        else:
            d = node.props.direction
            o = [1, 0][d]
            max_size = node.props.grid_size[d]

        p = node.props.padding
        result: CellsResult = (cells := [], (ccol := [p[0]], crow := [p[1]]))

        imax_size = 0
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
            opos = dtup2(d, cs - 1, rs - 1)
            if it.props.subgrid:
                main_span = ce - cs > 1
                alt_span = re - rs > 1
                sg_dir = it.props.direction
                sg_max_size = None
                if main_span and alt_span:
                    if sg_dir == d:
                        sg_max_size = ce - cs
                    else:
                        sg_max_size = re - rs
                elif main_span:
                    sg_dir = d
                    sg_max_size = ce - cs
                elif alt_span:
                    sg_dir = o
                    sg_max_size = re - rs
                subcells = GridLayout.cells(it, SubGrid(sg_dir, sg_max_size))[0]
                batch = []
                gr = re
                for sc in subcells:
                    npos = (opos[0] + sc.pos[0], opos[1] + sc.pos[1])
                    newcell = replace(sc, pos=npos)
                    c = max(c, newcell.pos[d] + newcell.size[d] + 1)
                    gr = max(gr, newcell.pos[o] + newcell.size[o] + 1)
                    batch.append(newcell)
                it._grid_subgrid_cell = Cell(opos, dtup2(d, c - cs, gr - rs), it)  # type: ignore[attr-defined]
                it._parent_grid = node  # type: ignore[attr-defined]
            else:
                batch = [Cell(opos, dtup2(d, ce - cs, re - rs), it)]

            for cell in batch:
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

        g = node.props.gap
        for h in row_heights:
            crow.append(crow[-1] + h + g[1])

        for w in col_widths:
            ccol.append(ccol[-1] + w + g[0])

        node._grid_cells = result  # type: ignore[attr-defined]
        return result

    @staticmethod
    def arrange(node: 'Node') -> None:
        if node.props.subgrid:
            parent: Node = node._parent_grid  # type: ignore[attr-defined]
            cell: Cell = node._grid_subgrid_cell  # type: ignore[attr-defined]
            csize: tuple[list[float], list[float]]
            _, csize = parent._grid_cells  # type: ignore[attr-defined]
            p = node.props.padding
            pos = csize[0][cell.pos[0]], csize[1][cell.pos[1]]
            node.position = np = pos[0] - p[0], pos[1] - p[1]
            cells, _ = GridLayout.cells(node)
            if not node.props.virtual:
                for it in cells:
                    ip = it.node.position
                    it.node.position = (ip[0] - np[0], ip[1] - np[1])
            return

        cells, (ccol, crow) = GridLayout.cells(node)
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
