"""荷重-変位データのサイクルに関する純粋関数群"""

from typing import List, Tuple, Optional, Dict, Any
import numpy as np


def compute_cycle_markers(data: np.ndarray, step: float = 0.5) -> np.ndarray:
    """データの符号反転からサイクル番号を数えます。

    0 と欠損（NaN）は符号を持たない点として飛ばし、直前の有効な値と符号が変わった位置で
    step だけ数を進めます（step=0.5 なら正負の往復で 1 サイクル）。サイクル番号は 1 から始まります。

    Args:
        data: 対象データ配列（欠損は NaN または None）
        step: 符号反転1回あたりの増分

    Returns:
        np.ndarray: サイクル番号の配列（整数）

    Examples:
        >>> from tascpy.analytics.functional.load_displacement.cycles import compute_cycle_markers
        >>> import numpy as np
        >>> compute_cycle_markers(np.array([10, 5, -5, -10, 5, 10]), step=0.5)
        array([1, 1, 1, 1, 2, 2])
        >>> compute_cycle_markers(np.array([10, 0, -10, np.nan, 10]), step=0.5)
        array([1, 1, 1, 1, 2])
    """
    sign = np.nan_to_num(np.sign(np.asarray(data, dtype=float)))
    nonzero = np.flatnonzero(sign)
    flips = np.zeros(len(sign))
    flips[nonzero[1:]] = sign[nonzero[1:]] != sign[nonzero[:-1]]
    return np.floor(1 + step * np.cumsum(flips)).astype(int)


def calculate_polygon_area(x: np.ndarray, y: np.ndarray) -> float:
    """多角形の面積を計算（靴紐の公式）
    
    Args:
        x: X座標配列
        y: Y座標配列
        
    Returns:
        float: 面積（絶対値）
        
    Examples:
        >>> from tascpy.analytics.functional.load_displacement.cycles import calculate_polygon_area
        >>> import numpy as np
        >>> x = np.array([0, 1, 1, 0])
        >>> y = np.array([0, 0, 1, 1])
        >>> calculate_polygon_area(x, y)
        1.0
    """
    if len(x) < 3 or len(y) < 3:
        return 0.0
    return 0.5 * float(np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1))))


def compute_hysteresis_energy(
    loads: np.ndarray,
    disps: np.ndarray,
) -> Tuple[float, float, float, float, float]:
    """1サイクルのヒステリシスループ面積（エネルギー散逸）と統計量を計算します。

    Args:
        loads: 荷重データ配列
        disps: 変位データ配列

    Returns:
        Tuple[float, float, float, float, float]:
            (エネルギー, 最大荷重, 最小荷重, 最大変位, 最小変位)
            
    Examples:
        >>> from tascpy.analytics.functional.load_displacement.cycles import compute_hysteresis_energy
        >>> import numpy as np
        >>> loads = np.array([0, 100, 0, -100, 0])
        >>> disps = np.array([0, 1, 2, 1, 0])
        >>> compute_hysteresis_energy(loads, disps)
        (200.0, 100.0, -100.0, 2.0, 0.0)
    """
    load = np.asarray(loads, dtype=float)
    disp = np.asarray(disps, dtype=float)
    if len(load) != len(disp):
        raise ValueError("荷重と変位のデータ長が一致しません")

    valid = ~(np.isnan(load) | np.isnan(disp))
    if valid.sum() < 3:
        return (0.0, np.nan, np.nan, np.nan, np.nan)
    l_arr, d_arr = load[valid], disp[valid]
    return (calculate_polygon_area(d_arr, l_arr), float(l_arr.max()), float(l_arr.min()),
            float(d_arr.max()), float(d_arr.min()))


def compute_secant_stiffness(
    max_load: float,
    min_load: float,
    disp_at_max_load: float,
    disp_at_min_load: float,
) -> float:
    """最大荷重点と最小荷重点を結ぶ直線の傾き（割線剛性）を計算します。

    Args:
        max_load: 最大荷重
        min_load: 最小荷重
        disp_at_max_load: 最大荷重点の変位
        disp_at_min_load: 最小荷重点の変位

    Returns:
        float: 割線剛性（計算不能時は np.nan）

    Examples:
        >>> from tascpy.analytics.functional.load_displacement.cycles import compute_secant_stiffness
        >>> compute_secant_stiffness(100.0, -100.0, 1.0, -1.0)
        100.0
    """
    values = (max_load, min_load, disp_at_max_load, disp_at_min_load)
    if any(v is None or np.isnan(v) for v in values):
        return np.nan

    delta_disp = disp_at_max_load - disp_at_min_load
    if abs(delta_disp) < 1e-9:
        return np.nan
    return (max_load - min_load) / delta_disp


