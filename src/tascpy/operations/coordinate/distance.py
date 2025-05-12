"""座標ドメインの距離計算関数

このモジュールには、座標ベースの距離計算に関する関数が含まれています。
"""

from typing import Dict, Optional, List, Any, Tuple, Union
import numpy as np
from ...operations.registry import operation
from ...domains.coordinate import CoordinateCollection
from ...core.column import Column


@operation(domain="coordinate")
def calculate_distance(
    collection: CoordinateCollection, column1: str, column2: str
) -> float:
    """2つの列の座標間の距離を計算します

    指定された2つの列の座標位置間のユークリッド距離を計算します。
    2次元または3次元座標に対応しています。

    Args:
        collection: 座標コレクション
        column1: 1つ目の列名
        column2: 2つ目の列名

    Returns:
        float: 2点間のユークリッド距離

    Raises:
        ValueError: 座標情報がない場合
    """
    return collection.calculate_distance(column1, column2)


@operation(domain="coordinate")
def calculate_distance_matrix(
    collection: CoordinateCollection,
    columns: Optional[List[str]] = None,
    result_column_prefix: str = "distance_",
) -> CoordinateCollection:
    """選択した列の間の距離行列を計算し、結果列を追加します

    指定された列間の全ての組み合わせについて距離を計算し、距離行列を作成します。
    計算結果はメタデータに保存され、列ペア間の距離も個別の列として追加されます。

    Args:
        collection: 座標コレクション
        columns: 計算対象の列名リスト（None の場合は座標を持つ全列）
        result_column_prefix: 結果列の接頭辞

    Returns:
        CoordinateCollection: 距離行列を含むコレクション

    Raises:
        ValueError: 列が2つ未満の場合
    """
    result = collection.clone()

    if columns is None:
        columns = collection.get_columns_with_coordinates()

    if len(columns) < 2:
        raise ValueError("距離行列の計算には少なくとも2つの列が必要です")

    # 距離行列の計算
    n = len(columns)
    distances = np.zeros((n, n))

    for i in range(n):
        for j in range(i + 1, n):
            try:
                dist = collection.calculate_distance(columns[i], columns[j])
                distances[i, j] = dist
                distances[j, i] = dist
            except ValueError:
                # 距離計算できない場合はNoneで埋める
                distances[i, j] = np.nan
                distances[j, i] = np.nan

    # 距離行列をメタデータに保存
    if "analysis" not in result.metadata:
        result.metadata["analysis"] = {}

    result.metadata["analysis"]["distance_matrix"] = {
        "columns": columns,
        "matrix": distances.tolist(),
    }

    # 結果を列として追加
    for i, col1 in enumerate(columns):
        for j, col2 in enumerate(columns):
            if i < j:  # 対角成分と重複を避ける
                result_name = f"{result_column_prefix}{col1}_to_{col2}"
                result.columns[result_name] = Column(
                    ch=None,
                    name=result_name,
                    unit="m",  # 単位はメートルと仮定
                    values=[distances[i, j]] * len(collection.step),
                    metadata={
                        "description": f"Distance between {col1} and {col2}",
                        "type": "coordinate_distance",
                        "source_columns": [col1, col2],
                    },
                )

    return result


@operation(domain="coordinate")
def find_nearest_neighbors(
    collection: CoordinateCollection,
    column: str,
    n_neighbors: int = 3,
    result_column: Optional[str] = None,
) -> CoordinateCollection:
    """指定した列に最も近い座標を持つ近傍列を探します

    指定された列を基準として、座標空間上で最も近い n 個の列を探索します。
    結果はメタデータに保存され、近傍情報も新しい列として追加されます。

    Args:
        collection: 座標コレクション
        column: 基準となる列名
        n_neighbors: 取得する近傍の数
        result_column: 結果列名（None の場合、自動生成）

    Returns:
        CoordinateCollection: 近傍情報を含むコレクション

    Raises:
        ValueError: 指定された列が存在しない場合、または座標情報がない場合
    """
    result = collection.clone()

    if column not in collection.columns:
        raise ValueError(f"列 '{column}' が見つかりません")

    # 座標が設定されている列を取得
    columns_with_coords = collection.get_columns_with_coordinates()

    if column not in columns_with_coords:
        raise ValueError(f"列 '{column}' には座標情報がありません")

    if len(columns_with_coords) <= 1:
        raise ValueError("近傍検索には少なくとも2つの座標情報が必要です")

    # 基準列を除外
    other_columns = [c for c in columns_with_coords if c != column]

    # 各列との距離を計算
    distances = []
    for other_col in other_columns:
        try:
            dist = collection.calculate_distance(column, other_col)
            distances.append((other_col, dist))
        except ValueError:
            # 距離計算できない場合はスキップ
            continue

    # 距離でソート
    distances.sort(key=lambda x: x[1])

    # n_neighborsを確認して調整
    n_neighbors = min(n_neighbors, len(distances))

    # 近傍情報をメタデータに保存
    if "analysis" not in result.metadata:
        result.metadata["analysis"] = {}

    neighbors = [
        {"column": col, "distance": dist} for col, dist in distances[:n_neighbors]
    ]

    result.metadata["analysis"]["nearest_neighbors"] = {
        "reference_column": column,
        "neighbors": neighbors,
    }

    # 結果列名の決定
    if result_column is None:
        result_column = f"neighbors_of_{column}"

    # 近傍情報を文字列として列に追加
    neighbor_str = ", ".join(
        [f"{n['column']}({n['distance']:.4f}m)" for n in neighbors]
    )
    result.columns[result_column] = Column(
        ch=None,
        name=result_column,
        unit=None,
        values=[neighbor_str] * len(collection.step),
        metadata={
            "description": f"Nearest neighbors of {column}",
            "type": "nearest_neighbors",
            "reference_column": column,
            "neighbors": neighbors,
        },
    )

    return result


