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


@operation(domain="core")
def moving_average(
    collection: ColumnCollection,
    column: str,
    window_size: int = 3,
    result_column: Optional[str] = None,
    edge_handling: str = "asymmetric",
    in_place: bool = False,
) -> ColumnCollection:
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
    moving_avg = utils_moving_average(
        data, window_size=window_size, edge_handling=edge_handling
    )

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
    # NumPyを使用して高速化
    if isinstance(data, np.ndarray) and np.issubdtype(data.dtype, np.number):
        valid_arr = data[~np.isnan(data)]
    else:
        valid_arr = np.array([x for x in data if x is not None], dtype=float)

    if len(valid_arr) == 0:
        raise ValueError(f"列 '{column}' に有効なデータがありません")

    # データの特性を把握
    data_mean = np.mean(valid_arr)
    data_std = np.std(valid_arr)
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

    # NumPy配列に変換 (None対応)
    if isinstance(data, np.ndarray) and np.issubdtype(data.dtype, np.number):
        data_arr = data.astype(float)
    else:
        # data contains None, ensure correct float conversion
        data_arr = np.array([x if x is not None else np.nan for x in data], dtype=float)
    
    # reference_valueは既に計算済み (lines 165-168)
    # data_mean, data_std are calculated from valid_data

    # 移動平均列を取得 (Noneが含まれる可能性がある)
    ma_values = result[ma_col].values
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
    # NaNはFalse扱い
    is_outlier = (ratio > threshold) & (diff > min_abs_value)
    
    # int型のフラグ配列 (0 or 1)
    # np.whereでNaNはFalseになるので0になる
    outlier_flags = np.where(is_outlier, 1, 0).tolist()

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


@operation(domain="core")
def gaussian_filter(
    collection: ColumnCollection,
    column: str,
    sigma: float = 1.0,
    window_size: Optional[int] = None,
    result_column: Optional[str] = None,
    in_place: bool = False,
) -> ColumnCollection:
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
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")

    # ウィンドウサイズの自動設定 (scipy.ndimage.gaussian_filter1d の truncate=4.0 相当を考慮)
    if window_size is None:
        # 4*sigma 程度をカバーするサイズ
        radius = int(4.0 * sigma + 0.5)
        window_size = 2 * radius + 1
    
    if window_size < 1:
        raise ValueError("ウィンドウサイズは1以上である必要があります")

    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()

    # 列の値を取得
    data = collection[column].values
    
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
    
    # 結果リストへの変換 (NaN -> None)
    result_values = [None if np.isnan(v) else v for v in smoothed]

    # 結果列名が指定されていない場合は自動生成
    if result_column is None:
        result_column = f"gaussian(col={column},sigma={sigma})"

    # 結果を格納
    if result_column in result.columns:
        result.columns[result_column].values = result_values
    else:
        source_column = collection[column]
        column_type = detect_column_type(
            getattr(source_column, "ch", None),
            result_column,
            getattr(source_column, "unit", None),
            result_values,
        )
        result.add_column(result_column, column_type)

    return result


@operation(domain="core")
def smooth(
    collection: ColumnCollection,
    column: str,
    method: str = "moving_average",
    window_size: int = 3,
    sigma: float = 1.0,  # for gaussian
    result_column: Optional[str] = None,
    in_place: bool = False,
    **kwargs
) -> ColumnCollection:
    """指定した列のデータを平滑化します

    移動平均またはガウシアンフィルタを使用して、データのノイズを低減します。

    Args:
        collection: 処理対象の ColumnCollection
        column: 処理対象の列名
        method: 平滑化手法 ("moving_average" または "gaussian")
        window_size: ウィンドウサイズ（移動平均用、ガウシアンの場合はフィルタサイズに影響）
        sigma: ガウシアンフィルタの標準偏差
        result_column: 結果を格納する列名
        in_place: True の場合、結果を元の列に上書き
        **kwargs: その他の引数（moving_averageのedge_handlingなど）

    Returns:
        ColumnCollection: 平滑化された列を含むコレクション
    """
    if method == "moving_average" or method == "ma":
        return moving_average(
            collection,
            column,
            window_size=window_size,
            result_column=result_column,
            in_place=in_place,
            **kwargs
        )
    elif method == "gaussian":
        return gaussian_filter(
            collection,
            column,
            sigma=sigma,
            window_size=kwargs.get("kernel_size", None), # window_size引数があればそれも考慮可能だが、gaussianはsigmaベースが一般的
            result_column=result_column,
            in_place=in_place,
        )
    else:
        raise ValueError(f"不明な平滑化手法です: {method}. 'moving_average' または 'gaussian' を指定してください。")


