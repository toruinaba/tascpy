"""座標ドメインの補間関数

このモジュールには、座標ベースのデータ補間に関する関数が含まれています。
"""

from typing import Dict, Optional, List, Any, Tuple, Union
import numpy as np
from ...operations.registry import register_functional
from tascpy.domains.coordinate import CoordinateCollection
from ...operations.validation import requires_domain, requires_coordinates
from ...functional.coordinate.interpolation import (
    compute_point_interpolation_values,
    compute_grid_interpolation_values,
    compute_spatial_interpolation_values,
)
from .abstraction import (
    resolve_point_interpolation,
    resolve_grid_interpolation,
    resolve_spatial_interpolation,
)


interpolate_at_point = register_functional(
    compute_point_interpolation_values,
    domain="coordinate",
    name="interpolate_at_point",
    shared_with=["strain"],
    extra_decorators=[
        resolve_point_interpolation(),
        requires_coordinates(),
        requires_domain(["coordinate", "strain"]),
    ]
)
"""座標点での値を補間して計算します

    指定された座標点 (x, y, z) において、既存の座標値に基づいて値を補間します。
    補間方法として逆距離加重法、最近傍法、線形補間法を選択できます。

    Args:
        collection: 座標コレクション
        x: 補間する X 座標
        y: 補間する Y 座標
        z: 補間する Z 座標 (2D の場合は None)
        target_columns: 補間対象の列名リスト (None の場合は座標を持つ全列)
        method: 補間方法 ("inverse_distance", "nearest", "linear")
        power: 逆距離加重法のパワーパラメータ
        result_prefix: 結果列の接頭辞

    Returns:
        CoordinateCollection: 補間結果を含むコレクション
        
    Examples:
        >>> interp_col = col.ops.interpolate_at_point(
        ...     x=10.0, y=20.0, method="inverse_distance"
        ... )
"""
interpolate_at_point.__doc__ = """座標点での値を補間して計算します

    指定された座標点 (x, y, z) において、既存の座標値に基づいて値を補間します。
    補間方法として逆距離加重法、最近傍法、線形補間法を選択できます。

    Args:
        collection: 座標コレクション
        x: 補間する X 座標
        y: 補間する Y 座標
        z: 補間する Z 座標 (2D の場合は None)
        target_columns: 補間対象の列名リスト (None の場合は座標を持つ全列)
        method: 補間方法 ("inverse_distance", "nearest", "linear")
        power: 逆距離加重法のパワーパラメータ
        result_prefix: 結果列の接頭辞

    Returns:
        CoordinateCollection: 補間結果を含むコレクション
        
    Examples:
        >>> interp_col = col.ops.interpolate_at_point(
        ...     x=10.0, y=20.0, method="inverse_distance"
        ... )
"""

interpolate_grid = register_functional(
    compute_grid_interpolation_values,
    domain="coordinate",
    name="interpolate_grid",
    shared_with=["strain"],
    extra_decorators=[
        resolve_grid_interpolation(),
        requires_coordinates(),
        requires_domain(["coordinate", "strain"]),
    ]
)
"""指定した領域のグリッド上で値を補間します

    指定された x-y 平面上の矩形領域をグリッドに分割し、各グリッド点での値を補間します。
    補間結果はメタデータと結果列に保存されます。

    Args:
        collection: 座標コレクション
        x_range: X 座標の範囲 (min, max)
        y_range: Y 座標の範囲 (min, max)
        grid_size: グリッドサイズ (nx, ny) (デフォルト: (10, 10))
        target_column: 補間対象の列名
        method: 補間方法 ("inverse_distance", "nearest", "linear")
        power: 逆距離加重法のパワーパラメータ
        result_prefix: 結果列の接頭辞

    Returns:
        CoordinateCollection: グリッド補間結果を含むコレクション
        
    Examples:
        >>> grid_col = col.ops.interpolate_grid(x_range=(0, 100), y_range=(0, 100), grid_size=(20, 20), target_column="Temperature")
"""
interpolate_grid.__doc__ = """指定した領域のグリッド上で値を補間します

    指定された x-y 平面上の矩形領域をグリッドに分割し、各グリッド点での値を補間します。
    補間結果はメタデータと結果列に保存されます。

    Args:
        collection: 座標コレクション
        x_range: X 座標の範囲 (min, max)
        y_range: Y 座標の範囲 (min, max)
        grid_size: グリッドサイズ (nx, ny) (デフォルト: (10, 10))
        target_column: 補間対象の列名
        method: 補間方法 ("inverse_distance", "nearest", "linear")
        power: 逆距離加重法のパワーパラメータ
        result_prefix: 結果列の接頭辞

    Returns:
        CoordinateCollection: グリッド補間結果を含むコレクション
        
    Examples:
        >>> grid_col = col.ops.interpolate_grid(x_range=(0, 100), y_range=(0, 100), grid_size=(20, 20), target_column="Temperature")
"""

