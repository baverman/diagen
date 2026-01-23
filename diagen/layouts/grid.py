from dataclasses import dataclass
from typing import TYPE_CHECKING, overload

from ..props import Span
from ..utils import dtup2
from . import PositionInfo

if TYPE_CHECKING:
    from ..nodes import Node


@dataclass
class Cell:
    # 0-base indexes
    start: tuple[int, int]
    end: tuple[int, int]
    node: 'Node'

    @property
    def size(self) -> tuple[int, int]:
        s = self.start
        e = self.end
        return e[0] - s[0], e[1] - s[1]


@dataclass
class SubGrid:
    parent: 'Node'
    direction: int
    max_size: int | None
    origin: tuple[int, int]
    rc: tuple[dict[int, list[Cell]], dict[int, list[Cell]]]


@dataclass
class GridCells:
    cells: list[Cell]
    dimensions: tuple[list[float], list[float]]


@dataclass
class SubGridCells:
    parent: 'Node'
    cell: Cell
    cells: list[Cell]


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


def subgrid_cells(node: 'Node') -> SubGridCells | None:
    return getattr(node, '_subgrid_cells', None)


class GridLayout:
    @staticmethod
    def size(node: 'Node', axis: int) -> float:
        if sg := subgrid_cells(node):
            gc = GridLayout.cells(sg.parent)
            csize = gc.dimensions
            cell = sg.cell
            g = sg.parent.props.gap
            p = node.props.padding
            s = csize[axis][cell.start[axis]]
            return p[axis] + p[axis + 2] + csize[axis][cell.end[axis]] - s - g[axis]
        else:
            csize = GridLayout.cells(node).dimensions
            p = node.props.padding
            g = node.props.gap
            return p[axis] + csize[axis][-1] + p[axis + 2] - g[axis]

    @overload
    @staticmethod
    def cells(node: 'Node', subgrid: SubGrid) -> SubGridCells: ...

    @overload
    @staticmethod
    def cells(node: 'Node') -> GridCells: ...

    @staticmethod
    def cells(node: 'Node', subgrid: SubGrid | None = None) -> SubGridCells | GridCells:
        try:
            return node._grid_cells  # type: ignore[no-any-return,attr-defined]
        except AttributeError:
            pass

        if subgrid:
            d = subgrid.direction
            o = [1, 0][d]
            max_size = subgrid.max_size
            grid_origin = subgrid.origin
            rc = subgrid.rc
            parent = subgrid.parent
        else:
            d = node.props.direction
            o = [1, 0][d]
            max_size = node.props.grid_size[d]
            grid_origin = 0, 0
            rc = ({}, {})
            parent = node

        cells = []
        imax_size = 0
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
            opos = dtup2(d, cs - 1 + grid_origin[d], rs - 1 + grid_origin[o])
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
                subcells = GridLayout.cells(it, SubGrid(parent, sg_dir, sg_max_size, opos, rc))
                cells.extend(subcells.cells)
                c = subcells.cell.end[d] + 1
            else:
                cell = Cell(opos, dtup2(d, ce - 1 + grid_origin[d], re - 1 + grid_origin[o]), it)
                cells.append(cell)
                for i in range(cell.start[d], cell.end[d]):
                    rc[d].setdefault(i, []).append(cell)
                for i in range(cell.start[o], cell.end[o]):
                    rc[o].setdefault(i, []).append(cell)

            if max_size is not None and c > max_size:
                c = 1
                r += 1

        if subgrid:
            max_x = max(it.end[0] for it in cells)
            max_y = max(it.end[1] for it in cells)
            cell = Cell(opos, (max_x, max_y), node)
            result = SubGridCells(parent, cell, cells)
            node._subgrid_cells = result  # type: ignore[attr-defined]
            return result

        cols, rows = rc
        col_count = max(it.end[0] for it in cells)
        row_count = max(it.end[1] for it in cells)
        row_heights = [
            max((it.node.size[1] / it.size[1] for it in rows.get(i, [])), default=0)
            for i in range(row_count)
        ]
        col_widths = [
            max((it.node.size[0] / it.size[0] for it in cols.get(j, [])), default=0)
            for j in range(col_count)
        ]

        crow = [0.0]
        g = node.props.gap
        for h in row_heights:
            crow.append(crow[-1] + h + g[1])

        ccol = [0.0]
        for w in col_widths:
            ccol.append(ccol[-1] + w + g[0])

        gresult = GridCells(cells, (ccol, crow))
        node._grid_cells = gresult  # type: ignore[attr-defined]
        return gresult

    @staticmethod
    def arrange(info: PositionInfo, node: 'Node') -> None:
        if sgc := subgrid_cells(node):
            gc = GridLayout.cells(sgc.parent)
            ccol, crow = gc.dimensions
            cell = sgc.cell

            origin = info[sgc.parent]
            p = node.props.padding

            info[node] = (
                origin[0] + ccol[cell.start[0]] - p[0],
                origin[1] + crow[cell.start[1]] - p[1],
            )
            return

        gc = GridLayout.cells(node)
        ccol, crow = gc.dimensions
        g = node.props.gap
        p = node.props.padding

        if node in info:
            origin = info[node]
        else:
            origin = info[node] = info[node.parent]

        for it in gc.cells:
            align = it.node.align(node)
            s = ccol[it.start[0]], crow[it.start[1]]
            bw = ccol[it.end[0]] - s[0] - g[0]
            bh = crow[it.end[1]] - s[1] - g[1]
            pos = (
                origin[0] + p[0] + s[0] + (bw - it.node.size[0]) / 2 * (align[0] + 1),
                origin[1] + p[1] + s[1] + (bh - it.node.size[1]) / 2 * (align[1] + 1),
            )
            info[it.node] = pos
