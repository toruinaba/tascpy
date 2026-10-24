"""トップレベルの遅延 export が型付きで解決されることの検査（実行はしない）"""

from typing import assert_type

import tascpy
from tascpy.core import ColumnCollection
from tascpy.domains import LoadDisplacementCollection

assert_type(tascpy.ColumnCollection, type[ColumnCollection])
assert_type(tascpy.LoadDisplacementCollection, type[LoadDisplacementCollection])
assert_type(tascpy.load("data.txt"), ColumnCollection)
assert_type(tascpy.ColumnCollection({"A": [1.0]}).ops.add("A", 1.0).end(), ColumnCollection)