spatial_interpolation_to_points = register_functional(
    compute_spatial_interpolation_values,
    domain="coordinate",
    name="spatial_interpolation_to_points",
    shared_with=["strain"],
    extra_decorators=[
        resolve_spatial_interpolation(),
        requires_coordinates(),
        requires_domain(["coordinate", "strain"]),
    ]
)
"""ソース列からターゲット列の座標位置に値を補間します

    指定されたソース列の座標位置の値を使用して、ターゲット列の座標位置における
    値を補間します。複数のソースからの補間値の平均が計算されます。

    Args:
        collection: 座標コレクション
        source_columns: 補間ソースとなる列名リスト（None の場合は座標を持つ全列）
        target_columns: 補間先の座標を持つ列名リスト
        method: 補間方法 ("inverse_distance", "nearest", "linear")
        power: 逆距離加重法のパワーパラメータ
        result_prefix: 結果列の接頭辞

    Returns:
        CoordinateCollection: 補間結果を含むコレクション
        
    Examples:
        >>> mapped_col = col.ops.spatial_interpolation_to_points(
        ...     source_columns=["Sensor1", "Sensor2"],
        ...     target_columns=["NodeA", "NodeB"],
        ...     method="inverse_distance"
        ... )
"""
spatial_interpolation_to_points.__doc__ = """ソース列からターゲット列の座標位置に値を補間します

    指定されたソース列の座標位置の値を使用して、ターゲット列の座標位置における
    値を補間します。複数のソースからの補間値の平均が計算されます。

    Args:
        collection: 座標コレクション
        source_columns: 補間ソースとなる列名リスト（None の場合は座標を持つ全列）
        target_columns: 補間先の座標を持つ列名リスト
        method: 補間方法 ("inverse_distance", "nearest", "linear")
        power: 逆距離加重法のパワーパラメータ
        result_prefix: 結果列の接頭辞

    Returns:
        CoordinateCollection: 補間結果を含むコレクション
        
    Examples:
        >>> mapped_col = col.ops.spatial_interpolation_to_points(
        ...     source_columns=["Sensor1", "Sensor2"],
        ...     target_columns=["NodeA", "NodeB"],
        ...     method="inverse_distance"
        ... )
"""

interp_point = register_functional(
    compute_point_interpolation_values,
    domain="coordinate",
    name="interp_point",
    shared_with=["strain"],
    extra_decorators=[
        resolve_point_interpolation(),
        requires_coordinates(),
        requires_domain(["coordinate", "strain"]),
    ]
)
interp_point.__doc__ = "interpolate_at_point のエイリアス"

interp_grid = register_functional(
    compute_grid_interpolation_values,
    domain="coordinate",
    name="interp_grid",
    shared_with=["strain"],
    extra_decorators=[
        resolve_grid_interpolation(),
        requires_coordinates(),
        requires_domain(["coordinate", "strain"]),
    ]
)
interp_grid.__doc__ = "interpolate_grid のエイリアス"
