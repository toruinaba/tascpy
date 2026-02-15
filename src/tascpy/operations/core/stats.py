"""
統計処理に関連する操作を提供するモジュール。
移動平均、異常値検出など、データの統計的処理のための関数を含みます。
"""

from typing import Optional, List, Dict, Any, Tuple, Union
import numpy as np
from ...utils.data import moving_average as utils_moving_average
from ...core.collection import ColumnCollection
from ...core.column import Column, detect_column_type
from ..registry import operation
from ..abstraction import transform_column, inject_columns, handle_missing_values

# --- Transformation Operations ---

def _ma_naming(func_name, col_name, **kwargs):
    window_size = kwargs.get("window_size", 3)
    return f"ma{window_size}({col_name})"

@operation(domain="core")
@transform_column(num_inputs=1, result_naming=_ma_naming)
def moving_average(
    vals: Any,
    window_size: int = 3,
    edge_handling: str = "asymmetric",
) -> Any:
    """指定した列に対して移動平均を計算します

    指定された列の各値に対して、周辺値を使用した平均値を算出します。
    エッジ処理方法を選択することで、端部の計算方法を調整できます。

    Args:
        collection: 処理対象の ColumnCollection
        column: 処理対象の列名
        window_size: 移動平均のウィンドウサイズ（奇数推奨）
        result_column: 結果を格納する列名（None の場合は自動生成）
        edge_handling: エッジ処理方法（"symmetric", "asymmetric"）
        in_place: True の場合、結果を元の列に上書き

    Returns:
        ColumnCollection: 移動平均が計算された列を含むコレクション

    Raises:
        KeyError: 指定された列が存在しない場合
        ValueError: 無効なエッジ処理方法やウィンドウサイズが指定された場合
    """
    if edge_handling not in ["symmetric", "asymmetric"]:
        raise ValueError(f"無効なエッジ処理方法です: {edge_handling}")

    if window_size < 1:
        raise ValueError("ウィンドウサイズは1以上である必要があります")

    # データ長チェックはutils_moving_average内でエラーになるか、配列長で確認
    # valsはnumpy array (by transform_column)
    if len(vals) < window_size:
         raise ValueError("ウィンドウサイズがデータ長より大きくなっています")

    return utils_moving_average(
        vals, window_size=window_size, edge_handling=edge_handling
    )


def _outlier_naming(func_name, col_name, **kwargs):
    return f"outlier({col_name})"

@operation(domain="core")
@transform_column(num_inputs=1, result_naming=_outlier_naming)
def detect_outliers(
    vals: Any,
    window_size: int = 3,
    threshold: float = 0.5,
    edge_handling: str = "asymmetric",
    min_abs_value: float = 1e-10,
    scale_factor: float = 1.0,
) -> List[int]:
    """移動平均との差分比率を用いた異常値検出を行います

    データ値と移動平均の差分比率が閾値を超える場合に、その値を異常値として検出します。
    検出結果は新しい列に 0（正常）または 1（異常）のフラグとして格納されます。

    Args:
        collection: 処理対象の ColumnCollection
        column: 処理対象の列名
        window_size: 移動平均のウィンドウサイズ（奇数推奨）
        threshold: 異常値とみなす移動平均との差分比率の閾値
        edge_handling: エッジ処理方法（"symmetric", "asymmetric"）
        min_abs_value: 比率計算時の最小絶対値
        scale_factor: スケール調整係数
        result_column: 結果を格納する列名（None の場合は自動生成）

    Returns:
        ColumnCollection: 異常値フラグ列を含むコレクション（1=異常値、0=正常値）

    Raises:
        KeyError: 指定された列が存在しない場合
        ValueError: 無効なエッジ処理方法やウィンドウサイズが指定された場合、または有効なデータがない場合
    """
    if edge_handling not in ["symmetric", "asymmetric"]:
        raise ValueError(f"無効なエッジ処理方法です: {edge_handling}")

    if window_size < 1:
        raise ValueError("ウィンドウサイズは1以上である必要があります")

    if len(vals) < window_size:
        raise ValueError("データ長がウィンドウサイズより小さいです")

    # None値を除去した有効なデータのみでデータ特性を把握
    # NumPyを使用して高速化
    data = vals # transform_column ensures numpy array or list
    if isinstance(data, np.ndarray) and np.issubdtype(data.dtype, np.number):
        valid_arr = data[~np.isnan(data)]
    else:
        # If object array or list, handle None/NaN manually if transform_column passed them
        # transform_column with handle_none="nan" converts None to NaN in float array usually.
        # But let's be safe.
        valid_arr = np.array([x for x in data if x is not None and (not isinstance(x, float) or not np.isnan(x))], dtype=float)

    if len(valid_arr) == 0:
        raise ValueError(f"有効なデータがありません")

    # データの特性を把握
    data_std = np.std(valid_arr)
    # built-in max is shadowed by module level max function
    import builtins
    reference_value = builtins.max(data_std * scale_factor, min_abs_value)

    # 移動平均を計算 (utilsを使用)
    ma_values = utils_moving_average(
        data, window_size=window_size, edge_handling=edge_handling
    )
    
    # 統一的にNaNを含むfloat配列として扱う
    if isinstance(data, np.ndarray) and np.issubdtype(data.dtype, np.number):
        data_arr = data.astype(float)
    else:
        # Convert list/obj array to float array with NaN
        data_arr = np.array([x if x is not None else np.nan for x in data], dtype=float)
        
    if isinstance(ma_values, np.ndarray) and np.issubdtype(ma_values.dtype, np.number):
        ma_arr = ma_values.astype(float)
    else:
        ma_arr = np.array([x if x is not None else np.nan for x in ma_values], dtype=float)

    # ベクトル演算
    diff = np.abs(data_arr - ma_arr)
    denominator = np.maximum(np.abs(ma_arr), reference_value)
    
    # 比率計算 (0除算などはNaNになる)
    with np.errstate(divide='ignore', invalid='ignore'):
        ratio = diff / denominator
        
    # 条件判定
    # ratio > threshold AND diff > min_abs_value
    is_outlier = (ratio > threshold) & (diff > min_abs_value)
    
    # int型のフラグ配列 (0 or 1)
    outlier_flags = np.where(is_outlier, 1, 0).tolist()

    return outlier_flags