def compute_peaks_and_valleys(
    data: np.ndarray,
    distance: int = 1,
    threshold: Optional[float] = None,
) -> np.ndarray:
    """配列内の極大値(1)と極小値(-1)を検出します。
    
    Args:
        data: 対象データ配列
        distance: ピーク間の最小距離（インデックス数）
        threshold: 隣接点との最小差
        
    Returns:
        np.ndarray: ピーク(1)、バレー(-1)、その他(0)のフラグ配列
        
    Examples:
        >>> from tascpy.analytics.functional.load_displacement.cycles import compute_peaks_and_valleys
        >>> import numpy as np
        >>> data = np.array([0, 2, 1, 0, -1, -2, -1, 0])
        >>> compute_peaks_and_valleys(data)
        array([ 0,  1,  0,  0,  0, -1,  0,  0])
    """
    data_float = np.asarray(data, dtype=float)
    flags = np.zeros(len(data), dtype=int)
    dist = max(1, distance)

    for i in range(1, len(data) - 1):
        if np.isnan(data_float[i]):
            continue
            
        # 極大判定
        if data_float[i] > data_float[i-1] and data_float[i] > data_float[i+1]:
            is_peak = True
            start = max(0, i - dist)
            if np.any(data_float[start:i] >= data_float[i]):
                is_peak = False
            
            if is_peak:
                end = min(len(data), i + dist + 1)
                if np.any(data_float[i+1:end] >= data_float[i]):
                    is_peak = False

            if is_peak and threshold is not None:
                min_neighbor = min(data_float[max(0, i-1)], data_float[min(len(data)-1, i+1)])
                if data_float[i] - min_neighbor < threshold:
                    is_peak = False

            if is_peak:
                flags[i] = 1

        # 極小判定
        if data_float[i] < data_float[i-1] and data_float[i] < data_float[i+1]:
            is_valley = True
            start = max(0, i - dist)
            if np.any(data_float[start:i] <= data_float[i]):
                is_valley = False
            
            if is_valley:
                end = min(len(data), i + dist + 1)
                if np.any(data_float[i+1:end] <= data_float[i]):
                    is_valley = False

            if is_valley and threshold is not None:
                max_neighbor = max(data_float[max(0, i-1)], data_float[min(len(data)-1, i+1)])
                if max_neighbor - data_float[i] < threshold:
                    is_valley = False

            if is_valley:
                flags[i] = -1

    return flags


def compute_energy_and_stats(
    loads: np.ndarray,
    disps: np.ndarray,
    markers: np.ndarray,
) -> Tuple[float, float, float, float, float, float]:
    """1サイクルのヒステリシス解析結果と各種統計情報をまとめて計算します。
    
    Args:
        loads: 荷重データ配列
        disps: 変位データ配列
        markers: サイクルマーカーの配列。先頭要素をサイクル番号として抽出します。
        
    Returns:
        Tuple: (サイクル番号, エネルギー, 最大荷重, 最小荷重, 最大変位, 最小変位)
        
    Examples:
        >>> from tascpy.analytics.functional.load_displacement.cycles import compute_energy_and_stats
        >>> import numpy as np
        >>> loads = np.array([0, 100, 0, -100, 0])
        >>> disps = np.array([0, 1, 2, 1, 0])
        >>> markers = np.array([1, 1, 1, 1, 1])
        >>> compute_energy_and_stats(loads, disps, markers)
        (1.0, 200.0, 100.0, -100.0, 2.0, 0.0)
    """
    energy, max_l, min_l, max_d, min_d = compute_hysteresis_energy(loads, disps)
    c_num = float(markers[0]) if len(markers) > 0 else 1.0
    return c_num, energy, max_l, min_l, max_d, min_d


def compute_stiffness_degradation_stats(
    loads: np.ndarray,
    disps: np.ndarray,
    markers: np.ndarray,
) -> Tuple[float, float]:
    """1サイクルの割線剛性（最大荷重点と最小荷重点を結ぶ直線の傾き）を計算します。

    Args:
        loads: 荷重データ配列
        disps: 変位データ配列
        markers: サイクルマーカーの配列。先頭要素をサイクル番号として抽出します。

    Returns:
        Tuple: (サイクル番号, 割線剛性)。荷重・変位がともに有効な点が2点未満なら剛性は NaN

    Examples:
        >>> from tascpy.analytics.functional.load_displacement.cycles import compute_stiffness_degradation_stats
        >>> import numpy as np
        >>> loads = np.array([0, 100, 0, -100, 0])
        >>> disps = np.array([0, 1, 0, -1, 0])
        >>> markers = np.array([1, 1, 1, 1, 1])
        >>> compute_stiffness_degradation_stats(loads, disps, markers)
        (1.0, 100.0)
    """
    c_num = float(markers[0]) if len(markers) > 0 else 1.0
    loads = np.asarray(loads, dtype=float)
    disps = np.asarray(disps, dtype=float)
    valid = ~(np.isnan(loads) | np.isnan(disps))
    if valid.sum() < 2:
        return c_num, np.nan
    l_arr, d_arr = loads[valid], disps[valid]
    i_max, i_min = int(np.argmax(l_arr)), int(np.argmin(l_arr))
    return c_num, compute_secant_stiffness(l_arr[i_max], l_arr[i_min], d_arr[i_max], d_arr[i_min])