@operation(domain="coordinate")
def spatial_clustering(
    collection: CoordinateCollection,
    n_clusters: int = 2,
    columns: Optional[List[str]] = None,
    result_column: str = "cluster",
    algorithm: str = "kmeans",
) -> CoordinateCollection:
    """座標情報に基づいてクラスタリングを行います

    列の座標位置に基づいて、類似した位置にある列をグループ化します。
    クラスタリング結果はメタデータに保存され、各列のクラスタ情報も追加されます。

    Args:
        collection: 座標コレクション
        n_clusters: クラスタ数
        columns: クラスタリング対象の列名リスト（None の場合は座標を持つ全列）
        result_column: 結果列名
        algorithm: クラスタリングアルゴリズム（"kmeans", "hierarchical"）

    Returns:
        CoordinateCollection: クラスタリング結果を含むコレクション

    Raises:
        ValueError: クラスタ数が列数より多い場合、または有効な座標データがない場合
    """
    result = collection.clone()

    if columns is None:
        columns = collection.get_columns_with_coordinates()

    if len(columns) < n_clusters:
        raise ValueError(
            f"クラスタ数({n_clusters})は座標列数({len(columns)})より少なくする必要があります"
        )

    # 座標データの収集
    coord_data = []
    valid_columns = []

    for col in columns:
        try:
            x, y, z = collection.get_column_coordinates(col)

            # 必要な座標情報があるか確認
            if x is None or y is None:
                continue

            # 2D or 3D座標として追加
            if z is None:
                coord_data.append([x, y])
            else:
                coord_data.append([x, y, z])

            valid_columns.append(col)
        except ValueError:
            continue

    if not coord_data:
        raise ValueError("有効な座標データがありません")

    # 座標データをnumpy配列に変換
    X = np.array(coord_data)

    # クラスタリングの実行
    try:
        # scikit-learnのインポート（必要に応じて）
        from sklearn.cluster import KMeans, AgglomerativeClustering

        if algorithm.lower() == "kmeans":
            model = KMeans(n_clusters=n_clusters, random_state=42)
        elif algorithm.lower() == "hierarchical":
            model = AgglomerativeClustering(n_clusters=n_clusters)
        else:
            raise ValueError(f"サポートされていないアルゴリズム: {algorithm}")

        labels = model.fit_predict(X)
    except ImportError:
        # scikit-learnがない場合は簡易的なK-meansを実装
        labels = _simple_kmeans(X, n_clusters)

    # クラスタリング結果をメタデータに保存
    if "analysis" not in result.metadata:
        result.metadata["analysis"] = {}

    cluster_info = {}
    for i, col in enumerate(valid_columns):
        cluster_id = int(labels[i])
        if cluster_id not in cluster_info:
            cluster_info[cluster_id] = []
        cluster_info[cluster_id].append(col)

    result.metadata["analysis"]["clustering"] = {
        "algorithm": algorithm,
        "n_clusters": n_clusters,
        "clusters": cluster_info,
    }

    # 結果のメタデータを各列に追加
    for i, col in enumerate(valid_columns):
        cluster_id = int(labels[i])

        if not hasattr(result.columns[col], "metadata"):
            result.columns[col].metadata = {}

        if "analysis" not in result.columns[col].metadata:
            result.columns[col].metadata["analysis"] = {}

        result.columns[col].metadata["analysis"]["cluster"] = cluster_id

    # クラスタ情報を新しい列として追加（オプション）
    cluster_map = {col: int(labels[i]) for i, col in enumerate(valid_columns)}

    result.columns[result_column] = Column(
        ch=None,
        name=result_column,
        unit=None,
        values=[str(cluster_map)] * len(collection.step),
        metadata={
            "description": f"Clustering results using {algorithm}",
            "type": "clustering",
            "clusters": cluster_info,
        },
    )

    return result


def _simple_kmeans(X: np.ndarray, n_clusters: int, max_iter: int = 100) -> np.ndarray:
    """簡易的なK-meansクラスタリング実装

    scikit-learnがない場合のフォールバック実装

    Args:
        X: 座標データ配列
        n_clusters: クラスタ数
        max_iter: 最大繰り返し回数

    Returns:
        np.ndarray: クラスタラベル
    """
    # データ点数と次元数
    n_samples, n_features = X.shape

    # 初期センターをランダムに選択
    np.random.seed(42)
    centers = X[np.random.choice(n_samples, n_clusters, replace=False)]

    # クラスタラベル初期化
    labels = np.zeros(n_samples, dtype=int)

    for _ in range(max_iter):
        # 各データ点に最も近いセンターを割り当て
        old_labels = labels.copy()

        for i in range(n_samples):
            # 全センターとの距離を計算
            distances = np.sqrt(((X[i] - centers) ** 2).sum(axis=1))
            # 最も近いセンターのインデックスを割り当て
            labels[i] = np.argmin(distances)

        # 収束判定
        if np.all(old_labels == labels):
            break

        # センターの更新
        for j in range(n_clusters):
            mask = labels == j
            if mask.sum() > 0:  # クラスタjに割り当てられたデータ点がある場合
                centers[j] = X[mask].mean(axis=0)

    return labels
