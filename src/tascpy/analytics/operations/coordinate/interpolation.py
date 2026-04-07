"""座標ドメインの補間関数

このモジュールには、座標ベースのデータ補間に関する関数が含まれています。
"""

from typing import Dict, Optional, List, Any, Tuple, Union
import numpy as np
from tascpy.domains.coordinate import CoordinateCollection
from tascpy.core.column import Column
from ...operations.registry import operation
from ...operations.validation import requires_domain, requires_coordinates
from ...functional.coordinate.interpolation import (
    compute_point_interpolation_values,
    compute_grid_interpolation_values,
    compute_spatial_interpolation_values,
)


def _build_source_data(collection: CoordinateCollection, target_columns: Optional[List[str]]) -> Tuple[List[Dict], List[str]]:
    """座標付き列からsource_dataリストとvalid_targetsを構築するヘルパー。"""
    if target_columns is None:
        target_columns = collection.get_columns_with_coordinates()
    source_data = []
    valid_targets = []
    for col_name in target_columns:
        values = collection[col_name].values
        if len(values) == 0:
            continue
        if isinstance(values[0], (int, float, np.number)):
            value = np.nanmean([v for v in values if v is not None and not np.isnan(v)])
        else:
            value = values[0]
        col_x, col_y, col_z = collection.get_column_coordinates(col_name)
        if col_x is None or col_y is None:
            continue
        source_data.append({"point": {"x": col_x, "y": col_y, "z": col_z}, "value": value, "col_name": col_name})
        valid_targets.append(col_name)
    return source_data, valid_targets


@operation(domain="coordinate", shared_with=["strain"])
@requires_coordinates()
@requires_domain(["coordinate", "strain"])
def interpolate_at_point(
    collection: CoordinateCollection,
    x: float,
    y: float,
    z: Optional[float] = None,
    target_columns: Optional[List[str]] = None,
    method: str = "inverse_distance",
    power: float = 2.0,
    result_prefix: str = "interp_",
) -> CoordinateCollection:
    """座標点での値を補間して計算します。

    指定された座標点 (x, y, z) において、既存の座標値に基づいて値を補間します。
    補間方法として逆距離加重法、最近傍法、線形補間法を選択できます。

    Args:
        collection: 座標コレクション
        x: 補間する X 座標
        y: 補間する Y 座標
        z: 補間する Z 座標 (2D の場合は None)
        target_columns: 補間対象の列名リスト (None の場合は座標を持つ全列)
        method: 補間方法 (\"inverse_distance\", \"nearest\", \"linear\")
        power: 逆距離加重法のパワーパラメータ
        result_prefix: 結果列の接頭辞

    Returns:
        CoordinateCollection: 補間結果を含むコレクション

    Examples:
        >>> interp_col = col.ops.interpolate_at_point(
        ...     x=10.0, y=20.0, method="inverse_distance"
        ... )
    """
    source_data, valid_targets = _build_source_data(collection, target_columns)
    if not source_data:
        raise ValueError("補間に使用できる座標付き列がありません")

    is_3d = z is not None
    # filter source_data if 3D: need z in source
    if is_3d:
        source_data = [s for s in source_data if s["point"]["z"] is not None]
        valid_targets = [s["col_name"] for s in source_data]

    interp_values = compute_point_interpolation_values(source_data, x, y, z, method, power)

    result = collection.clone()
    for i, col_name in enumerate(valid_targets):
        result_col_name = f"{result_prefix}{col_name}"
        result.columns[result_col_name] = Column(
            ch=None,
            name=result_col_name,
            unit=collection[col_name].unit if hasattr(collection[col_name], "unit") else None,
            values=[interp_values[i]] * len(collection.step),
            metadata={
                "description": f"Interpolated value at ({x}, {y}{', ' + str(z) if is_3d else ''})",
                "interpolation": {
                    "method": method,
                    "power": power if method == "inverse_distance" else None,
                    "target": {"x": x, "y": y, "z": z if is_3d else None},
                },
            },
        )
    return result


# エイリアス
interp_point = interpolate_at_point


