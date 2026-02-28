"""座標ドメインのクラスタリング用純粋関数群"""

import numpy as np
from typing import List, Tuple, Optional

def simple_kmeans(X: np.ndarray, n_clusters: int, max_iter: int = 100) -> np.ndarray:
    """簡易的なK-meansクラスタリング実装
    
    Args:
        X: 座標データ配列 (n_samples, n_features)
        n_clusters: クラスタ数
        max_iter: 最大繰り返し回数
        
    Returns:
        np.ndarray: 各データ点のクラスタラベル
    """
    n_samples, _ = X.shape
    
    np.random.seed(42)
    centers = X[np.random.choice(n_samples, n_clusters, replace=False)]
    
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

def find_nearest_neighbors_logic(distances: List[Tuple[str, float]], n_neighbors: int) -> List[Tuple[str, float]]:
    """距離のリストから最も近いN個の近傍を取得します。

    Args:
        distances: (識別子, 距離) のリスト
        n_neighbors: 取得する近傍数

    Returns:
        List[Tuple[str, float]]: ソート済みの近傍リスト
    """
    sorted_distances = sorted([d for d in distances if d[1] is not None and not np.isnan(d[1])], key=lambda x: x[1])
    n = min(n_neighbors, len(sorted_distances))
    return sorted_distances[:n]
