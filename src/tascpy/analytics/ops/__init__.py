"""ドメイン固有の操作クラス (`collection.ops`)

汎用の操作は `tascpy.core.CoreOps` にあります。新しいドメインは CoreOps を継承したクラスを作り、
コレクション側の `ops` プロパティで返します。
"""

from .coordinate import CoordinateOps
from .load_displacement import LoadDisplacementOps
from .strain import StrainOps

__all__ = ["LoadDisplacementOps", "CoordinateOps", "StrainOps"]
