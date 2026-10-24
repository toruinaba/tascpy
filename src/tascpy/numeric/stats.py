from typing import Any, Optional

import numpy as np


def _as_float(values: Any) -> np.ndarray:
    """値の並びを float 配列にする（None は NaN）"""
    return np.asarray(values, dtype=float)


def moving_average(data: Any, window_size: int = 3) -> np.ndarray:
    """中心移動平均を計算します（欠損 NaN はウィンドウ内の平均から除く）。

    端ではウィンドウに含まれる有効な点だけで平均します。ウィンドウ内に有効な点がなければ NaN です。

    Args:
        data: 入力値の配列（None は欠損）
        window_size: ウィンドウサイズ

    Returns:
        np.ndarray: 移動平均

    Examples:
        >>> import numpy as np
        >>> from tascpy.numeric.stats import moving_average
        >>> moving_average([10.0, 20.0, None, 40.0], window_size=3)
        array([15., 15., 30., 40.])
    """
    values = _as_float(data)
    if len(values) == 0:
        return np.array([], dtype=float)
    kernel = np.ones(window_size)
    valid = ~np.isnan(values)
    numerator = np.convolve(np.where(valid, values, 0.0), kernel, mode="same")
    denominator = np.convolve(valid.astype(float), kernel, mode="same")
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(denominator > 0, numerator / denominator, np.nan)


def detect_outliers(
    vals: Any,
    window_size: int = 3,
    threshold: float = 0.5,
    min_abs_value: float = 1e-10,
    scale_factor: float = 1.0,
) -> np.ndarray:
    """移動平均からの偏差率が閾値を超える点を外れ値とみなします。

    偏差率 = |値 - 移動平均| / max(|移動平均|, 標準偏差 × scale_factor, min_abs_value)

    Args:
        vals: 入力値の配列（None は欠損）
        window_size: 移動平均のウィンドウサイズ
        threshold: 外れ値とみなす偏差率の閾値
        min_abs_value: 偏差の最小値（これ以下の偏差は外れ値としない、ゼロ除算防止にも使う）
        scale_factor: 標準偏差にかける係数

    Returns:
        np.ndarray: 外れ値フラグの配列（0: 正常, 1: 外れ値、欠損は 0）

    Raises:
        ValueError: ウィンドウサイズが不正な場合、または有効なデータがない場合
    """
    if window_size < 1:
        raise ValueError("ウィンドウサイズは1以上である必要があります")
    values = _as_float(vals)
    if len(values) < window_size:
        raise ValueError("データ長がウィンドウサイズより小さいです")
    valid = values[~np.isnan(values)]
    if len(valid) == 0:
        raise ValueError("有効なデータがありません")

    reference = max(float(np.std(valid)) * scale_factor, min_abs_value)
    average = moving_average(values, window_size=window_size)
    deviation = np.abs(values - average)
    with np.errstate(invalid="ignore"):
        ratio = deviation / np.maximum(np.abs(average), reference)
        return np.where((ratio > threshold) & (deviation > min_abs_value), 1, 0)


def gaussian_filter(
    vals: Any,
    sigma: float = 1.0,
    window_size: Optional[int] = None,
) -> np.ndarray:
    """ガウシアンフィルタを適用して平滑化を行います。

    欠損値は無視して畳み込み計算を行います。

    Args:
        vals (Union[np.ndarray, List[float]]): 入力値の配列またはリスト。
        sigma (float, optional): ガウス分布の標準偏差。デフォルトは 1.0。
        window_size (Optional[int], optional): フィルタのウィンドウサイズ。指定しない場合は sigma から自動計算されます。

    Returns:
        np.ndarray: 平滑化後の配列。

    Raises:
        ValueError: ウィンドウサイズが1未満の場合。
        
    Examples:
        >>> from tascpy.numeric.stats import gaussian_filter
        >>> import numpy as np
        >>> arr = np.array([0, 10, 0, 0, 0])
        >>> smoothed = gaussian_filter(arr, sigma=1.0)
    """
    if window_size is None:
        window_size = 2 * int(4.0 * sigma + 0.5) + 1
    if window_size < 1:
        raise ValueError("ウィンドウサイズは1以上である必要があります")
    values = _as_float(vals)

    radius = window_size // 2
    x = np.arange(-radius, radius + 1)
    kernel = np.exp(-(x**2) / (2 * sigma**2))
    kernel /= kernel.sum()

    valid = ~np.isnan(values)
    n = len(values)
    numerator = np.convolve(np.where(valid, values, 0.0), kernel, mode="full")[radius:radius + n]
    denominator = np.convolve(valid.astype(float), kernel, mode="full")[radius:radius + n]
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(denominator > 0, numerator / denominator, np.nan)
