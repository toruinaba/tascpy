"""座標ドメインの距離計算関数

このモジュールには、座標ベースの距離計算に関する関数が含まれています。
"""

from typing import Dict, Optional, List, Any, Tuple, Union
import numpy as np

from ...operations.registry import register_functional
from ...domains.coordinate import CoordinateCollection
from ...core.column import Column
from ...operations.validation import requires_domain, requires_coordinates
from ...functional.coordinate.clustering import find_nearest_neighbors_logic, simple_kmeans
from ...functional.coordinate.distance import compute_euclidean_distance
from .abstraction import (
    inject_coordinate_matrix, 
    store_clustering_result, 
    resolve_nearest_neighbors,
    resolve_distance
)

calculate_distance = register_functional(
    compute_euclidean_distance,
    domain="coordinate",
    name="calculate_distance",
    shared_with=["strain"],
    extra_decorators=[
        resolve_distance(),
        requires_coordinates(),
        requires_domain(["coordinate", "strain"]),
    ]
)
calculate_distance.__doc__ = """2つの列の座標間の距離を計算します

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

find_nearest_neighbors = register_functional(
    find_nearest_neighbors_logic,
    domain="coordinate",
    name="find_nearest_neighbors",
    shared_with=["strain"],
    extra_decorators=[
        resolve_nearest_neighbors(),
        requires_coordinates(),
        requires_domain(["coordinate", "strain"])
    ]
)
find_nearest_neighbors.__doc__ = """指定した列に最も近い座標を持つ近傍列を探します

    指定された列を基準として、座標空間上で最も近い n 個の列を探索します。
    結果はメタデータに保存され、近傍情報も新しい列として追加されます。

    Args:
        collection: 座標コレクション
        column: 基準となる列名
        n_neighbors: 取得する近傍の数 (デフォルト: 3)
        result_column: 結果列名（None の場合、自動生成）

    Returns:
        CoordinateCollection: 近傍情報を含むコレクション
"""

spatial_clustering = register_functional(
    simple_kmeans,
    domain="coordinate",
    name="spatial_clustering",
    shared_with=["strain"],
    extra_decorators=[
        inject_coordinate_matrix(include_z=True),
        store_clustering_result(algorithm_key="algorithm"),
        requires_coordinates(),
        requires_domain(["coordinate", "strain"])
    ]
)
spatial_clustering.__doc__ = """座標情報に基づいてクラスタリングを行います

    列の座標位置に基づいて、類似した位置にある列をグループ化します。
    クラスタリング結果はメタデータに保存され、各列のクラスタ情報も追加されます。

    Args:
        collection: 座標コレクション
        n_clusters: クラスタ数 (デフォルト: 2)
        columns: クラスタリング対象の列名リスト（None の場合は座標を持つ全列）
        result_column: 結果列名 (デフォルト: "cluster")
        algorithm: クラスタリングアルゴリズム (デフォルト: "kmeans")

    Returns:
        CoordinateCollection: クラスタリング結果を含むコレクション
"""

distance = register_functional(
    compute_euclidean_distance,
    domain="coordinate",
    name="distance",
    shared_with=["strain"],
    extra_decorators=[
        resolve_distance(),
        requires_coordinates(),
        requires_domain(["coordinate", "strain"]),
    ]
)
distance.__doc__ = "calculate_distance のエイリアス"

nearest_neighbors = register_functional(
    find_nearest_neighbors_logic,
    domain="coordinate",
    name="nearest_neighbors",
    shared_with=["strain"],
    extra_decorators=[
        resolve_nearest_neighbors(),
        requires_coordinates(),
        requires_domain(["coordinate", "strain"])
    ]
)
nearest_neighbors.__doc__ = "find_nearest_neighbors のエイリアス"

cluster = register_functional(
    simple_kmeans,
    domain="coordinate",
    name="cluster",
    shared_with=["strain"],
    extra_decorators=[
        inject_coordinate_matrix(include_z=True),
        store_clustering_result(algorithm_key="algorithm"),
        requires_coordinates(),
        requires_domain(["coordinate", "strain"])
    ]
)
cluster.__doc__ = "spatial_clustering のエイリアス"

