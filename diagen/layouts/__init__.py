from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..nodes import Node

NodePosition = tuple[float, float]
PositionInfo = dict[Optional['Node'], NodePosition]
