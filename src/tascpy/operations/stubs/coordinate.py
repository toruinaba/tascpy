# 自動生成されたcoordinateドメインのスタブファイル - 編集しないでください
from typing import Optional, Union, List, Dict, Any, Callable, TypeVar, cast
from ...core.collection import ColumnCollection
from .proxy_base import CollectionOperationsBase

class CoordinateCollectionOperations(CollectionOperationsBase):
    """coordinateドメインの操作メソッドスタブ定義
    
    このクラスはPylanceの型チェックとオートコンプリートのためのスタブです。
    実際の実行には使用されません。
    """

    def end(self) -> ColumnCollection:
        """操作チェーンを終了し、最終的なColumnCollectionを取得"""
        ...

    def debug(self, message: Optional[str] = None) -> "CoordinateCollectionOperations":
        """デバッグメッセージを表示
        
        Args:
            message: デバッグメッセージ
        
        Returns:
            CoordinateCollectionOperations: 自身を返す
        """
        ...


    def get_column_coordinates(
        self,
        column: str
    ) -> "CoordinateCollectionOperations":
        """列の座標情報を取得する

Args:
    collection: 座標コレクション
    column: 列名

Returns:
    Dict[str, Optional[float]]: 座標情報を含む辞書"""
        ...
    

    def set_column_coordinates(
        self,
        column: str,
        x: Optional[float] = None,
        y: Optional[float] = None,
        z: Optional[float] = None
    ) -> "CoordinateCollectionOperations":
        """指定した列の座標値を設定する

Args:
    collection: 座標コレクション
    column: 列名
    x: X座標
    y: Y座標
    z: Z座標

Returns:
    CoordinateCollection: 更新されたコレクション"""
        ...
    

    def get_columns_with_coordinates(
        self,
        
    ) -> "CoordinateCollectionOperations":
        """座標情報が設定されている列のリストを取得する

Args:
    collection: 座標コレクション

Returns:
    List[str]: 座標情報を持つ列名のリスト"""
        ...
    

    def extract_coordinates(
        self,
        result_prefix: str = 'coord_'
    ) -> "CoordinateCollectionOperations":
        """各列の座標値を新しい列としてコレクションに追加する

Args:
    collection: 座標コレクション
    result_prefix: 結果列の接頭辞

Returns:
    CoordinateCollection: 座標列を追加したコレクション"""
        ...
    

    def calculate_distance(
        self,
        column1: str,
        column2: str
    ) -> "CoordinateCollectionOperations":
        """2つの列の座標間の距離を計算する

Args:
    collection: 座標コレクション
    column1: 1つ目の列名
    column2: 2つ目の列名

Returns:
    float: 2点間のユークリッド距離"""
        ...
    

    def calculate_distance_matrix(
        self,
        columns: Optional[list[str]] = None,
        result_column_prefix: str = 'distance_'
    ) -> "CoordinateCollectionOperations":
        """選択した列の間の距離行列を計算し、結果列を追加する

Args:
    collection: 座標コレクション
    columns: 計算対象の列名リスト（Noneの場合は座標を持つ全列）
    result_column_prefix: 結果列の接頭辞

Returns:
    CoordinateCollection: 距離行列を含むコレクション"""
        ...
    

    def find_nearest_neighbors(
        self,
        column: str,
        n_neighbors: int = 3,
        result_column: Optional[str] = None
    ) -> "CoordinateCollectionOperations":
        """指定した列に最も近い座標を持つ近傍列を探す

Args:
    collection: 座標コレクション
    column: 基準となる列名
    n_neighbors: 取得する近傍の数
    result_column: 結果列名（Noneの場合、自動生成）

Returns:
    CoordinateCollection: 近傍情報を含むコレクション"""
        ...
    

    def spatial_clustering(
        self,
        n_clusters: int = 2,
        columns: Optional[list[str]] = None,
        result_column: str = 'cluster',
        algorithm: str = 'kmeans'
    ) -> "CoordinateCollectionOperations":
        """座標情報に基づいてクラスタリングを行う

Args:
    collection: 座標コレクション
    n_clusters: クラスタ数
    columns: クラスタリング対象の列名リスト（Noneの場合は座標を持つ全列）
    result_column: 結果列名
    algorithm: クラスタリングアルゴリズム（"kmeans", "hierarchical"）

Returns:
    CoordinateCollection: クラスタリング結果を含むコレクション"""
        ...
    

    def interpolate_at_point(
        self,
        x: float,
        y: float,
        z: Optional[float] = None,
        target_columns: Optional[list[str]] = None,
        method: str = 'inverse_distance',
        power: float = 2.0,
        result_prefix: str = 'interp_'
    ) -> "CoordinateCollectionOperations":
        """座標点での値を補間して計算する

Args:
    collection: 座標コレクション
    x: 補間するX座標
    y: 補間するY座標
    z: 補間するZ座標 (2Dの場合はNone)
    target_columns: 補間対象の列名リスト (Noneの場合は座標を持つ全列)
    method: 補間方法 ("inverse_distance", "nearest", "linear")
    power: 逆距離加重法のパワーパラメータ
    result_prefix: 結果列の接頭辞

Returns:
    CoordinateCollection: 補間結果を含むコレクション"""
        ...
    

    def interpolate_grid(
        self,
        x_range: tuple[float, float],
        y_range: tuple[float, float],
        grid_size: tuple[int, int] = (10, 10),
        target_column: str = None,
        method: str = 'inverse_distance',
        power: float = 2.0,
        result_prefix: str = 'grid_'
    ) -> "CoordinateCollectionOperations":
        """指定した領域のグリッド上で値を補間する

Args:
    collection: 座標コレクション
    x_range: X座標の範囲 (min, max)
    y_range: Y座標の範囲 (min, max)
    grid_size: グリッドサイズ (nx, ny)
    target_column: 補間対象の列名
    method: 補間方法
    power: 逆距離加重法のパワーパラメータ
    result_prefix: 結果列の接頭辞

Returns:
    CoordinateCollection: グリッド補間結果を含むコレクション"""
        ...
    

    def spatial_interpolation_to_points(
        self,
        source_columns: Optional[list[str]] = None,
        target_columns: Optional[list[str]] = None,
        method: str = 'inverse_distance',
        power: float = 2.0,
        result_prefix: str = 'interp_'
    ) -> "CoordinateCollectionOperations":
        """ソース列からターゲット列の座標位置に値を補間する

Args:
    collection: 座標コレクション
    source_columns: 補間ソースとなる列名リスト（Noneの場合は座標を持つ全列）
    target_columns: 補間先の座標を持つ列名リスト
    method: 補間方法
    power: 逆距離加重法のパワーパラメータ
    result_prefix: 結果列の接頭辞

Returns:
    CoordinateCollection: 補間結果を含むコレクション"""
        ...
    
