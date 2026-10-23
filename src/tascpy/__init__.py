"""
tascpy - 実験データ処理のためのPythonライブラリ
"""

__version__ = "0.2.0"

try:
    from .visualization.config import configure_plotting

    configure_plotting()
except ImportError:
    pass

from .core import Column, ColumnCollection, ColumnMeta
from .domains import CoordinateCollection, LoadDisplacementCollection, StrainCollection
from .io import load

__all__ = [
    "ColumnCollection", "Column", "ColumnMeta",
    "LoadDisplacementCollection", "CoordinateCollection", "StrainCollection",
    "load",
]
