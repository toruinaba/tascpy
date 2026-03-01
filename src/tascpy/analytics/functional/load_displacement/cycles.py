"""荷重-変位データのサイクルに関する純粋関数群"""

from typing import List, Tuple, Optional, Dict, Any
import numpy as np


def compute_cycle_markers(data: np.ndarray, step: float = 0.5) -> np.ndarray:
    """データの符号反転からサイクル数をカウントします。
    
    Args:
        data: 対象データ配列
        step: サイクルカウントの増分
        
    Returns:
        np.ndarray: サイクルマーカーの配列
    """
    cycle = [1.0]
    for i in range(1, len(data)):
        if (
            data[i] is not None
            and data[i - 1] is not None
            and data[i] * data[i - 1] < 0
        ):
            c = cycle[i - 1] + step
            cycle.append(c)
        else:
            cycle.append(cycle[i - 1])
            
    return np.array([int(c) for c in cycle])


def calculate_polygon_area(x: np.ndarray, y: np.ndarray) -> float:
    """多角形の面積を計算（靴紐の公式）
    
    Args:
        x: X座標配列
        y: Y座標配列
        
    Returns:
        float: 面積（絶対値）
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
    """
    if len(loads) != len(disps):
        raise ValueError("荷重と変位のデータ長が一致しません")

    valid_indices = [k for k, (l, d) in enumerate(zip(loads, disps)) if l is not None and not np.isnan(l) and d is not None and not np.isnan(d)]
    
    if len(valid_indices) < 3:
        return (0.0, np.nan, np.nan, np.nan, np.nan)

    l_arr = np.array([loads[k] for k in valid_indices], dtype=float)
    d_arr = np.array([disps[k] for k in valid_indices], dtype=float)
    
    energy = calculate_polygon_area(d_arr, l_arr)
    
    max_l = float(np.max(l_arr))
    min_l = float(np.min(l_arr))
    max_d = float(np.max(d_arr))
    min_d = float(np.min(d_arr))

    return (energy, max_l, min_l, max_d, min_d)


def compute_secant_stiffness(
    max_load: float,
    min_load: float,
    max_disp: float,
    min_disp: float
) -> float:
    """最大荷重点と最小荷重点を結ぶ直線の傾き（割線剛性）を計算します。
    
    Args:
        max_load: 最大荷重
        min_load: 最小荷重
        max_disp: 最大変位
        min_disp: 最小変位
        
    Returns:
        float: 割線剛性（計算不能時は np.nan）
    """
    if any(v is None or np.isnan(v) for v in (max_load, min_load, max_disp, min_disp)):
        return np.nan
        
    delta_disp = max_disp - min_disp
    delta_load = max_load - min_load
    
    if abs(delta_disp) < 1e-9:
        return np.nan
        
    return delta_load / delta_disp


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
    """
    data_float = np.array([float(x) if x is not None else np.nan for x in data])
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
    *args,
    **kwargs
) -> Tuple[float, float, float, float, float, float]:
    """1サイクルのヒステリシス解析結果と各種統計情報をまとめて計算します。
    
    Args:
        loads: 荷重データ配列
        disps: 変位データ配列
        markers: サイクルマーカーの配列。先頭要素をサイクル番号として抽出します。
        
    Returns:
        Tuple: (サイクル番号, エネルギー, 最大荷重, 最小荷重, 最大変位, 最小変位)
    """
    energy, max_l, min_l, max_d, min_d = compute_hysteresis_energy(loads, disps)
    c_num = float(markers[0]) if len(markers) > 0 else 1.0
    return c_num, energy, max_l, min_l, max_d, min_d


def compute_stiffness_degradation_stats(
    loads: np.ndarray,
    disps: np.ndarray,
    markers: np.ndarray,
    *args,
    **kwargs
) -> Tuple[float, float]:
    """1サイクルの剛性推移（割線剛性）を計算します。
    
    Args:
        loads: 荷重データ配列
        disps: 変位データ配列
        markers: サイクルマーカーの配列。先頭要素をサイクル番号として抽出します。
        
    Returns:
        Tuple: (サイクル番号, 割線剛性)
    """
    energy, max_l, min_l, max_d, min_d = compute_hysteresis_energy(loads, disps)
    k = compute_secant_stiffness(max_l, min_l, max_d, min_d)
    c_num = float(markers[0]) if len(markers) > 0 else 1.0
    return c_num, k
