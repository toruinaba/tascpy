"""tascpy.core - データモデル、汎用の操作、ファイル入出力、描画

描画（`tascpy.core.plot`）は matplotlib を読み込むため、ここでは import せず `coll.plot` で初めて読み込みます。
"""

from .column import KEEP, Column, ColumnMeta
from .collection import INDEX_COLUMNS, ColumnCollection, concat
from .ops import CoreOps
from .ops_list import OpsList
from .result import AnalysisResult, GridResult, PointResult, ScalarResult, XYSeriesResult
from .row import Row

__all__ = [
    "ColumnCollection", "Column", "ColumnMeta", "Row", "KEEP", "INDEX_COLUMNS", "concat",
    "CoreOps", "OpsList",
    "AnalysisResult", "XYSeriesResult", "ScalarResult", "PointResult", "GridResult",
]
