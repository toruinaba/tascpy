"""メソッドチェーン用の操作クラス (`collection.ops`)

ドメイン固有の操作を追加するには、対応する Ops クラスにメソッドを定義します。
新しいドメインは CoreOps を継承したクラスを作り、コレクション側の `ops` プロパティで返します。
"""

from .coordinate import CoordinateOps
from .core import CoreOps
from .list import OpsList
from .load_displacement import LoadDisplacementOps
from .strain import StrainOps

__all__ = ["CoreOps", "LoadDisplacementOps", "CoordinateOps", "StrainOps", "OpsList"]
