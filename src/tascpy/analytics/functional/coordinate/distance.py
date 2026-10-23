"""座標間の距離の純粋関数"""

from typing import Any

import numpy as np


def euclidean_distance(p1: Any, p2: Any) -> float:
    """2点間のユークリッド距離（座標は同じ次元の並び）

    Examples:
        >>> from tascpy.analytics.functional.coordinate.distance import euclidean_distance
        >>> euclidean_distance([0, 0], [3, 4])
        5.0
        >>> euclidean_distance([0, 0, 0], [1, 2, 2])
        3.0
    """
    a, b = np.asarray(p1, dtype=float), np.asarray(p2, dtype=float)
    if a.shape != b.shape:
        raise ValueError(f"座標の次元が一致しません: {a.shape} vs {b.shape}")
    return float(np.linalg.norm(a - b))
