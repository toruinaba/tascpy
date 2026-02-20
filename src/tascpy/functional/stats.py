from typing import Union, Optional, List, Any, Tuple
import numpy as np
from ..utils.data import moving_average as utils_moving_average

# --- Transformations ---

def moving_average(
    vals: Union[np.ndarray, List[float]],
    window_size: int = 3,
    edge_handling: str = "asymmetric",
) -> Any:
    """移動平均を計算します。

    Args:
        vals (Union[np.ndarray, List[float]]): 入力値の配列またはリスト。
        window_size (int, optional): ウィンドウサイズ。デフォルトは 3。
        edge_handling (str, optional): 境界処理の方法 ('symmetric', 'asymmetric')。デフォルトは "asymmetric"。

    Returns:
        Any: 移動平均処理後の配列（入力の型に依存）。

    Raises:
        ValueError: 無効なエッジ処理方法、ウィンドウサイズが1未満、またはデータ長より大きい場合。
    """
    if edge_handling not in ["symmetric", "asymmetric"]:
        raise ValueError(f"無効なエッジ処理方法です: {edge_handling}")

    if window_size < 1:
        raise ValueError("ウィンドウサイズは1以上である必要があります")

    # Check length
    if len(vals) < window_size:
         raise ValueError("ウィンドウサイズがデータ長より大きくなっています")

    return utils_moving_average(
        vals, window_size=window_size, edge_handling=edge_handling
    )

def detect_outliers(
    vals: Union[np.ndarray, List[float]],
    window_size: int = 3,
    threshold: float = 0.5,
    edge_handling: str = "asymmetric",
    min_abs_value: float = 1e-10,
    scale_factor: float = 1.0,
) -> List[int]:
    """移動平均を使用して外れ値を検出します。

    移動平均からの偏差率が閾値を超える場合を外れ値とみなします。

    Args:
        vals (Union[np.ndarray, List[float]]): 入力値の配列またはリスト。
        window_size (int, optional): 移動平均のウィンドウサイズ。デフォルトは 3。
        threshold (float, optional): 外れ値判定の閾値（偏差率）。デフォルトは 0.5。
        edge_handling (str, optional): 境界処理の方法。デフォルトは "asymmetric"。
        min_abs_value (float, optional): 最小絶対値（ゼロ除算防止）。デフォルトは 1e-10。
        scale_factor (float, optional): 基準値（標準偏差等）のスケーリング係数。デフォルトは 1.0。

    Returns:
        List[int]: 外れ値フラグのリスト（0: 正常, 1: 外れ値）。

    Raises:
        ValueError: 無効な引数、または有効なデータが存在しない場合。
    """
    if edge_handling not in ["symmetric", "asymmetric"]:
        raise ValueError(f"無効なエッジ処理方法です: {edge_handling}")

    if window_size < 1:
        raise ValueError("ウィンドウサイズは1以上である必要があります")

    if len(vals) < window_size:
        raise ValueError("データ長がウィンドウサイズより小さいです")

    # Helper to clean data
    data = vals
    if isinstance(data, np.ndarray) and np.issubdtype(data.dtype, np.number):
        valid_arr = data[~np.isnan(data)]
    else:
        valid_arr = np.array([x for x in data if x is not None and (not isinstance(x, float) or not np.isnan(x))], dtype=float)

    if len(valid_arr) == 0:
        raise ValueError(f"有効なデータがありません")

    data_std = np.std(valid_arr)
    # Use max from python defaults or numpy? Logic used builtins.max
    reference_value = float(max(data_std * scale_factor, min_abs_value))

    ma_values = utils_moving_average(
        data, window_size=window_size, edge_handling=edge_handling
    )
    
    # Convert to float array (handling None/NaN)
    if isinstance(data, np.ndarray) and np.issubdtype(data.dtype, np.number):
        data_arr = data.astype(float)
    else:
        data_arr = np.array([x if x is not None else np.nan for x in data], dtype=float)
        
    if isinstance(ma_values, np.ndarray) and np.issubdtype(ma_values.dtype, np. number):
        ma_arr = ma_values.astype(float)
    else:
        ma_arr = np.array([x if x is not None else np.nan for x in ma_values], dtype=float)

    diff = np.abs(data_arr - ma_arr)
    denominator = np.maximum(np.abs(ma_arr), reference_value)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        ratio = diff / denominator
        
    is_outlier = (ratio > threshold) & (diff > min_abs_value)
    
    # Return as list of 0/1 flags
    outlier_flags = np.where(is_outlier, 1, 0).tolist()

    return outlier_flags

def gaussian_filter(
    vals: Union[np.ndarray, List[float]],
    sigma: float = 1.0,
    window_size: Optional[int] = None,
) -> Any:
    """ガウシアンフィルタを適用して平滑化を行います。

    欠損値は無視して畳み込み計算を行います。

    Args:
        vals (Union[np.ndarray, List[float]]): 入力値の配列またはリスト。
        sigma (float, optional): ガウス分布の標準偏差。デフォルトは 1.0。
        window_size (Optional[int], optional): フィルタのウィンドウサイズ。指定しない場合は sigma から自動計算されます。

    Returns:
        Any: 平滑化後の配列（NumPy配列）。

    Raises:
        ValueError: ウィンドウサイズが1未満の場合。
    """
    if window_size is None:
        radius = int(4.0 * sigma + 0.5)
        window_size = 2 * radius + 1
    
    if window_size < 1:
        raise ValueError("ウィンドウサイズは1以上である必要があります")

    data = vals
    if isinstance(data, np.ndarray) and np.issubdtype(data.dtype, np.number):
        data_arr = data.astype(float)
    else:
        data_arr = np.array([x if x is not None else np.nan for x in data], dtype=float)

    radius = window_size // 2
    x = np.arange(-radius, radius + 1)
    kernel = np.exp(-(x**2) / (2 * sigma**2))
    kernel = kernel / np.sum(kernel)

    valid_mask = ~np.isnan(data_arr)
    filled_data = np.where(valid_mask, data_arr, 0.0)
    
    numerator = np.convolve(filled_data, kernel, mode='same')
    denominator = np.convolve(valid_mask.astype(float), kernel, mode='same')
    
    with np.errstate(divide='ignore', invalid='ignore'):
        smoothed = numerator / denominator
    
    smoothed[denominator == 0] = np.nan
    
    return smoothed

# --- Aggregations ---

def calc_max(vals: Any) -> float:
    """最大値を計算します（NaNは無視されます）。

    Args:
        vals (Any): 入力値の配列またはリスト。

    Returns:
        float: 最大値。
    """
    return float(np.nanmax(vals))

def calc_min(vals: Any) -> float:
    """最小値を計算します（NaNは無視されます）。

    Args:
        vals (Any): 入力値の配列またはリスト。

    Returns:
        float: 最小値。
    """
    return float(np.nanmin(vals))

def calc_mean(vals: Any) -> float:
    """平均値を計算します（NaNは無視されます）。

    Args:
        vals (Any): 入力値の配列またはリスト。

    Returns:
        float: 平均値。
    """
    return float(np.nanmean(vals))

def calc_std(vals: Any) -> float:
    """標準偏差を計算します（NaNは無視されます）。

    Args:
        vals (Any): 入力値の配列またはリスト。

    Returns:
        float: 標準偏差。
    """
    return float(np.nanstd(vals))

def calc_sum(vals: Any) -> float:
    """合計値を計算します（NaNは無視されます）。

    Args:
        vals (Any): 入力値の配列またはリスト。

    Returns:
        float: 合計値。
    """
    return float(np.nansum(vals))