def _gaussian_naming(func_name, col_name, **kwargs):
    sigma = kwargs.get("sigma", 1.0)
    return f"gaussian(col={col_name},sigma={sigma})"

@operation(domain="core")
@transform_column(num_inputs=1, result_naming=_gaussian_naming)
def gaussian_filter(
    vals: Any,
    sigma: float = 1.0,
    window_size: Optional[int] = None,
) -> Any:
    """指定した列に対してガウシアンフィルタを適用します

    ガウス分布の重みを用いた畳み込み演算により、データを平滑化します。
    ノイズ除去特性が優れており、急激な変化を滑らかにします。

    Args:
        collection: 処理対象の ColumnCollection
        column: 処理対象の列名
        sigma: ガウス分布の標準偏差（平滑化の強さ）
        window_size: カーネルサイズ（デフォルトは 6*sigma + 1 の奇数）
        result_column: 結果を格納する列名（None の場合は自動生成）
        in_place: True の場合、結果を元の列に上書き

    Returns:
        ColumnCollection: 平滑化された列を含むコレクション
    """
    # ウィンドウサイズの自動設定 (scipy.ndimage.gaussian_filter1d の truncate=4.0 相当を考慮)
    if window_size is None:
        # 4*sigma 程度をカバーするサイズ
        radius = int(4.0 * sigma + 0.5)
        window_size = 2 * radius + 1
    
    if window_size < 1:
        raise ValueError("ウィンドウサイズは1以上である必要があります")

    data = vals
    # NumPy配列に変換 (None対応)
    if isinstance(data, np.ndarray) and np.issubdtype(data.dtype, np.number):
        data_arr = data.astype(float)
    else:
        # Noneを含む場合はNaNに変換
        data_arr = np.array([x if x is not None else np.nan for x in data], dtype=float)

    # ガウシアンカーネルの作成
    # x = [-radius, ..., 0, ..., radius]
    radius = window_size // 2
    x = np.arange(-radius, radius + 1)
    kernel = np.exp(-(x**2) / (2 * sigma**2))
    kernel = kernel / np.sum(kernel)  # 正規化

    # 畳み込み演算 (NaNを考慮)
    valid_mask = ~np.isnan(data_arr)
    filled_data = np.where(valid_mask, data_arr, 0.0)
    
    # データの畳み込み
    numerator = np.convolve(filled_data, kernel, mode='same')
    
    # 重みの畳み込み（NaNがあった場合の補正用）
    denominator = np.convolve(valid_mask.astype(float), kernel, mode='same')
    
    # 結果の計算
    with np.errstate(divide='ignore', invalid='ignore'):
        smoothed = numerator / denominator
    
    # 完全にデータがない場所はNaN
    smoothed[denominator == 0] = np.nan
    
    return smoothed






# --- Aggregation Operations ---

@operation(domain="core")
@inject_columns(num_inputs=1)
@handle_missing_values(strategy="nan")
def max(vals: Any) -> float:
    """列の最大値を取得します"""
    # vals is guaranteed to be a float array with NaN for None
    return float(np.nanmax(vals))

@operation(domain="core")
@inject_columns(num_inputs=1)
@handle_missing_values(strategy="nan")
def min(vals: Any) -> float:
    """列の最小値を取得します"""
    return float(np.nanmin(vals))

@operation(domain="core")
@inject_columns(num_inputs=1)
@handle_missing_values(strategy="nan")
def mean(vals: Any) -> float:
    """列の平均値を取得します"""
    return float(np.nanmean(vals))

@operation(domain="core")
@inject_columns(num_inputs=1)
@handle_missing_values(strategy="nan")
def std(vals: Any) -> float:
    """列の標準偏差を取得します"""
    return float(np.nanstd(vals))

@operation(domain="core")
@inject_columns(num_inputs=1)
@handle_missing_values(strategy="nan")
def sum(vals: Any) -> float:
    """列の合計値を取得します"""
    return float(np.nansum(vals))
