"""座標に基づく計算（距離・近傍・クラスタリング・空間補間）の純粋関数"""

from typing import Any, List, Tuple

import numpy as np

INTERPOLATION_METHODS = ("inverse_distance", "nearest")
_EXACT = 1e-12


def interpolate(points: Any, values: Any, targets: Any, method: str = "inverse_distance",
                power: float = 2.0) -> np.ndarray:
    """補間元の点の値から、補間先の座標での値を求めます

    - "inverse_distance": 逆距離加重 Σ(w·v)/Σw（w = 1/距離^power）。補間先が補間元の点と一致する場合はその点の値
    - "nearest": 最も近い補間元の点の値

    値が欠損（NaN）の補間元は、その列（時刻）の計算から除きます。有効な補間元がなければ NaN です。

    Args:
        points: 補間元の座標 (N, D)。D は 2 または 3
        values: 補間元の値 (N,)、または時刻ごとの値 (N, T)
        targets: 補間先の座標 (M, D)、または1点 (D,)
        method: 補間方法 ("inverse_distance", "nearest")
        power: 逆距離加重のべき指数

    Returns:
        np.ndarray: 補間値。形は (M,) / (M, T)、補間先が1点なら () / (T,)

    Raises:
        ValueError: 座標の次元が合わない場合、または未対応の method の場合

    Examples:
        >>> import numpy as np
        >>> from tascpy.numeric.spatial import interpolate
        >>> points = np.array([[0.0, 0.0], [10.0, 0.0]])
        >>> float(interpolate(points, [10.0, 20.0], [5.0, 0.0]))
        15.0
        >>> interpolate(points, [[10.0, 0.0], [20.0, 40.0]], [5.0, 0.0])
        array([15., 20.])
    """
    if method not in INTERPOLATION_METHODS:
        raise ValueError(f"サポートされていない補間方法: {method}（{', '.join(INTERPOLATION_METHODS)} のいずれか）")
    src = np.atleast_2d(np.asarray(points, dtype=float))
    raw_values = np.asarray(values, dtype=float)
    vals = raw_values.reshape(len(src), -1)
    raw_targets = np.asarray(targets, dtype=float)
    dst = np.atleast_2d(raw_targets)
    if src.shape[1] != dst.shape[1]:
        raise ValueError(f"補間元 ({src.shape[1]}次元) と補間先 ({dst.shape[1]}次元) の座標の次元が一致しません")

    distance = np.linalg.norm(dst[:, None, :] - src[None, :, :], axis=2)  # (M, N)
    valid = ~np.isnan(vals)  # (N, T)
    filled = np.where(valid, vals, 0.0)

    if method == "nearest":
        masked = np.where(valid.T[None, :, :], distance[:, None, :], np.inf)  # (M, T, N)
        nearest = np.argmin(masked, axis=2)
        result = np.take_along_axis(vals.T[None, :, :], nearest[..., None], axis=2)[..., 0]
        result = np.where(np.isinf(np.min(masked, axis=2)), np.nan, result)
    else:
        exact = distance < _EXACT
        with np.errstate(divide="ignore"):
            far_weight = np.where(exact, 0.0, 1.0 / distance**power)
        exact_weight = exact.astype(float)
        with np.errstate(invalid="ignore", divide="ignore"):
            far = (far_weight @ filled) / (far_weight @ valid)
            at_point = (exact_weight @ filled) / (exact_weight @ valid)
        result = np.where(np.isnan(at_point), far, at_point)

    result = result.reshape((len(dst),) + raw_values.shape[1:])
    return result[0] if raw_targets.ndim == 1 else result


def euclidean_distance(p1: Any, p2: Any) -> float:
    """2点間のユークリッド距離（座標は同じ次元の並び）

    Examples:
        >>> from tascpy.numeric.spatial import euclidean_distance
        >>> euclidean_distance([0, 0], [3, 4])
        5.0
        >>> euclidean_distance([0, 0, 0], [1, 2, 2])
        3.0
    """
    a, b = np.asarray(p1, dtype=float), np.asarray(p2, dtype=float)
    if a.shape != b.shape:
        raise ValueError(f"座標の次元が一致しません: {a.shape} vs {b.shape}")
    return float(np.linalg.norm(a - b))


def find_nearest_neighbors_logic(distances: List[Tuple[str, float]], n_neighbors: int) -> List[Tuple[str, float]]:
    """距離のリストから最も近いN個の近傍を取得します。

    Args:
        distances: (識別子, 距離) のリスト
        n_neighbors: 取得する近傍数

    Returns:
        List[Tuple[str, float]]: ソート済みの近傍リスト
        
    Examples:
        >>> from tascpy.numeric.spatial import find_nearest_neighbors_logic
        >>> dists = [("p1", 5.0), ("p2", 2.0), ("p3", 8.0)]
        >>> find_nearest_neighbors_logic(dists, 2)
        [('p2', 2.0), ('p1', 5.0)]
    """
    sorted_distances = sorted([d for d in distances if d[1] is not None and not np.isnan(d[1])], key=lambda x: x[1])
    n = min(n_neighbors, len(sorted_distances))
    return sorted_distances[:n]


def simple_kmeans(X: np.ndarray, n_clusters: int, max_iter: int = 100) -> np.ndarray:
    """簡易的なK-meansクラスタリング実装
    
    Args:
        X: 座標データ配列 (n_samples, n_features)
        n_clusters: クラスタ数
        max_iter: 最大繰り返し回数
        
    Returns:
        np.ndarray: 各データ点のクラスタラベル
        
    Examples:
        >>> from tascpy.numeric.spatial import simple_kmeans
        >>> import numpy as np
        >>> X = np.array([[1, 2], [1, 4], [1, 0], [10, 2], [10, 4], [10, 0]])
        >>> labels = simple_kmeans(X, 2)
    """
    n_samples, _ = X.shape
    
    rng = np.random.default_rng(42)
    centers = X[rng.choice(n_samples, n_clusters, replace=False)]
    
    labels = np.zeros(n_samples, dtype=int)
    
    for _ in range(max_iter):
        old_labels = labels.copy()
        
        for i in range(n_samples):
            distances = np.sqrt(((X[i] - centers) ** 2).sum(axis=1))
            labels[i] = np.argmin(distances)
            
        if np.all(old_labels == labels):
            break
            
        for j in range(n_clusters):
            mask = labels == j
            if mask.sum() > 0:
                centers[j] = X[mask].mean(axis=0)
                
    return labels
