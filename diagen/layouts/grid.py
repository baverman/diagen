from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..nodes import Node


@dataclass
class Cell:
    pos: tuple[int, int]
    size: tuple[int, int]
    node: 'Node'


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

        max_cols = node.props.grid_columns
        cells = []
        rows: dict[int, list[Cell]] = {}
        cols: dict[int, list[Cell]] = {}
        r = c = 0
        for it in node.children:
            cs, ce = it.props.grid_col if it.props.grid_col else (c + 1, c + 2)
            if ce <= 0:
                ce = (max_cols or 0) + 1 + ce
            ce = max(cs + 1, min(ce, (max_cols or 0) + 1))
            if cs < (c + 1):
                r += 1

            cell = Cell((cs - 1, r), (ce - cs, 1), it)
            cells.append(cell)
            for cc in range(cell.size[0]):
                cols.setdefault(cell.pos[0] + cc, []).append(cell)
            for rr in range(cell.size[1]):
                rows.setdefault(cell.pos[1] + rr, []).append(cell)

            c = ce - 1
            if max_cols is not None and c >= max_cols:
                c = 0
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
        c = node.position if node.props.virtual else (0, 0)
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
