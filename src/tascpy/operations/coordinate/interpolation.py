"""座標ドメインの補間関数

このモジュールには、座標ベースのデータ補間に関する関数が含まれています。
"""

from typing import Dict, Optional, List, Any, Tuple, Union
import numpy as np
from ...operations.registry import operation
from ...domains.coordinate import CoordinateCollection
from ...core.column import Column


@operation(domain="coordinate")
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
    """座標点での値を補間して計算する

    Args:
        collection: 座標コレクション
        x: 補間するX座標
        y: 補間するY座標
        z: 補間するZ座標 (2Dの場合はNone)
        target_columns: 補間対象の列名リスト (Noneの場合は座標を持つ全列)
        method: 補間方法 ("inverse_distance", "nearest", "linear")
        power: 逆距離加重法のパワーパラメータ
        result_prefix: 結果列の接頭辞

    Returns:
        CoordinateCollection: 補間結果を含むコレクション
    """
    result = collection.clone()

    # 補間対象の列を決定
    if target_columns is None:
        target_columns = collection.get_columns_with_coordinates()

    if not target_columns:
        raise ValueError("補間に使用できる座標付き列がありません")

    # 2D補間か3D補間かを判断
    is_3d = z is not None

    # 補間方法の選択
    if method == "inverse_distance":
        interp_func = _inverse_distance_weighting
    elif method == "nearest":
        interp_func = _nearest_neighbor
    elif method == "linear":
        interp_func = _linear_interpolation
    else:
        raise ValueError(f"サポートされていない補間方法: {method}")

    # 座標値と値のペアを収集
    for col_name in target_columns:
        # 値の取得
        values = collection[col_name].values

        if not values:
            continue

        # 平均値または代表値
        if isinstance(values[0], (int, float, np.number)):
            # 数値の場合は平均値を使用
            value = np.nanmean([v for v in values if v is not None and not np.isnan(v)])
        else:
            # 非数値の場合は最初の値を使用
            value = values[0]

        # 座標情報の取得
        col_x, col_y, col_z = collection.get_column_coordinates(col_name)

        if col_x is None or col_y is None:
            continue  # 座標がない列はスキップ

        if is_3d and col_z is None:
            continue  # 3D補間の場合、Z座標がない列はスキップ

        # 代表点として座標と値のペアを収集
        point = {"x": col_x, "y": col_y, "z": col_z if is_3d else None}

        # 補間用のデータを収集
        point_data = {"point": point, "value": value, "col_name": col_name}

        # 結果の列名
        result_col_name = f"{result_prefix}{col_name}"

        # 補間関数を呼び出し
        interp_value = interp_func(point_data, x, y, z, power)

        # 結果を新しい列として追加
        result.columns[result_col_name] = Column(
            ch=None,
            name=result_col_name,
            unit=(
                collection[col_name].unit
                if hasattr(collection[col_name], "unit")
                else None
            ),
            values=[interp_value] * len(collection.step),
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


@operation(domain="coordinate")
def interpolate_grid(
    collection: CoordinateCollection,
    x_range: Tuple[float, float],
    y_range: Tuple[float, float],
    grid_size: Tuple[int, int] = (10, 10),
    target_column: str = None,
    method: str = "inverse_distance",
    power: float = 2.0,
    result_prefix: str = "grid_",
) -> CoordinateCollection:
    """指定した領域のグリッド上で値を補間する

    Args:
        collection: 座標コレクション
        x_range: X座標の範囲 (min, max)
        y_range: Y座標の範囲 (min, max)
        grid_size: グリッドサイズ (nx, ny)
        target_column: 補間対象の列名
        method: 補間方法
        power: 逆距離加重法のパワーパラメータ
        result_prefix: 結果列の接頭辞

    Returns:
        CoordinateCollection: グリッド補間結果を含むコレクション
    """
    result = collection.clone()

    # 補間対象の列を確認
    if target_column is None:
        coord_columns = collection.get_columns_with_coordinates()
        if not coord_columns:
            raise ValueError("補間に使用できる座標付き列がありません")
        target_column = coord_columns[0]

    if target_column not in collection.columns:
        raise ValueError(f"列 '{target_column}' が見つかりません")

    # 値の取得
    values = collection[target_column].values

    if not values:
        raise ValueError(f"列 '{target_column}' に値がありません")

    # 補間対象の値を計算
    if isinstance(values[0], (int, float, np.number)):
        # 数値の場合は平均値を使用
        value = np.nanmean([v for v in values if v is not None and not np.isnan(v)])
    else:
        # 非数値の場合は最初の値を使用
        value = values[0]

    # グリッドの生成
    nx, ny = grid_size
    x_grid = np.linspace(x_range[0], x_range[1], nx)
    y_grid = np.linspace(y_range[0], y_range[1], ny)

    # ターゲット列の座標取得
    col_x, col_y, col_z = collection.get_column_coordinates(target_column)

    if col_x is None or col_y is None:
        raise ValueError(f"列 '{target_column}' に座標情報がありません")

    # ソースデータの準備
    point_data = {
        "point": {"x": col_x, "y": col_y, "z": col_z},
        "value": value,
        "col_name": target_column,
    }

    # 補間方法の選択
    if method == "inverse_distance":
        interp_func = _inverse_distance_weighting
    elif method == "nearest":
        interp_func = _nearest_neighbor
    else:
        interp_func = _linear_interpolation

    # グリッド上で補間
    grid_values = np.zeros((ny, nx))
    for i, y in enumerate(y_grid):
        for j, x in enumerate(x_grid):
            grid_values[i, j] = interp_func(point_data, x, y, None, power)

    # グリッドデータをメタデータに保存
    if "analysis" not in result.metadata:
        result.metadata["analysis"] = {}

    result.metadata["analysis"]["grid_interpolation"] = {
        "x_range": x_range,
        "y_range": y_range,
        "grid_size": grid_size,
        "method": method,
        "target_column": target_column,
    }

    # グリッドデータを文字列として格納（シリアライズ）
    grid_str = np.array2string(grid_values, precision=4, suppress_small=True)

    # 結果を新しい列として追加
    result_col_name = f"{result_prefix}{target_column}_grid"
    result.columns[result_col_name] = Column(
        ch=None,
        name=result_col_name,
        unit=None,
        values=[grid_str] * len(collection.step),
        metadata={
            "description": f"Grid interpolation of {target_column}",
            "grid": {
                "x_min": x_range[0],
                "x_max": x_range[1],
                "y_min": y_range[0],
                "y_max": y_range[1],
                "nx": nx,
                "ny": ny,
            },
        },
    )

    return result


@operation(domain="coordinate")
def spatial_interpolation_to_points(
    collection: CoordinateCollection,
    source_columns: Optional[List[str]] = None,
    target_columns: Optional[List[str]] = None,
    method: str = "inverse_distance",
    power: float = 2.0,
    result_prefix: str = "interp_",
) -> CoordinateCollection:
    """ソース列からターゲット列の座標位置に値を補間する

    Args:
        collection: 座標コレクション
        source_columns: 補間ソースとなる列名リスト（Noneの場合は座標を持つ全列）
        target_columns: 補間先の座標を持つ列名リスト
        method: 補間方法
        power: 逆距離加重法のパワーパラメータ
        result_prefix: 結果列の接頭辞

    Returns:
        CoordinateCollection: 補間結果を含むコレクション
    """
    result = collection.clone()

    # 座標情報を持つ列を取得
    columns_with_coords = collection.get_columns_with_coordinates()

    # ソース列とターゲット列の決定
    if source_columns is None:
        source_columns = columns_with_coords

    if target_columns is None:
        # ターゲットが指定されていない場合、ソースと重複しない座標列を選択
        target_columns = [c for c in columns_with_coords if c not in source_columns]

    if not source_columns:
        raise ValueError("補間元の座標付き列がありません")

    if not target_columns:
        raise ValueError("補間先の座標付き列がありません")

    # 補間方法の選択
    if method == "inverse_distance":
        interp_func = _inverse_distance_weighting
    elif method == "nearest":
        interp_func = _nearest_neighbor
    else:
        interp_func = _linear_interpolation

    # ソースデータ収集
    source_data = []
    for col_name in source_columns:
        values = collection[col_name].values

        if not values:
            continue

        # 値の処理
        if isinstance(values[0], (int, float, np.number)):
            value = np.nanmean([v for v in values if v is not None and not np.isnan(v)])
        else:
            value = values[0]

        # 座標情報の取得
        col_x, col_y, col_z = collection.get_column_coordinates(col_name)

        if col_x is None or col_y is None:
            continue

        # 補間用データに追加
        source_data.append(
            {
                "point": {"x": col_x, "y": col_y, "z": col_z},
                "value": value,
                "col_name": col_name,
            }
        )

    # 各ターゲット位置での補間
    for target_col in target_columns:
        # ターゲット座標
        target_x, target_y, target_z = collection.get_column_coordinates(target_col)

        if target_x is None or target_y is None:
            continue

        # 3D補間かどうか
        is_3d = target_z is not None and all(
            d["point"]["z"] is not None for d in source_data
        )

        # 補間の計算（複数のソースからの補間平均）
        interp_values = []
        for src_data in source_data:
            interp_value = interp_func(
                src_data, target_x, target_y, target_z if is_3d else None, power
            )
            interp_values.append(interp_value)

        # 平均値を計算
        if interp_values:
            avg_interp = np.nanmean(interp_values)
        else:
            avg_interp = np.nan

        # 結果を新しい列として追加
        result_col_name = f"{result_prefix}{target_col}"
        result.columns[result_col_name] = Column(
            ch=None,
            name=result_col_name,
            unit=None,  # 元データによって異なるため、統一された単位は設定しない
            values=[avg_interp] * len(collection.step),
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


def _inverse_distance_weighting(
    point_data: Dict[str, Any], x: float, y: float, z: Optional[float], power: float
) -> float:
    """逆距離加重法による補間

    Args:
        point_data: 点のデータ（point, value, col_name）
        x, y, z: 補間する座標位置
        power: 重み付けパワー

    Returns:
        float: 補間値
    """
    # 点の座標
    px = point_data["point"]["x"]
    py = point_data["point"]["y"]
    pz = point_data["point"]["z"]

    value = point_data["value"]

    # 距離の計算
    if z is not None and pz is not None:
        # 3D距離
        distance = np.sqrt((x - px) ** 2 + (y - py) ** 2 + (z - pz) ** 2)
    else:
        # 2D距離
        distance = np.sqrt((x - px) ** 2 + (y - py) ** 2)

    # 距離が0（完全一致）の場合
    if distance < 1e-10:
        return value

    # 逆距離重み
    weight = 1.0 / (distance**power)
    return value * weight


def _nearest_neighbor(
    point_data: Dict[str, Any], x: float, y: float, z: Optional[float], power: float
) -> float:
    """最近傍法による補間

    Args:
        point_data: 点のデータ（point, value, col_name）
        x, y, z: 補間する座標位置
        power: 使用しないが、インターフェースの統一のため受け取る

    Returns:
        float: 補間値
    """
    # 点の座標
    px = point_data["point"]["x"]
    py = point_data["point"]["y"]
    pz = point_data["point"]["z"]

    value = point_data["value"]

    # 距離の計算 (補間結果には影響しないが、メタデータとして使用)
    if z is not None and pz is not None:
        # 3D距離
        distance = np.sqrt((x - px) ** 2 + (y - py) ** 2 + (z - pz) ** 2)
    else:
        # 2D距離
        distance = np.sqrt((x - px) ** 2 + (y - py) ** 2)

    return value


def _linear_interpolation(
    point_data: Dict[str, Any], x: float, y: float, z: Optional[float], power: float
) -> float:
    """線形補間（実装簡略化のため、逆距離加重法と同様の実装）

    実際の線形補間は複数の点が必要なため、これは簡略化した実装です。
    本来は三角形分割などを用いた多点での線形補間が必要です。

    Args:
        point_data: 点のデータ（point, value, col_name）
        x, y, z: 補間する座標位置
        power: 使用しないが、インターフェースの統一のため受け取る

    Returns:
        float: 補間値
    """
    # 線形補間の代わりに逆距離加重法を使用
    return _inverse_distance_weighting(point_data, x, y, z, 1.0)  # power=1.0 が線形的
