# 自動生成されたcoordinateドメインのスタブファイル - 編集しないでください
from typing import Optional, Union, List, Dict, Any, Callable, TypeVar, cast, Generic, overload, Literal
from ..core.collection import ColumnCollection
from ..domains.coordinate import CoordinateCollection
from .proxy_base import CollectionOperationsBase

class CoordinateCollectionOperations(CollectionOperationsBase[CoordinateCollection]):
    """coordinateドメインの操作メソッドスタブ定義
    
    このクラスはPylanceの型チェックとオートコンプリートのためのスタブです。
    実際の実行には使用されません。
    """

    def end(self) -> CoordinateCollection:
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
        """列の座標情報を取得します

指定された列に設定されている座標情報（x, y, z）を取得します。

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
        """指定した列の座標値を設定します

列に対して x、y、z の各座標値を設定します。
設定しない座標はそのままの値が維持されます。

Args:
    collection: 座標コレクション
    column: 列名
    x: X 座標
    y: Y 座標
    z: Z 座標

Returns:
    CoordinateCollection: 更新されたコレクション"""
        ...
    

    def get_columns_with_coordinates(
        self,
        
    ) -> "CoordinateCollectionOperations":
        """座標情報が設定されている列のリストを取得します

コレクション内で座標情報が設定されている全ての列名のリストを返します。

Args:
    collection: 座標コレクション

Returns:
    List[str]: 座標情報を持つ列名のリスト"""
        ...
    

    def extract_coordinates(
        self,
        result_prefix: str = 'coord_'
    ) -> "CoordinateCollectionOperations":
        """各列の座標値を新しい列としてコレクションに追加します

座標情報が設定されている列の x、y、z 座標値を取得し、それぞれを独立した列として
コレクションに追加します。新しい列名には指定された接頭辞が付与されます。

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
    ValueError: 座標情報がない場合"""
        ...
    

    def calculate_distance_matrix(
        self,
        columns: Optional[list[str]] = None,
        result_column_prefix: str = 'distance_'
    ) -> "CoordinateCollectionOperations":
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
    ValueError: 列が2つ未満の場合"""
        ...
    

    def find_nearest_neighbors(
        self,
        column: str,
        n_neighbors: int = 3,
        result_column: Optional[str] = None
    ) -> "CoordinateCollectionOperations":
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
    ValueError: 指定された列が存在しない場合、または座標情報がない場合"""
        ...
    

    def spatial_clustering(
        self,
        n_clusters: int = 2,
        columns: Optional[list[str]] = None,
        result_column: str = 'cluster',
        algorithm: str = 'kmeans'
    ) -> "CoordinateCollectionOperations":
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
    ValueError: クラスタ数が列数より多い場合、または有効な座標データがない場合"""
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
        """座標点での値を補間して計算します

指定された座標点 (x, y, z) において、既存の座標値に基づいて値を補間します。
補間方法として逆距離加重法、最近傍法、線形補間法を選択できます。

Args:
    collection: 座標コレクション
    x: 補間する X 座標
    y: 補間する Y 座標
    z: 補間する Z 座標 (2D の場合は None)
    target_columns: 補間対象の列名リスト (None の場合は座標を持つ全列)
    method: 補間方法 ("inverse_distance", "nearest", "linear")
    power: 逆距離加重法のパワーパラメータ
    result_prefix: 結果列の接頭辞

Returns:
    CoordinateCollection: 補間結果を含むコレクション

Raises:
    ValueError: 補間に使用できる座標付き列がない場合"""
        ...
    

    def interpolate_grid(
        self,
        x_range: tuple[float, float],
        y_range: tuple[float, float],
        grid_size: tuple[int, int] = (10, 10),
        target_column: Optional[str] = None,
        method: str = 'inverse_distance',
        power: float = 2.0,
        result_prefix: str = 'grid_'
    ) -> "CoordinateCollectionOperations":
        """指定した領域のグリッド上で値を補間します

指定された x-y 平面上の矩形領域をグリッドに分割し、各グリッド点での値を補間します。
補間結果はメタデータと結果列に保存されます。

Args:
    collection: 座標コレクション
    x_range: X 座標の範囲 (min, max)
    y_range: Y 座標の範囲 (min, max)
    grid_size: グリッドサイズ (nx, ny)
    target_column: 補間対象の列名
    method: 補間方法 ("inverse_distance", "nearest", "linear")
    power: 逆距離加重法のパワーパラメータ
    result_prefix: 結果列の接頭辞

Returns:
    CoordinateCollection: グリッド補間結果を含むコレクション

Raises:
    ValueError: 有効な座標情報がない場合、または指定した列が存在しない場合"""
        ...
    

    def spatial_interpolation_to_points(
        self,
        source_columns: Optional[list[str]] = None,
        target_columns: Optional[list[str]] = None,
        method: str = 'inverse_distance',
        power: float = 2.0,
        result_prefix: str = 'interp_'
    ) -> "CoordinateCollectionOperations":
        """ソース列からターゲット列の座標位置に値を補間します

指定されたソース列の座標位置の値を使用して、ターゲット列の座標位置における
値を補間します。複数のソースからの補間値の平均が計算されます。

Args:
    collection: 座標コレクション
    source_columns: 補間ソースとなる列名リスト（None の場合は座標を持つ全列）
    target_columns: 補間先の座標を持つ列名リスト
    method: 補間方法 ("inverse_distance", "nearest", "linear")
    power: 逆距離加重法のパワーパラメータ
    result_prefix: 結果列の接頭辞

Returns:
    CoordinateCollection: 補間結果を含むコレクション

Raises:
    ValueError: 補間元または補間先の座標付き列がない場合"""
        ...
    