@operation(domain="core")
def ma(
    collection: ColumnCollection,
    column: str,
    window_size: int = 3,
    result_column: Optional[str] = None,
    edge_handling: str = "asymmetric",
    in_place: bool = False,
) -> ColumnCollection:
    """moving_average のエイリアス"""
    return moving_average(
        collection,
        column,
        window_size=window_size,
        result_column=result_column,
        edge_handling=edge_handling,
        in_place=in_place,
    )


@operation(domain="core")
def outliers(
    collection: ColumnCollection,
    column: str,
    window_size: int = 3,
    threshold: float = 0.5,
    edge_handling: str = "asymmetric",
    min_abs_value: float = 1e-10,
    scale_factor: float = 1.0,
    result_column: Optional[str] = None,
) -> ColumnCollection:
    """detect_outliers のエイリアス"""
    return detect_outliers(
        collection,
        column,
        window_size=window_size,
        threshold=threshold,
        edge_handling=edge_handling,
        min_abs_value=min_abs_value,
        scale_factor=scale_factor,
        result_column=result_column,
    )



@operation(domain="core")
def max(collection: ColumnCollection, column: str) -> float:
    """列の最大値を取得します
    
    Args:
        collection: 対象のコレクション
        column: 列名
        
    Returns:
        float: 最大値
    """
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")
    values = collection[column].values
    
    # None/NaN処理
    if hasattr(values, "dtype") and np.issubdtype(values.dtype, np.number):
        return float(np.nanmax(values))
    
    valid_values = [v for v in values if v is not None and (not isinstance(v, float) or not np.isnan(v))]
    if not valid_values:
        return float("nan")
        
    return float(np.max(valid_values))

@operation(domain="core")
def min(collection: ColumnCollection, column: str) -> float:
    """列の最小値を取得します
    
    Args:
        collection: 対象のコレクション
        column: 列名
        
    Returns:
        float: 最小値
    """
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")
    values = collection[column].values
    
    if hasattr(values, "dtype") and np.issubdtype(values.dtype, np.number):
        return float(np.nanmin(values))
    
    valid_values = [v for v in values if v is not None and (not isinstance(v, float) or not np.isnan(v))]
    if not valid_values:
        return float("nan")
        
    return float(np.min(valid_values))

@operation(domain="core")
def mean(collection: ColumnCollection, column: str) -> float:
    """列の平均値を取得します
    
    Args:
        collection: 対象のコレクション
        column: 列名
        
    Returns:
        float: 平均値
    """
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")
    values = collection[column].values
    
    if hasattr(values, "dtype") and np.issubdtype(values.dtype, np.number):
        return float(np.nanmean(values))
    
    valid_values = [v for v in values if v is not None and (not isinstance(v, float) or not np.isnan(v))]
    if not valid_values:
        return float("nan")
        
    return float(np.mean(valid_values))

@operation(domain="core")
def std(collection: ColumnCollection, column: str) -> float:
    """列の標準偏差を取得します
    
    Args:
        collection: 対象のコレクション
        column: 列名
        
    Returns:
        float: 標準偏差
    """
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")
    values = collection[column].values
    
    if hasattr(values, "dtype") and np.issubdtype(values.dtype, np.number):
        return float(np.nanstd(values))
    
    valid_values = [v for v in values if v is not None and (not isinstance(v, float) or not np.isnan(v))]
    if not valid_values:
        return float("nan")
        
    return float(np.std(valid_values))

@operation(domain="core")
def sum(collection: ColumnCollection, column: str) -> float:
    """列の合計値を取得します
    
    Args:
        collection: 対象のコレクション
        column: 列名
        
    Returns:
        float: 合計値
    """
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")
    values = collection[column].values
    
    if hasattr(values, "dtype") and np.issubdtype(values.dtype, np.number):
        return float(np.nansum(values))
    
    valid_values = [v for v in values if v is not None and (not isinstance(v, float) or not np.isnan(v))]
    if not valid_values:
        return float("nan")
        
    return float(np.sum(valid_values))
