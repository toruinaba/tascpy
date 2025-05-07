"""
統計処理に関連する操作を提供するモジュール。
移動平均、異常値検出など、データの統計的処理のための関数を含みます。
"""

from typing import Optional, List, Dict, Any, Tuple, Union
from ...core.collection import ColumnCollection
from ...core.column import Column, detect_column_type
from ..registry import operation


@operation(domain="core")
def moving_average(
    collection: ColumnCollection,
    column: str,
    window_size: int = 3,
    result_column: Optional[str] = None,
    edge_handling: str = "asymmetric",
    in_place: bool = False,
) -> ColumnCollection:
    """
    指定した列に対して移動平均を計算します。

    Args:
        collection: 処理対象のColumnCollection
        column: 処理対象の列名
        window_size: 移動平均のウィンドウサイズ（奇数推奨）
        result_column: 結果を格納する列名（指定がない場合は自動生成）
        edge_handling: エッジ処理方法 ("symmetric", "asymmetric")
        in_place: True の場合、結果を元の列に上書き

    Returns:
        ColumnCollection: 移動平均が計算された列を含むコレクション
    """
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")

    if edge_handling not in ["symmetric", "asymmetric"]:
        raise ValueError(f"無効なエッジ処理方法です: {edge_handling}")

    if window_size < 1:
        raise ValueError("ウィンドウサイズは1以上である必要があります")

    if window_size > len(collection):
        raise ValueError("ウィンドウサイズがデータ長より大きくなっています")

    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()

    # 列の値を取得
    data = collection[column].values

    # 移動平均を計算
    moving_avg = []
    half_window = window_size // 2

    for i in range(len(data)):
        if edge_handling == "symmetric":
            start = max(0, i - half_window)
            end = min(len(data), i + half_window + 1)
            window = [v for v in data[start:end] if v is not None]
        else:  # asymmetric
            if i < half_window:  # 左端
                window = [v for v in data[0 : i + half_window + 1] if v is not None]
            elif i >= len(data) - half_window:  # 右端
                window = [v for v in data[i - half_window :] if v is not None]
            else:  # 中央部
                window = [
                    v
                    for v in data[i - half_window : i + half_window + 1]
                    if v is not None
                ]

        # 窓内のデータが存在する場合のみ平均値を計算
        if window:
            moving_avg.append(sum(window) / len(window))
        else:
            moving_avg.append(None)

    # 結果列名が指定されていない場合は自動生成
    if result_column is None:
        result_column = f"ma{window_size}({column})"

    # 結果を新しい列として追加（または既存の列を上書き）
    if result_column in result.columns:
        result.columns[result_column].values = moving_avg
    else:
        # 新しい列を追加
        # 元の列から単位などの情報を継承
        source_column = collection[column]
        column_type = detect_column_type(
            getattr(source_column, "ch", None),
            result_column,
            getattr(source_column, "unit", None),
            moving_avg,
        )
        result.add_column(result_column, column_type)

    return result


@operation(domain="core")
def detect_outliers(
    collection: ColumnCollection,
    column: str,
    window_size: int = 3,
    threshold: float = 0.5,
    edge_handling: str = "asymmetric",
    min_abs_value: float = 1e-10,
    scale_factor: float = 1.0,
    result_column: Optional[str] = None,
) -> ColumnCollection:
    """
    移動平均との差分比率を用いた異常値検出を行います。

    Args:
        collection: 処理対象のColumnCollection
        column: 処理対象の列名
        window_size: 移動平均のウィンドウサイズ（奇数推奨）
        threshold: 異常値とみなす移動平均との差分比率の閾値
        edge_handling: エッジ処理方法 ("symmetric", "asymmetric")
        min_abs_value: 比率計算時の最小絶対値
        scale_factor: スケール調整係数
        result_column: 結果を格納する列名（指定がない場合は自動生成）

    Returns:
        ColumnCollection: 異常値フラグ列を含むコレクション（1=異常値、0=正常値）
    """
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")

    if edge_handling not in ["symmetric", "asymmetric"]:
        raise ValueError(f"無効なエッジ処理方法です: {edge_handling}")

    if window_size < 1:
        raise ValueError("ウィンドウサイズは1以上である必要があります")

    if len(collection) < window_size:
        raise ValueError("データ長がウィンドウサイズより小さいです")

    # 結果を格納するオブジェクトを準備
    result = collection.clone()

    # 列の値を取得
    data = collection[column].values

    # None値を除去した有効なデータのみでデータ特性を把握
    valid_data = [x for x in data if x is not None]

    if not valid_data:
        raise ValueError(f"列 '{column}' に有効なデータがありません")

    # データの特性を把握
    data_mean = sum(valid_data) / len(valid_data)
    data_std = (sum((x - data_mean) ** 2 for x in valid_data) / len(valid_data)) ** 0.5
    reference_value = max(data_std * scale_factor, min_abs_value)

    # 移動平均を計算
    # 内部で移動平均を再計算せずに、既存の操作を使用
    ma_col = f"_ma_temp_{column}"
    result = moving_average(
        result,
        column=column,
        window_size=window_size,
        edge_handling=edge_handling,
        result_column=ma_col,
    )

    moving_avg = result[ma_col].values

    # 異常値フラグを初期化（0=正常、1=異常）
    outlier_flags = [0] * len(data)

    # 異常値を検出
    for i, value in enumerate(data):
        if value is None or moving_avg[i] is None:
            continue

        avg = moving_avg[i]
        diff = abs(value - avg)
        denominator = max(abs(avg), reference_value)

        if diff / denominator > threshold and diff > min_abs_value:
            outlier_flags[i] = 1

    # 結果列名が指定されていない場合は自動生成
    if result_column is None:
        result_column = f"outlier({column})"

    # 結果を新しい列として追加
    if result_column in result.columns:
        result.columns[result_column].values = outlier_flags
    else:
        column_type = detect_column_type(None, result_column, "", outlier_flags)
        result.add_column(result_column, column_type)

    # 一時的に作成した移動平均列を削除
    result.remove_column(ma_col)

    return result
