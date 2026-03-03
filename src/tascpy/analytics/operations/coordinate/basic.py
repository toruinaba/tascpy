"""座標ドメインの基本的な操作関数

このモジュールには、座標情報を扱うための宣言的な操作が含まれています。
"""

from typing import Dict, Optional, List, Any, Tuple
import numpy as np

from ...operations.registry import register_functional
from tascpy.domains.coordinate import CoordinateCollection
from tascpy.core.column import Column
from ...operations.validation import requires_domain, requires_coordinates
from ...functional.coordinate.basic import extract_coordinates as _extract_coordinates_pure
from .abstraction import resolve_extract_coordinates

extract_coordinates = register_functional(
    _extract_coordinates_pure,
    domain="coordinate",
    name="extract_coordinates",
    shared_with=["strain"],
    extra_decorators=[
        resolve_extract_coordinates(),
        requires_coordinates(),
        requires_domain(["coordinate", "strain"]),
    ]
)
extract_coordinates.__doc__ = """各列の座標値を新しい列としてコレクションに追加します

    座標情報が設定されている列の x、y、z 座標値を取得し、それぞれを独立した列として
    コレクションに追加します。新しい列名には指定された接頭辞が付与されます。

    Args:
        collection: 座標コレクション
        result_prefix: 結果列の接頭辞 (デフォルト: "coord_")

    Returns:
        CoordinateCollection: 座標列を追加したコレクション
        
    Examples:
        >>> col = col.ops.extract_coordinates(result_prefix="coord_")
        >>> x_coords = col["coord_x"].values
"""
