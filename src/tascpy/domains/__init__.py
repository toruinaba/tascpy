"""tascpy.domains - ドメイン（荷重-変位・座標・ひずみ）

各ドメインは collection（設定）/ ops（操作）/ plotter・draw（描画）を持つパッケージです。
`as_*` は `col.ops.end_as(as_*, ...)` に渡す変換関数です。
"""

from .coordinate import CoordinateCollection, CoordinateOps, as_coordinate
from .load_displacement import LoadDisplacementCollection, LoadDisplacementOps, as_load_displacement
from .strain import StrainCollection, StrainOps, as_strain

__all__ = [
    "LoadDisplacementCollection", "CoordinateCollection", "StrainCollection",
    "LoadDisplacementOps", "CoordinateOps", "StrainOps",
    "as_load_displacement", "as_coordinate", "as_strain",
]
