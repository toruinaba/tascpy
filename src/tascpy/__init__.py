"""
tascpy - 実験データ処理のためのPythonライブラリ
"""

from importlib import import_module
from typing import TYPE_CHECKING, Any

__version__ = "0.7.1"

# `import tascpy.numeric` で polars / matplotlib を読み込まないよう、公開名は初回アクセス時に import する
_EXPORTS = {
    "ColumnCollection": "tascpy.core",
    "Column": "tascpy.core",
    "ColumnMeta": "tascpy.core",
    "LoadDisplacementCollection": "tascpy.domains",
    "CoordinateCollection": "tascpy.domains",
    "StrainCollection": "tascpy.domains",
    "as_load_displacement": "tascpy.domains",
    "as_coordinate": "tascpy.domains",
    "as_strain": "tascpy.domains",
    "load": "tascpy.core.io",
    "load_parquet": "tascpy.core.io",
}

if TYPE_CHECKING:
    from .core import Column, ColumnCollection, ColumnMeta
    from .core.io import load, load_parquet
    from .domains import (
        CoordinateCollection,
        LoadDisplacementCollection,
        StrainCollection,
        as_coordinate,
        as_load_displacement,
        as_strain,
    )

__all__ = [
    "ColumnCollection", "Column", "ColumnMeta",
    "LoadDisplacementCollection", "CoordinateCollection", "StrainCollection",
    "as_load_displacement", "as_coordinate", "as_strain",
    "load", "load_parquet",
]


def __getattr__(name: str) -> Any:
    if name not in _EXPORTS:
        raise AttributeError(f"module 'tascpy' has no attribute '{name}'")
    # 組み込みドメインを登録しておく（load_parquet がドメインのコレクションを復元できるように）
    import_module("tascpy.domains")
    value = getattr(import_module(_EXPORTS[name]), name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted([*globals(), *_EXPORTS])
