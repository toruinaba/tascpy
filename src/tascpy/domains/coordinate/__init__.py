"""tascpy.domains.coordinate - 座標ドメイン"""

from .collection import CoordinateCollection, as_coordinate
from .ops import CoordinateOps

__all__ = ["CoordinateCollection", "CoordinateOps", "as_coordinate"]
