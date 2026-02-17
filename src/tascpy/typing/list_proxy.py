# 自動生成されたCollectionListOperationsスタブ - 編集しないでください
from typing import Optional, Union, List, Dict, Any, Callable, TypeVar, Generic, overload
from ..core.collection import ColumnCollection
from .proxy_base import CollectionOperationsBase
from typing import Literal
from ..domains.core import ColumnCollection
from ..domains.strain import StrainCollection
from ..domains.load_displacement import LoadDisplacementCollection
from ..domains.coordinate import CoordinateCollection

# コレクション型のTypeVar
C = TypeVar('C', bound=ColumnCollection)

class CollectionListOperations(Generic[C]):
    """複数のColumnCollectionを一度に操作するためのプロキシクラス
    
    このクラスはPylanceの型チェックとオートコンプリートのためのスタブです。
    実際の実行には使用されません。
    """

    def __len__(self) -> int:
        """コレクションリストの長さを返します"""
        ...

    def __getitem__(
        self, index: Union[int, slice]
    ) -> Union[CollectionOperationsBase[C], "CollectionListOperations[C]"]:
        """指定されたインデックスのCollectionOperationsを返します
        
        Args:
            index: アクセスするインデックスまたはスライス
            
        Returns:
            インデックスの場合はCollectionOperations、スライスの場合はCollectionListOperations
            
        Raises:
            IndexError: インデックスが範囲外の場合
            TypeError: インデックスが整数またはスライスでない場合
        """
        ...

    def map(
        self, operation: str, *args: Any, **kwargs: Any
    ) -> Union["CollectionListOperations[C]", List[Any]]:
        """各コレクションに同じ操作を適用します
        
        Args:
            operation: 適用する操作名
            *args: 操作に渡す位置引数
            **kwargs: 操作に渡すキーワード引数
            
        Returns:
            操作結果のCollectionListOperationsまたは結果のリスト
            
        Raises:
            AttributeError: 指定された操作が存在しない場合
        """
        ...

    def filter(
        self, predicate: Callable[[C], bool]
    ) -> "CollectionListOperations[C]":
        """条件を満たすコレクションだけをフィルタリングします
        
        Args:
            predicate: フィルタリング条件を判定する関数
            
        Returns:
            フィルタリングされたコレクションを持つCollectionListOperations
        """
        ...

    def concat(self) -> CollectionOperationsBase[C]:
        """全てのコレクションを連結して一つのCollectionOperationsを返します
        
        Returns:
            連結されたデータを持つCollectionOperations
            
        Raises:
            ValueError: 連結するコレクションが存在しない場合
        """
        ...

    def end_all(self) -> List[C]:
        """操作を終了し、ColumnCollectionのリストを返します"""
        ...

    @overload
    def as_domain(self, domain: Literal['core'], **kwargs: Any) -> "CollectionListOperations[ColumnCollection]":
        ...

    @overload
    def as_domain(self, domain: Literal['strain'], **kwargs: Any) -> "CollectionListOperations[StrainCollection]":
        ...

    @overload
    def as_domain(self, domain: Literal['load_displacement'], **kwargs: Any) -> "CollectionListOperations[LoadDisplacementCollection]":
        ...

    @overload
    def as_domain(self, domain: Literal['coordinate'], **kwargs: Any) -> "CollectionListOperations[CoordinateCollection]":
        ...

    def as_domain(self, domain: str, **kwargs: Any) -> "CollectionListOperations":
        """全てのコレクションを指定されたドメインに変換します
        
        Args:
            domain: 変換先のドメイン名
            **kwargs: 変換に渡す追加引数
            
        Returns:
            変換されたコレクションリスト
        """
        ...

    def filter_by_value(
        self,
        value: Any,
        tolerance: Optional[float] = None
    ) -> List[ndarray]:
        """Check if values are equal to target value.
Supports tolerance for float comparisons."""
        ...
    

    def filter_out_none(
        self,
        mode: str = 'any'
    ) -> List[list[bool]]:
        """Return boolean mask for valid rows (no None/NaN).
mode='any': Keep row if ALL columns are valid. (Wait, logic check below)
mode='all': Keep row if ANY column is valid. 

Standard 'dropna' logic:
any: if any value is NA, drop row. (So keep if ALL valid)
all: if all values are NA, drop row. (So keep if ANY valid)

The original implementation said:
mode='any': keep if all valid (drop if any invalid?) 
  -> "mode='any': ひとつでも無効なら除外" (If any invalid, exclude -> dropna(how='any'))
mode='all': keep if any valid (drop if all invalid)
  -> "mode='all': すべて無効なら除外" (If all invalid, exclude -> dropna(how='all'))"""
        ...
    

    def remove_consecutive_duplicates_across(
        self,
        mode: str = 'consecutive',
        dup_type: str = 'all'
    ) -> List[list[int]]:
        """Return indices to KEEP after removing duplicates.

Args:
    data: Dict of columns
    mode: 
        'consecutive': Remove if previous row is identical (keep first).
        'all': Not implemented yet, reserved for unique rows.
    dup_type:
        'all': Remove row if ALL columns match previous row value (standard).
        'any': Remove row if ANY column matches previous row value (strict)."""
        ...
    

    def remove_outliers(
        self,
        *args,
        **kwargs
    ) -> List[Any]:
        """"""
        ...
    

    def filter_by_condition(
        self,
        condition: <built-in function callable>
    ) -> "CollectionListOperations[C]":
        """Filter values by condition.
Returns boolean mask (True to keep)."""
        ...
    

    def remove_steps(
        self,
        steps: list[Any],
        tolerance: Optional[float] = None
    ) -> List[list[bool]]:
        """Generate mask to remove specific steps.
Returns True for kept steps."""
        ...
    

    def search_by_value(
        self,
        op_str: str,
        value: Any
    ) -> List[list[int]]:
        """Return indices where values satisfy the operator condition."""
        ...
    

    def search_by_range(
        self,
        min_val: Any,
        max_val: Any,
        inclusive: bool = True
    ) -> List[list[int]]:
        """Return indices where values are within range."""
        ...
    

    def search_by_step_range(
        self,
        min_val: float,
        max_val: float,
        inclusive: bool = True,
        tolerance: Optional[float] = None,
        by_step_value: bool = True
    ) -> List[list[int]]:
        """Return indices where steps are within range, with optional tolerance.
If by_step_value is False, searches within indices matching the step length."""
        ...
    

    def search_top_n(
        self,
        n: int,
        descending: bool = True
    ) -> List[list[int]]:
        """Return indices of top N values.
Handles NaN by excluding them."""
        ...
    

    def plot(
        self,
        y_values: ndarray,
        x_label: str,
        y_label: str,
        title: str,
        ax: Optional[Axes] = None,
        **kwargs
    ) -> List[Axes]:
        """基本プロット関数 (Functional wrapper)"""
        ...
    

    def visualize_outliers(
        self,
        y_values: Any,
        x_label: str,
        y_label: str,
        title: str,
        window_size: int = 3,
        threshold: float = 0.5,
        highlight_color: str = 'red',
        plot_type: str = 'scatter',
        show_normal: bool = True,
        normal_color: str = 'blue',
        normal_alpha: float = 0.5,
        outlier_marker: str = 'o',
        outlier_size: int = 50,
        ax: Optional[Axes] = None,
        edge_handling: str = 'asymmetric',
        min_abs_value: float = 1e-10,
        scale_factor: float = 1.0,
        **kwargs
    ) -> List[Axes]:
        """異常値を可視化する (Functional implementation)"""
        ...
    

    def plot_const_x(
        self,
        x_values: list[float],
        show_legend: bool = True,
        ax: Optional[Axes] = None,
        **kwargs
    ) -> List[Axes]:
        """特定のx値に対して複数のy列の値をプロットします"""
        ...
    

    def iplot(
        self,
        y_values: ndarray,
        x_label: str,
        y_label: str,
        title: str,
        fig: Optional[Any] = None,
        **kwargs
    ) -> List[Any]:
        """インタラクティブなグラフを描画します (Functional wrapper)"""
        ...
    

    def select(
        self,
        columns: Optional[list[str]] = None,
        indices: Optional[list[int]] = None,
        steps: Optional[list[Union[int, float]]] = None,
        by_step_value: bool = True,
        tolerance: Optional[float] = None
    ) -> List[tuple[list[int], dict[str, Any]]]:
        """Select indices based on steps or direct indices.
Returns: (final_indices, metadata_update)"""
        ...
    

    def fetch_near_step(
        self,
        value: float,
        **kwargs
    ) -> "CollectionListOperations[C]":
        """Find index of nearest value.
Returns list containing single index."""
        ...
    

    def switch_by_step(
        self,
        v1: ndarray,
        v2: ndarray,
        threshold: Union[int, float],
        compare_mode: str = 'value',
        by_step_value: bool = True,
        tolerance: Optional[float] = None
    ) -> List[ndarray]:
        """Switch between v1 and v2 based on steps/index."""
        ...
    

    def blend_by_step(
        self,
        v1: ndarray,
        v2: ndarray,
        start: Union[int, float],
        end: Union[int, float],
        compare_mode: str = 'value',
        by_step_value: bool = True,
        blend_method: str = 'linear',
        tolerance: Optional[float] = None
    ) -> List[ndarray]:
        """Blend v1 and v2 based on steps/index."""
        ...
    

    def sum_columns(
        self,
        columns = None
    ) -> List[Any]:
        """"""
        ...
    

    def average_columns(
        self,
        columns = None
    ) -> List[Any]:
        """"""
        ...
    

    def conditional_select(
        self,
        v2: ndarray,
        cond_values: ndarray,
        threshold: Union[int, float] = 0,
        compare: str = '>'
    ) -> List[ndarray]:
        """Select from v1 or v2 based on condition."""
        ...
    

    def custom_combine(
        self,
        v2: Any,
        combine_func: Callable[[Any, Any], Any],
        **kwargs
    ) -> "CollectionListOperations[C]":
        """Combine v1 and v2 using custom function."""
        ...
    

    def add(
        self,
        v2: Union[ndarray, float]
    ) -> List[ndarray]:
        """Add two values or arrays."""
        ...
    

    def subtract(
        self,
        v2: Union[ndarray, float]
    ) -> List[ndarray]:
        """Subtract v2 from v1."""
        ...
    

    def multiply(
        self,
        v2: Union[ndarray, float]
    ) -> List[ndarray]:
        """Multiply two values or arrays."""
        ...
    

    def divide(
        self,
        v2: Union[ndarray, float],
        **kwargs
    ) -> List[ndarray]:
        """Divide v1 by v2."""
        ...
    

    def diff(
        self,
        x: Union[ndarray, list[float]],
        method: str = 'central'
    ) -> List[ndarray]:
        """Calculate differential coefficient from x, y coordinates."""
        ...
    

    def integrate(
        self,
        x: Union[ndarray, list[float]],
        method: str = 'trapezoid',
        initial_value: float = 0.0
    ) -> List[ndarray]:
        """Calculate integral of y with respect to x."""
        ...
    

    def evaluate(
        self,
        expression: str,
        **kwargs
    ) -> List[Union[list[Optional[float]], ndarray]]:
        """"""
        ...
    

    def moving_average(
        self,
        window_size: int = 3,
        edge_handling: str = 'asymmetric'
    ) -> List[Any]:
        """Calculate moving average."""
        ...
    

    def detect_outliers(
        self,
        window_size: int = 3,
        threshold: float = 0.5,
        edge_handling: str = 'asymmetric',
        min_abs_value: float = 1e-10,
        scale_factor: float = 1.0
    ) -> List[list[int]]:
        """Detect outliers using moving average."""
        ...
    

    def gaussian_filter(
        self,
        sigma: float = 1.0,
        window_size: Optional[int] = None
    ) -> List[Any]:
        """Apply gaussian filter."""
        ...
    

    def max(
        self,
        
    ) -> List[float]:
        """Get max value."""
        ...
    

    def min(
        self,
        
    ) -> List[float]:
        """Get min value."""
        ...
    

    def mean(
        self,
        
    ) -> List[float]:
        """Get mean value."""
        ...
    

    def std(
        self,
        
    ) -> List[float]:
        """Get standard deviation."""
        ...
    

    def sum(
        self,
        
    ) -> List[float]:
        """Get sum."""
        ...
    

    def sin(
        self,
        degrees: bool = False
    ) -> List[ndarray]:
        """Calculate sine of values."""
        ...
    

    def cos(
        self,
        degrees: bool = False
    ) -> List[ndarray]:
        """Calculate cosine of values."""
        ...
    

    def tan(
        self,
        degrees: bool = False
    ) -> List[ndarray]:
        """Calculate tangent of values."""
        ...
    

    def exp(
        self,
        
    ) -> List[ndarray]:
        """Calculate exponential of values."""
        ...
    

    def log(
        self,
        base: float = 2.718281828459045
    ) -> List[ndarray]:
        """Calculate logarithm of values."""
        ...
    

    def sqrt(
        self,
        
    ) -> List[ndarray]:
        """Calculate square root of values."""
        ...
    

    def pow(
        self,
        exponent: float
    ) -> List[ndarray]:
        """Calculate power of values."""
        ...
    

    def abs_values(
        self,
        
    ) -> List[ndarray]:
        """Calculate absolute values."""
        ...
    

    def round_values(
        self,
        decimals: int = 0
    ) -> List[ndarray]:
        """Round values to specified decimals."""
        ...
    

    def normalize(
        self,
        method: str = 'minmax'
    ) -> List[ndarray]:
        """Normalize values using specified method."""
        ...
    

    def interpolate(
        self,
        base_column_name: str = 'step',
        x_values: Optional[list[float]] = None,
        point_count: Optional[int] = None,
        method: str = 'linear',
        columns: Optional[list[str]] = None
    ) -> "CollectionListOperations[C]":
        """指定した列の値に基づいてデータを内挿します"""
        ...
    

    def split_by_integers(
        self,
        markers: Union[list[int], ndarray]
    ) -> List[list[ndarray]]:
        """Calculate split indices based on integer markers."""
        ...
    

    def split_at_indices(
        self,
        indices: Union[int, list[int]]
    ) -> List[list[slice]]:
        """Calculate split slices based on indices."""
        ...
    

    def get_column_coordinates(
        self,
        column: str
    ) -> List[dict[str, Optional[float]]]:
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
    ) -> "CollectionListOperations[C]":
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
        
    ) -> List[list[str]]:
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
    ) -> "CollectionListOperations[C]":
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
    ) -> List[float]:
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
    

    def find_nearest_neighbors(
        self,
        column: str,
        n_neighbors: int = 3,
        result_column: Optional[str] = None
    ) -> "CollectionListOperations[C]":
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
    ) -> "CollectionListOperations[C]":
        """座標情報に基づいてクラスタリングを行います

列の座標位置に基づいて、類似した位置にある列をグループ化します。
クラスタリング結果はメタデータに保存され、各列のクラスタ情報も追加されます。

Args:
    collection: 座標コレクション
    n_clusters: クラスタ数
    columns: クラスタリング対象の列名リスト（None の場合は座標を持つ全列）
    result_column: 結果列名
    algorithm: クラスタリングアルゴリズム（"kmeans"）

Returns:
    CoordinateCollection: クラスタリング結果を含むコレクション

Raises:
    ValueError: クラスタ数が列数より多い場合、または有効な座標データがない場合"""
        ...
    

    def distance(
        self,
        column1: str,
        column2: str
    ) -> List[float]:
        """calculate_distance のエイリアス"""
        ...
    

    def nearest_neighbors(
        self,
        column: str,
        n_neighbors: int = 3,
        result_column: Optional[str] = None
    ) -> "CollectionListOperations[C]":
        """find_nearest_neighbors のエイリアス"""
        ...
    

    def cluster(
        self,
        n_clusters: int = 2,
        columns: Optional[list[str]] = None,
        result_column: str = 'cluster',
        algorithm: str = 'kmeans'
    ) -> "CollectionListOperations[C]":
        """spatial_clustering のエイリアス"""
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
    ) -> "CollectionListOperations[C]":
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
    ) -> "CollectionListOperations[C]":
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
    ) -> "CollectionListOperations[C]":
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
    

    def interp_point(
        self,
        x: float,
        y: float,
        z: Optional[float] = None,
        target_columns: Optional[list[str]] = None,
        method: str = 'inverse_distance',
        power: float = 2.0,
        result_prefix: str = 'interp_'
    ) -> "CollectionListOperations[C]":
        """interpolate_at_point のエイリアス"""
        ...
    

    def interp_grid(
        self,
        x_range: tuple[float, float],
        y_range: tuple[float, float],
        grid_size: tuple[int, int] = (10, 10),
        target_column: Optional[str] = None,
        method: str = 'inverse_distance',
        power: float = 2.0,
        result_prefix: str = 'grid_'
    ) -> "CollectionListOperations[C]":
        """interpolate_grid のエイリアス"""
        ...
    

    def calculate_rosette_strains(
        self,
        rosette_name: Optional[str] = None,
        columns: Optional[list[str]] = None,
        rosette_type: str = 'rectangular',
        orientation: float = 0.0,
        prefix: Optional[str] = None
    ) -> "CollectionListOperations[C]":
        """ロゼットひずみ計算 (主ひずみ・主応力方向)

3軸ひずみゲージの値から、最大・最小主ひずみ、最大せん断ひずみ、主ひずみ方向を計算します。

Args:
    collection: ひずみコレクション
    rosette_name: 定義済みのロゼット名（metadataから情報を取得）
    columns: ゲージのカラム名リスト [e1, e2, e3]。
             rosette_name指定時は無視されます。
             直交の場合: 0, 45, 90度
             デルタの場合: 0, 60, 120度
    rosette_type: ロゼットタイプ ('rectangular' or 'delta')
                  rosette_name指定時はmetadataが優先されます。
    orientation: 第1ゲージの設置角度（X軸基準、反時計回り、度単位）
                 rosette_name指定時はmetadataが優先されます。
    prefix: 結果カラム名の接頭辞。デフォルトは rosette_name または "rosette"

Returns:
    StrainCollection: 計算結果（e_max, e_min, gamma_max, theta）が追加されたコレクション"""
        ...
    

    def plot_rosette_vectors(
        self,
        rosette_name: str,
        step_index: int = 0,
        scale: float = 1.0,
        ax: Optional[Any] = None
    ) -> List[Any]:
        """ロゼットの主ひずみベクトルをプロットする

指定したステップにおける主ひずみ（最大・最小）の大きさと方向を、
ロゼットの設置位置にベクトルとして描画します。
(事前に calculate_rosette_strains を実行しておく必要があります)

Args:
    collection: ひずみコレクション
    rosette_name: ロゼット名
    step_index: プロットするステップのインデックス
    scale: ベクトルの長さのスケール
    ax: MatplotlibのAxesオブジェクト（指定がない場合は新規作成）

Returns:
    Axes: プロットされたAxesオブジェクト"""
        ...
    

    def iplot_rosette_vectors(
        self,
        rosette_name: str,
        step_index: int = 0,
        scale: float = 1.0,
        fig: Optional[Any] = None
    ) -> List[Any]:
        """ロゼットの主ひずみベクトルをインタラクティブにプロットする (Plotly)"""
        ...
    

    def calculate_stress(
        self,
        load_column: str,
        area: float,
        result_column: str = 'stress',
        unit: str = 'MPa'
    ) -> "CollectionListOperations[C]":
        """応力を計算する (Stress = Load / Area)

Args:
    collection: ひずみコレクション
    load_column: 荷重データのカラム名
    area: 断面積
    result_column: 結果を格納するカラム名
    unit: 結果の単位

Returns:
    StrainCollection: 応力カラムが追加されたコレクション"""
        ...
    

    def analyze_material_properties(
        self,
        stress_column: str,
        strain_column: str,
        lateral_strain_column: Optional[str] = None,
        elastic_range: tuple[float, float] = (0.0005, 0.0025),
        offset: float = 0.002,
        result_prefix: str = 'material'
    ) -> "CollectionListOperations[C]":
        """材料特性（ヤング率、降伏点、ポアソン比）を解析する

Args:
    collection: ひずみコレクション
    stress_column: 応力カラム名
    strain_column: ひずみ（縦）カラム名
    lateral_strain_column: 横ひずみカラム名（ポアソン比計算用、任意）
    elastic_range: ヤング率計算に使用するひずみ範囲 (start, end)
    offset: 耐力計算用のオフセットひずみ量 (デフォルト 0.002 = 0.2%)
    result_prefix: 結果名の接頭辞

Returns:
    StrainCollection: 計算結果（ScalarResult, PointResult）が追加されたコレクション"""
        ...
    

    def get_load_column(
        self,
        
    ) -> List[str]:
        """荷重データのカラム名を取得

Args:
    collection: 荷重-変位コレクション

Returns:
    str: 荷重データのカラム名"""
        ...
    

    def get_displacement_column(
        self,
        
    ) -> List[str]:
        """変位データのカラム名を取得

Args:
    collection: 荷重-変位コレクション

Returns:
    str: 変位データのカラム名"""
        ...
    

    def get_load_data(
        self,
        
    ) -> List[ndarray]:
        """荷重データを取得

Args:
    collection: 荷重-変位コレクション

Returns:
    np.ndarray: 荷重データの配列"""
        ...
    

    def get_displacement_data(
        self,
        
    ) -> List[ndarray]:
        """変位データを取得

Args:
    collection: 荷重-変位コレクション

Returns:
    np.ndarray: 変位データの配列"""
        ...
    

    def get_valid_data_mask(
        self,
        
    ) -> List[ndarray]:
        """有効なデータポイントのマスクを取得

Args:
    collection: 荷重-変位コレクション

Returns:
    np.ndarray: 有効なデータのブールマスク"""
        ...
    

    def get_valid_data(
        self,
        
    ) -> List[tuple[ndarray, ndarray]]:
        """有効な荷重と変位のデータ組を取得

Args:
    collection: 荷重-変位コレクション

Returns:
    Tuple[np.ndarray, np.ndarray]: 有効な(変位, 荷重)データの組"""
        ...
    

    def calculate_slopes(
        self,
        result_column: Optional[str] = None,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None
    ) -> "CollectionListOperations[C]":
        """変位と荷重の間の傾きを計算

変位と荷重の間の点ごとの傾きを計算します。
デフォルトでは変位列を独立変数（X軸）、荷重列を従属変数（Y軸）として使用します。

Args:
    collection: 荷重-変位コレクション
    result_column: 結果を格納する列名
    x_column: X軸データの列名（指定がない場合は変位列を使用）
    y_column: Y軸データの列名（指定がない場合は荷重列を使用）

Returns:
    LoadDisplacementCollection: 傾きデータを含むコレクション"""
        ...
    

    def calculate_stiffness(
        self,
        range_start: float = 0.2,
        range_end: float = 0.8,
        method: str = 'linear_regression'
    ) -> List[float]:
        """荷重-変位曲線から剛性を計算

指定された範囲内のデータを使用して荷重-変位間の剛性（傾き）を計算します。

Args:
    collection: 荷重-変位コレクション
    range_start: 最大荷重に対する計算開始点の割合
    range_end: 最大荷重に対する計算終了点の割合
    method: 剛性計算方法 ("linear_regression" または "secant")

Returns:
    float: 剛性値"""
        ...
    

    def find_yield_point(
        self,
        method: str = 'offset',
        offset_value: float = 0.002,
        range_start: float = 0.1,
        range_end: float = 0.3,
        factor: float = 0.33,
        result_prefix: Optional[str] = 'yield',
        debug_mode: bool = False,
        fail_silently: bool = False
    ) -> "CollectionListOperations[C]":
        """降伏点を計算

荷重-変位データから降伏点を計算します。
オフセット法または一般降伏法から選択できます。

Args:
    collection: 荷重-変位コレクション
    method: 計算方法 ('offset', 'general')
    offset_value: オフセット降伏法でのオフセット量
    range_start: 初期勾配計算の範囲開始（最大荷重に対する比率）
    range_end: 初期勾配計算の範囲終了（最大荷重に対する比率）
    factor: 一般降伏法での勾配比率
    result_prefix: 結果列の接頭辞
    debug_mode: 詳細な計算過程情報を出力するかどうか
    fail_silently: 降伏点が見つからない場合に例外を発生させずに情報を返すかどうか

Returns:
    LoadDisplacementCollection: 降伏点情報または計算過程情報を含むコレクション

Raises:
    ValueError: 降伏点が見つかりず、fail_silently=False の場合"""
        ...
    

    def stiffness(
        self,
        range_start: float = 0.2,
        range_end: float = 0.8,
        method: str = 'linear_regression'
    ) -> List[float]:
        """calculate_stiffness のエイリアス"""
        ...
    

    def yield_point(
        self,
        method: str = 'offset',
        offset_value: float = 0.002,
        range_start: float = 0.1,
        range_end: float = 0.3,
        factor: float = 0.33,
        result_prefix: Optional[str] = 'yield',
        debug_mode: bool = False,
        fail_silently: bool = False
    ) -> "CollectionListOperations[C]":
        """find_yield_point のエイリアス"""
        ...
    

    def cycle_count(
        self,
        column: Optional[str] = None,
        step: float = 0.5,
        result_column: Optional[str] = None
    ) -> "CollectionListOperations[C]":
        """データの荷重符号反転からサイクル数をカウント

荷重の符号変化（正負の反転）からサイクル数をカウントし、
新しい列として追加します。

Args:
    collection: 荷重-変位コレクション
    column: サイクルをカウントする列（指定がない場合は荷重列を使用）
    step: サイクルカウントの増分
    result_column: 結果を格納する列名

Returns:
    LoadDisplacementCollection: サイクル数を含むコレクション"""
        ...
    

    def split_by_cycles(
        self,
        cycle_column: Optional[str] = None
    ) -> "CollectionListOperations[C]":
        """サイクル番号ごとにデータを分割

データをサイクル番号ごとに分割し、各サイクルの
荷重-変位コレクションのリストを返します。

Args:
    collection: 荷重-変位コレクション
    cycle_column: サイクル番号を含む列名（指定がない場合は自動検出/生成）

Returns:
    List[LoadDisplacementCollection]: サイクルごとに分割されたコレクションのリスト"""
        ...
    

    def analyze_hysteresis(
        self,
        cycle_column: Optional[str] = None
    ) -> "CollectionListOperations[C]":
        """ヒステリシスループ解析（エネルギー散逸の計算）

各サイクルのヒステリシスループ面積（エネルギー散逸）を計算し、
サイクルごとの統計量を含む新しいコレクションを返します。

Args:
    collection: 荷重-変位コレクション
    cycle_column: サイクル番号列（指定がない場合は自動検出）

Returns:
    LoadDisplacementCollection: サイクル番号、エネルギー、最大荷重などを列として持つコレクション"""
        ...
    

    def analyze_stiffness_degradation(
        self,
        cycle_column: Optional[str] = None
    ) -> "CollectionListOperations[C]":
        """剛性低下解析（サイクルごとの割線剛性）

各サイクルの最大荷重点と最小荷重点を結ぶ直線の傾き（割線剛性）を計算し、
剛性の推移を示す新しいコレクションを返します。

Args:
    collection: 荷重-変位コレクション
    cycle_column: サイクル番号列（指定がない場合は自動検出）

Returns:
    LoadDisplacementCollection: サイクル番号、剛性を含むコレクション"""
        ...
    

    def find_peaks_and_valleys(
        self,
        column: Optional[str] = None,
        result_column: str = 'peak_valley',
        distance: int = 1,
        threshold: Optional[float] = None,
        prominence: Optional[float] = None
    ) -> "CollectionListOperations[C]":
        """ピーク（極大値）とバレー（極小値）を検出します

指定された列の極大値と極小値を検出し、
1（ピーク）、-1（バレー）、0（その他）のフラグを持つ新しい列を追加します。

Args:
    collection: 荷重-変位コレクション
    column: 検出対象の列（指定がない場合は荷重列を使用）
    result_column: 結果を格納する列名
    distance: ピーク間の最小距離（インデックス数）
    threshold: 隣接点との最小差
    prominence: ピークの突出度（未実装: scipyが必要なため）

Returns:
    LoadDisplacementCollection: ピーク/バレーフラグを含むコレクション"""
        ...
    

    def get_curve_data(
        self,
        curve_name: str
    ) -> List[dict[str, Any]]:
        """メタデータに格納された曲線データを取得

Args:
    collection: 荷重-変位コレクション
    curve_name: 曲線名（例: "skeleton_curve", "cumulative_curve"）

Returns:
    Dict[str, Any]: 曲線データ（x, y, metadataを含む辞書）

Raises:
    ValueError: 指定した曲線が存在しない場合"""
        ...
    

    def get_curve_columns(
        self,
        curve_name: str
    ) -> List[tuple[Optional[Column], Optional[Column]]]:
        """メタデータに格納された曲線データをColumnオブジェクトとして取得

Args:
    collection: 荷重-変位コレクション
    curve_name: 曲線名（例: "skeleton_curve", "cumulative_curve"）

Returns:
    Tuple[Optional[Column], Optional[Column]]:
        (x軸のColumn, y軸のColumn)のタプル。曲線が存在しない場合は(None, None)

Raises:
    ValueError: 指定した曲線データにColumnが含まれていない場合
    ValueError: 指定した曲線が存在しない場合"""
        ...
    

    def list_available_curves(
        self,
        
    ) -> List[list[str]]:
        """利用可能な曲線の一覧を取得

Args:
    collection: 荷重-変位コレクション

Returns:
    List[str]: 利用可能な曲線名のリスト"""
        ...
    

    def create_skeleton_curve(
        self,
        has_decrease: bool = False,
        decrease_type: str = 'envelope',
        cycle_column: Optional[str] = None,
        result_load_column: Optional[str] = None,
        result_disp_column: Optional[str] = None,
        store_as_columns: bool = False
    ) -> "CollectionListOperations[C]":
        """荷重-変位データからスケルトン曲線を作成

複数サイクルの荷重-変位データから、包絡線（スケルトン曲線）を作成します。
スケルトン曲線は、各サイクルの最大応答値を結んだ曲線です。

デフォルトでは、スケルトン曲線はメタデータの "curves" セクションに格納されます。
これにより、列の長さが異なるデータを格納できます。
また、メタデータ内にColumnオブジェクトとしても格納されるため、いつでも取得可能です。

Args:
    collection: 荷重-変位コレクション
    has_decrease: 減少部分も含めるか
    decrease_type: 減少部分の処理方法 ('envelope', 'continuous_only', 'both')
    cycle_column: サイクル列名（指定なしの場合は自動生成）
    result_load_column: 結果の荷重列名（指定なしの場合は自動生成）
    result_disp_column: 結果の変位列名（指定なしの場合は自動生成）
    store_as_columns: Trueの場合、旧形式との互換性のために列としても格納

Returns:
    LoadDisplacementCollection: スケルトン曲線データを含むコレクション"""
        ...
    

    def create_cumulative_curve(
        self,
        cycle_column: Optional[str] = None,
        result_load_column: Optional[str] = None,
        result_disp_column: Optional[str] = None,
        store_as_columns: bool = False
    ) -> "CollectionListOperations[C]":
        """荷重-変位データから累積曲線を作成

複数サイクルの荷重-変位データから、累積変形曲線を作成します。
累積曲線は、各サイクルの変形を累積的に加算した曲線です。

デフォルトでは、累積曲線はメタデータの "curves" セクションに格納されます。
これにより、列の長さが異なるデータを格納できます。
また、メタデータ内にColumnオブジェクトとしても格納されるため、いつでも取得可能です。

Args:
    collection: 荷重-変位コレクション
    cycle_column: サイクル列名（指定なしの場合は自動生成）
    result_load_column: 結果の荷重列名（指定なしの場合は自動生成）
    result_disp_column: 結果の変位列名（指定なしの場合は自動生成）
    store_as_columns: Trueの場合、旧形式との互換性のために列としても格納

Returns:
    LoadDisplacementCollection: 累積曲線データを含むコレクション"""
        ...
    

    def export_curve_to_csv(
        self,
        curve_name: str,
        file_path: str,
        columns: tuple[str, str] = ('x', 'y'),
        encoding: str = 'utf-8',
        include_header: bool = True
    ) -> List[None]:
        """メタデータに格納された曲線データを CSV ファイルにエクスポートします。

Args:
    collection: LoadDisplacementCollection オブジェクト
    curve_name: エクスポートする曲線名（"skeleton_curve" や "cumulative_curve" など）
    file_path: 出力先の CSV ファイルパス
    columns: エクスポートするカラム名タプル（デフォルトは ("x", "y")）
    encoding: ファイルエンコーディング（デフォルトは "utf-8"）
    include_header: ヘッダー行を含めるかどうか

Raises:
    ValueError: 指定した曲線が存在しない場合、またはデータが不正な場合
    IOError: ファイル書き込みに失敗した場合"""
        ...
    

    def plot_load_displacement(
        self,
        ax: Optional[Axes] = None,
        **kwargs
    ) -> List[Axes]:
        """荷重-変位曲線をプロットします

荷重-変位データを二次元グラフとしてプロットします。
既存の軸オブジェクトを指定することも、新しく作成することもできます。

Args:
    collection: 荷重-変位コレクション
    ax: プロット先の軸（None の場合は新規作成）
    **kwargs: matplotlib の plot 関数に渡す追加引数

Returns:
    Axes: プロットされた軸オブジェクト"""
        ...
    

    def plot_skeleton_curve(
        self,
        plot_original: bool = True,
        skeleton_load_column: Optional[str] = None,
        skeleton_disp_column: Optional[str] = None,
        ax: Optional[Axes] = None,
        original_kwargs: Optional[dict[str, Any]] = None,
        skeleton_kwargs: Optional[dict[str, Any]] = None
    ) -> List[Axes]:
        """スケルトン曲線をプロットします

create_skeleton_curve 関数で作成したスケルトン曲線をプロットします。
元の荷重-変位データと比較して表示することも可能です。

スケルトン曲線データは、列または metadata["curves"]["skeleton_curve"] から取得します。
メタデータに格納されている場合はそちらが優先されます。

Args:
    collection: スケルトン曲線を含む荷重-変位コレクション
    plot_original: 元の荷重-変位データもプロットするかどうか
    skeleton_load_column: スケルトン曲線の荷重列名（None の場合は自動検出）
    skeleton_disp_column: スケルトン曲線の変位列名（None の場合は自動検出）
    ax: プロット先の軸（None の場合は新規作成）
    original_kwargs: 元データプロット用の追加引数
    skeleton_kwargs: スケルトン曲線プロット用の追加引数

Returns:
    Axes: プロットされた軸オブジェクト

Raises:
    ValueError: スケルトン曲線データが列にもメタデータにも見つからない場合"""
        ...
    

    def plot_cumulative_curve(
        self,
        plot_original: bool = True,
        cumulative_load_column: Optional[str] = None,
        cumulative_disp_column: Optional[str] = None,
        ax: Optional[Axes] = None,
        original_kwargs: Optional[dict[str, Any]] = None,
        cumulative_kwargs: Optional[dict[str, Any]] = None
    ) -> List[Axes]:
        """累積曲線をプロットします

create_cumulative_curve 関数で作成した累積曲線をプロットします。
元の荷重-変位データと比較して表示することも可能です。

累積曲線データは、列または metadata["curves"]["cumulative_curve"] から取得します。
メタデータに格納されている場合はそちらが優先されます。

Args:
    collection: 累積曲線を含む荷重-変位コレクション
    plot_original: 元の荷重-変位データもプロットするかどうか
    cumulative_load_column: 累積曲線の荷重列名（None の場合は自動検出）
    cumulative_disp_column: 累積曲線の変位列名（None の場合は自動検出）
    ax: プロット先の軸（None の場合は新規作成）
    original_kwargs: 元データプロット用の追加引数
    cumulative_kwargs: 累積曲線プロット用の追加引数

Returns:
    Axes: プロットされた軸オブジェクト

Raises:
    ValueError: 累積曲線データが列にもメタデータにも見つからない場合"""
        ...
    

    def plot_yield_point(
        self,
        ax: Optional[Axes] = None,
        plot_original_data: bool = True,
        plot_initial_slope: bool = True,
        plot_offset_line: bool = True,
        result_prefix: str = 'yield',
        **kwargs
    ) -> List[Axes]:
        """降伏点解析結果をプロットします

find_yield_point 関数で解析した降伏点情報をビジュアル化します。
元データ、初期勾配線、オフセット線などを表示できます。

Args:
    collection: 降伏点情報を含む荷重-変位コレクション
    ax: プロット先の軸（None の場合は新規作成）
    plot_original_data: 元の荷重-変位データもプロットするかどうか
    plot_initial_slope: 初期勾配線をプロットするかどうか
    plot_offset_line: オフセット線をプロットするかどうか（オフセット法の場合）
    result_prefix: 降伏点データの接頭辞
    **kwargs: matplotlib の plot 関数に渡す追加引数

Returns:
    Axes: プロットされた軸オブジェクト"""
        ...
    

    def plot_yield_analysis_details(
        self,
        ax: Optional[Axes] = None,
        **kwargs
    ) -> List[Axes]:
        """降伏点解析の詳細情報をプロットします

find_yield_point 関数で解析した降伏点情報の詳細をビジュアル化します。
初期勾配の計算範囲などの追加情報も表示します。

Args:
    collection: 降伏点情報を含む荷重-変位コレクション
    ax: プロット先の軸（None の場合は新規作成）
    **kwargs: matplotlib の plot 関数に渡す追加引数

Returns:
    Axes: プロットされた軸オブジェクト"""
        ...
    

    def compare_yield_methods(
        self,
        methods: list[dict[str, Any]] = None,
        ax: Optional[Axes] = None,
        **kwargs
    ) -> List[Axes]:
        """複数の降伏点計算方法を比較してプロットします

異なるパラメータや手法で計算した複数の降伏点を
一つのグラフ上に表示して比較できます。

Args:
    collection: 荷重-変位コレクション
    methods: 計算方法とパラメータのリスト。例:
             [{"method": "offset", "offset_value": 0.002},
              {"method": "general", "factor": 0.33}]
    ax: プロット先の軸（None の場合は新規作成）
    **kwargs: プロット関数に渡す追加引数

Returns:
    Axes: プロットされた軸オブジェクト"""
        ...
    

    def plot_multiple_curves(
        self,
        curves: list[dict[str, Any]],
        ax: Optional[Axes] = None,
        **kwargs
    ) -> List[Axes]:
        """複数の曲線を指定してプロットします

Args:
    collection: 荷重-変位コレクション
    curves: プロットする曲線の設定リスト
            [
                {"type": "original", "kwargs": {...}},
                {"type": "skeleton", "kwargs": {...}},
                {"type": "cumulative", "kwargs": {...}}
            ]
    ax: プロット先の軸（None の場合は新規作成）
    **kwargs: その他のオプション

Returns:
    Axes: プロットされた軸オブジェクト"""
        ...
    
