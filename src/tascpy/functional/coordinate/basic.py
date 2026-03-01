"""座標ドメインの基本的な純粋関数群"""

from typing import Dict, Any, Optional, List, Tuple
import numpy as np


def extract_coordinates(
    x_array: Optional[np.ndarray] = None,
    y_array: Optional[np.ndarray] = None,
    z_array: Optional[np.ndarray] = None,
    length: int = 1
) -> Dict[str, np.ndarray]:
    """与えられた座標配列を個別の成分として抽出します

    Args:
        x_array: X座標の配列
        y_array: Y座標の配列
        z_array: Z座標の配列
        length: 結果配列の長さ（全要素を同じ値で埋める場合）

    Returns:
        Dict[str, np.ndarray]: 抽出された各座標成分の配列を含む辞書
    """
    result = {}
    if x_array is not None:
        result["x"] = np.full(length, x_array) if np.isscalar(x_array) else np.array(x_array)
    if y_array is not None:
        result["y"] = np.full(length, y_array) if np.isscalar(y_array) else np.array(y_array)
    if z_array is not None:
        result["z"] = np.full(length, z_array) if np.isscalar(z_array) else np.array(z_array)
    
    return result
