"""座標ドメインの距離計算に関する純粋関数"""

from typing import Tuple, Dict, Any, List
import numpy as np


def compute_euclidean_distance(
    p1_x: float, p1_y: float,
    p2_x: float, p2_y: float, 
    p1_z: float = None,
    p2_z: float = None
) -> float:
    """2点間のユークリッド距離を計算します

    Args:
        p1_x: 点1のX座標
        p1_y: 点1のY座標
        p1_z: 点1のZ座標 (オプション)
        p2_x: 点2のX座標
        p2_y: 点2のY座標
        p2_z: 点2のZ座標 (オプション)

    Returns:
        float: 計算された距離
        
    Examples:
        >>> from tascpy.analytics.functional.coordinate.distance import compute_euclidean_distance
        >>> compute_euclidean_distance(0, 0, 3, 4)
        5.0
        >>> compute_euclidean_distance(0, 0, 0, 1, 2, 2)
        3.0
    """
    if p1_z is None and p2_z is None:
        p1 = np.array([p1_x, p1_y])
        p2 = np.array([p2_x, p2_y])
    else:
        z1 = p1_z if p1_z is not None else 0.0
        z2 = p2_z if p2_z is not None else 0.0
        p1 = np.array([p1_x, p1_y, z1])
        p2 = np.array([p2_x, p2_y, z2])
        
    return float(np.linalg.norm(p1 - p2))
