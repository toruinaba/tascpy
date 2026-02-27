"""荷重-変位データのサイクルに関する純粋関数群"""

from typing import List, Tuple, Optional
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
    return 0.5 * float(np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1))))


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