@operation(domain="coordinate", shared_with=["strain"])
@requires_coordinates()
@requires_domain(["coordinate", "strain"])
def interpolate_grid(
    collection: CoordinateCollection,
    x_range: Tuple[float, float],
    y_range: Tuple[float, float],
    grid_size: Tuple[int, int] = (10, 10),
    target_column: Optional[str] = None,
    method: str = "inverse_distance",
    power: float = 2.0,
    result_prefix: str = "grid_",
) -> CoordinateCollection:
    """指定した領域のグリッド上で値を補間します。

    指定された x-y 平面上の矩形領域をグリッドに分割し、各グリッド点での値を補間します。
    補間結果はメタデータと結果列に保存されます。

    Args:
        collection: 座標コレクション
        x_range: X 座標の範囲 (min, max)
        y_range: Y 座標の範囲 (min, max)
        grid_size: グリッドサイズ (nx, ny) (デフォルト: (10, 10))
        target_column: 補間対象の列名
        method: 補間方法 (\"inverse_distance\", \"nearest\", \"linear\")
        power: 逆距離加重法のパワーパラメータ
        result_prefix: 結果列の接頭辞

    Returns:
        CoordinateCollection: グリッド補間結果を含むコレクション

    Examples:
        >>> grid_col = col.ops.interpolate_grid(
        ...     x_range=(0, 100), y_range=(0, 100),
        ...     grid_size=(20, 20), target_column="Temperature"
        ... )
    """
    if target_column is None:
        coord_columns = collection.get_columns_with_coordinates()
        if not coord_columns:
            raise ValueError("補間に使用できる座標付き列がありません")
        target_column = coord_columns[0]
    if target_column not in collection.columns:
        raise ValueError(f"列 '{target_column}' が見つかりません")

    values = collection[target_column].values
    if len(values) == 0:
        raise ValueError(f"列 '{target_column}' に値がありません")

    if isinstance(values[0], (int, float, np.number)):
        value = np.nanmean([v for v in values if v is not None and not np.isnan(v)])
    else:
        value = values[0]

    col_x, col_y, col_z = collection.get_column_coordinates(target_column)
    if col_x is None or col_y is None:
        raise ValueError(f"列 '{target_column}' に座標情報がありません")

    source_point = {
        "point": {"x": col_x, "y": col_y, "z": col_z},
        "value": value,
        "col_name": target_column,
    }

    nx, ny = grid_size
    x_grid = np.linspace(x_range[0], x_range[1], nx)
    y_grid = np.linspace(y_range[0], y_range[1], ny)

    grid_values = compute_grid_interpolation_values(source_point, x_grid, y_grid, method, power)

    result = collection.clone()
    if "analysis" not in result.metadata:
        result.metadata["analysis"] = {}

    result.metadata["analysis"]["grid_interpolation"] = {
        "x_range": x_range,
        "y_range": y_range,
        "grid_size": grid_size,
        "method": method,
        "target_column": target_column,
    }

    grid_str = np.array2string(grid_values, precision=4, suppress_small=True)
    result_col_name = f"{result_prefix}{target_column}_grid"
    result.columns[result_col_name] = Column(
        ch=None,
        name=result_col_name,
        unit=None,
        values=[grid_str] * len(collection.step),
        metadata={
            "description": f"Grid interpolation of {target_column}",
            "grid": {
                "x_min": float(x_range[0]),
                "x_max": float(x_range[1]),
                "y_min": float(y_range[0]),
                "y_max": float(y_range[1]),
                "nx": nx,
                "ny": ny,
            },
        },
    )
    return result


# エイリアス
interp_grid = interpolate_grid


@operation(domain="coordinate", shared_with=["strain"])
@requires_coordinates()
@requires_domain(["coordinate", "strain"])
def spatial_interpolation_to_points(
    collection: CoordinateCollection,
    source_columns: Optional[List[str]] = None,
    target_columns: Optional[List[str]] = None,
    method: str = "inverse_distance",
    power: float = 2.0,
    result_prefix: str = "interp_",
) -> CoordinateCollection:
    """ソース列からターゲット列の座標位置に値を補間します。

    指定されたソース列の座標位置の値を使用して、ターゲット列の座標位置における
    値を補間します。複数のソースからの補間値の平均が計算されます。

    Args:
        collection: 座標コレクション
        source_columns: 補間ソースとなる列名リスト（None の場合は座標を持つ全列）
        target_columns: 補間先の座標を持つ列名リスト
        method: 補間方法 (\"inverse_distance\", \"nearest\", \"linear\")
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
    columns_with_coords = collection.get_columns_with_coordinates()
    if source_columns is None:
        source_columns = columns_with_coords
    if target_columns is None:
        target_columns = [c for c in columns_with_coords if c not in source_columns]

    if not source_columns:
        raise ValueError("補間元の座標付き列がありません")
    if not target_columns:
        raise ValueError("補間先の座標付き列がありません")

    source_data = []
    for col_name in source_columns:
        values = collection[col_name].values
        if len(values) == 0:
            continue
        if isinstance(values[0], (int, float, np.number)):
            value = np.nanmean([v for v in values if v is not None and not np.isnan(v)])
        else:
            value = values[0]
        col_x, col_y, col_z = collection.get_column_coordinates(col_name)
        if col_x is None or col_y is None:
            continue
        source_data.append({"point": {"x": col_x, "y": col_y, "z": col_z}, "value": value, "col_name": col_name})

    is_3d_overall = all(d["point"]["z"] is not None for d in source_data) if source_data else False

    target_coords = []
    valid_targets = []
    for target_col in target_columns:
        target_x, target_y, target_z = collection.get_column_coordinates(target_col)
        if target_x is None or target_y is None:
            continue
        is_3d_tgt = target_z is not None and is_3d_overall
        target_coords.append({"x": target_x, "y": target_y, "z": target_z if is_3d_tgt else None})
        valid_targets.append((target_col, is_3d_tgt))

    results = compute_spatial_interpolation_values(source_data, target_coords, is_3d_overall, method, power)

    result = collection.clone()
    for i, (target_col, _) in enumerate(valid_targets):
        result_col_name = f"{result_prefix}{target_col}"
        result.columns[result_col_name] = Column(
            ch=None,
            name=result_col_name,
            unit=None,
            values=[results[i]] * len(collection.step),
            metadata={
                "description": f"Interpolated value at {target_col} position",
                "interpolation": {
                    "method": method,
                    "power": power if method == "inverse_distance" else None,
                    "source_columns": source_columns,
                    "target_column": target_col,
                },
            },
        )
    return result
