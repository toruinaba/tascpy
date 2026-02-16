# 自動生成されたstrainドメインのスタブファイル - 編集しないでください
from typing import Optional, Union, List, Dict, Any, Callable, TypeVar, cast, Generic, overload, Literal
from ..core.collection import ColumnCollection
from ..domains.strain import StrainCollection
from .proxy_base import CollectionOperationsBase
from .list_proxy import CollectionListOperations
from .core import CoreCollectionOperations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .load_displacement import LoadDisplacementCollectionOperations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .coordinate import CoordinateCollectionOperations

class StrainCollectionOperations(CollectionOperationsBase[StrainCollection]):
    """strainドメインの操作メソッドスタブ定義
    
    このクラスはPylanceの型チェックとオートコンプリートのためのスタブです。
    実際の実行には使用されません。
    """

    def end(self) -> StrainCollection:
        """操作チェーンを終了し、最終的なColumnCollectionを取得"""
        ...

    def debug(self, message: Optional[str] = None) -> "StrainCollectionOperations":
        """デバッグメッセージを表示
        
        Args:
            message: デバッグメッセージ
        
        Returns:
            StrainCollectionOperations: 自身を返す
        """
        ...


    def get_column_coordinates(
        self,
        column: str
    ) -> dict[str, Optional[float]]:
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
    ) -> "StrainCollectionOperations":
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
        
    ) -> list[str]:
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
    ) -> "StrainCollectionOperations":
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
    ValueError: 座標情報がない場合"""
        ...
    

    def find_nearest_neighbors(
        self,
        column: str,
        n_neighbors: int = 3,
        result_column: Optional[str] = None
    ) -> "StrainCollectionOperations":
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
    ) -> "StrainCollectionOperations":
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
    ) -> float:
        """calculate_distance のエイリアス"""
        ...
    

    def nearest_neighbors(
        self,
        column: str,
        n_neighbors: int = 3,
        result_column: Optional[str] = None
    ) -> "StrainCollectionOperations":
        """find_nearest_neighbors のエイリアス"""
        ...
    

    def cluster(
        self,
        n_clusters: int = 2,
        columns: Optional[list[str]] = None,
        result_column: str = 'cluster',
        algorithm: str = 'kmeans'
    ) -> "StrainCollectionOperations":
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
    ) -> "StrainCollectionOperations":
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
    ) -> "StrainCollectionOperations":
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
    ) -> "StrainCollectionOperations":
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
    ) -> "StrainCollectionOperations":
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
    ) -> "StrainCollectionOperations":
        """interpolate_grid のエイリアス"""
        ...
    

    def calculate_rosette_strains(
        self,
        rosette_name: Optional[str] = None,
        columns: Optional[list[str]] = None,
        rosette_type: str = 'rectangular',
        orientation: float = 0.0,
        prefix: Optional[str] = None
    ) -> "StrainCollectionOperations":
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
    ) -> Any:
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
    ) -> Any:
        """ロゼットの主ひずみベクトルをインタラクティブにプロットする (Plotly)"""
        ...
    

    def calculate_stress(
        self,
        load_column: str,
        area: float,
        result_column: str = 'stress',
        unit: str = 'MPa'
    ) -> "StrainCollectionOperations":
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
    ) -> "StrainCollectionOperations":
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
    

    def filter_by_value(
        self,
        value: Any,
        tolerance: Optional[float] = None
    ) -> list[bool]:
        """指定された列の値が指定された値と等しい行をフィルタリングします"""
        ...
    

    def filter_out_none(
        self,
        columns: Optional[list[str]] = None,
        mode: str = 'any'
    ) -> list[bool]:
        """None値およびNaN値を含む行をフィルタリングして除外します"""
        ...
    

    def remove_consecutive_duplicates_across(
        self,
        columns: Optional[list[str]] = None,
        dup_type: str = 'all'
    ) -> list[int]:
        """複数の列間で共通の連続重複データを削除した新しい ColumnCollection オブジェクトを返します"""
        ...
    

    def remove_outliers(
        self,
        window_size: int = 3,
        threshold: float = 0.5,
        edge_handling: str = 'asymmetric',
        min_abs_value: float = 1e-10,
        scale_factor: float = 1.0
    ) -> "CollectionListOperations[StrainCollectionOperations]":
        """異常値を検出して除去した新しいコレクションを返します"""
        ...
    

    def filter_by_condition(
        self,
        condition: <built-in function callable>
    ) -> "CollectionListOperations[StrainCollectionOperations]":
        """指定された列の値が条件を満たす行をフィルタリングします"""
        ...
    

    def remove_steps(
        self,
        steps: list[Any],
        tolerance: Optional[float] = None
    ) -> list[bool]:
        """指定されたステップ値を持つ行を削除します"""
        ...
    

    def filter_val(
        self,
        column_name: str,
        value: Any,
        tolerance: Optional[float] = None
    ) -> "StrainCollectionOperations":
        """filter_by_value のエイリアス"""
        ...
    

    def filter_cond(
        self,
        column_name: str,
        condition: <built-in function callable>
    ) -> "StrainCollectionOperations":
        """filter_by_condition のエイリアス"""
        ...
    

    def rm_outliers(
        self,
        column: str,
        window_size: int = 3,
        threshold: float = 0.5,
        edge_handling: str = 'asymmetric',
        min_abs_value: float = 1e-10,
        scale_factor: float = 1.0
    ) -> "StrainCollectionOperations":
        """remove_outliers のエイリアス"""
        ...
    

    def search_by_value(
        self,
        op_str: str,
        value: Any
    ) -> list[int]:
        """値による検索を行います

指定された列の値に対して比較演算子を適用し、条件に一致する行のインデックスを返します。

Args:
    vals: 列の値 (inject_columnsにより注入)
    op_str: 演算子文字列 (">", "<", ">=", "<=", "==", "!=")
    value: 比較する値

Returns:
    List[int]: 条件に一致するインデックスのリスト"""
        ...
    

    def search_by_range(
        self,
        min_value: Any,
        max_value: Any,
        inclusive: bool = True
    ) -> list[int]:
        """範囲による検索を行います

指定された列の値が特定の範囲内にある行のインデックスを返します。

Args:
    vals: 列の値
    min_value: 最小値
    max_value: 最大値
    inclusive: 境界値を含めるかどうか

Returns:
    List[int]: 条件に一致するインデックスのリスト"""
        ...
    

    def search_by_step_range(
        self,
        min: Union[int, float],
        max: Union[int, float],
        inclusive: bool = True,
        by_step_value: bool = True,
        tolerance: Optional[float] = None
    ) -> Union[list[int], tuple]:
        """ステップ範囲による検索を行います"""
        ...
    

    def search_by_condition(
        self,
        condition_func: Callable[[Dict[str, Any]], bool],
        columns: Optional[list[str]] = None
    ) -> list[int]:
        """条件関数による検索を行います

行ごとのデータを辞書として受け取り、条件関数が True を返す行のインデックスを返します。
columns引数を指定すると、その列のみがデータ辞書に含まれます（パフォーマンス最適化）。

Args:
    data: 列データの辞書 (inject_columnsにより注入)
    condition_func: 行データ辞書を受け取り、boolを返す関数
    columns: 使用する列名のリスト (Noneの場合は全列)"""
        ...
    

    def search_missing_values(
        self,
        columns: Optional[list[str]] = None
    ) -> list[int]:
        """欠損値がある行を検索します

指定された列に欠損値（None または NaN）を含む行のインデックスを返します。"""
        ...
    

    def search_top_n(
        self,
        n: int,
        descending: bool = True
    ) -> list[int]:
        """指定した列の上位 N 件を検索します"""
        ...
    

    def plot(
        self,
        y_values: ndarray,
        x_label: str,
        y_label: str,
        title: str,
        ax: Optional[Axes] = None,
        **kwargs
    ) -> Axes:
        """グラフを描画します

(backend_mpl.plot を使用)
Args:
    x_values, y_values, x_label, y_label, title: @inject_plot_data により注入されます"""
        ...
    

    def visualize_outliers(
        self,
        column: str,
        window_size: int = 3,
        threshold: float = 0.5,
        x_column: Optional[str] = None,
        highlight_color: str = 'red',
        plot_type: str = 'scatter',
        show_normal: bool = True,
        normal_color: str = 'blue',
        normal_alpha: float = 0.6,
        outlier_marker: str = 'o',
        outlier_size: int = 80,
        ax: Optional[Axes] = None,
        edge_handling: str = 'asymmetric',
        min_abs_value: float = 1e-10,
        scale_factor: float = 1.0,
        **kwargs
    ) -> "StrainCollectionOperations":
        """異常値を可視化します

指定された列の異常値を検出し、視覚的に強調表示します。
元のデータをプロットし、その上に異常値のみマーカーで強調表示します。
detect_outliers 関数を内部で使用して異常値を特定します。

Args:
    collection: 対象コレクション
    column: 異常値を検出する列の名前
    window_size: 移動平均のウィンドウサイズ（奇数推奨）
    threshold: 異常値とみなす移動平均との差分比率の閾値
    x_column: x軸の列名（None の場合は step を使用）
    highlight_color: 異常値のマーカー色
    plot_type: 通常データのプロットタイプ（'scatter' または 'line'）
    show_normal: 通常のデータポイントも表示するかどうか
    normal_color: 通常のデータポイントの色
    normal_alpha: 通常のデータポイントの透明度
    outlier_marker: 異常値のマーカースタイル
    outlier_size: 異常値のマーカーサイズ
    ax: 既存の Axes オブジェクト（None の場合は新しい図を作成）
    edge_handling: エッジ処理方法（"symmetric", "asymmetric"）
    min_abs_value: 比率計算時の最小絶対値
    scale_factor: スケール調整係数
    **kwargs: プロット関数に渡す追加のキーワード引数

Returns:
    ColumnCollection: 異常値検出フラグを含む新しいコレクション

Examples:
    >>> # 基本的な異常値の可視化
    >>> collection.ops.visualize_outliers('pressure_data').end()
    >>>
    >>> # 異常値検出パラメータのカスタマイズ
    >>> collection.ops.visualize_outliers(
    ...     'temperature',
    ...     window_size=5,
    ...     threshold=0.3
    ... ).end()
    >>>
    >>> # 表示スタイルのカスタマイズ
    >>> collection.ops.visualize_outliers(
    ...     'sensor_value',
    ...     highlight_color='magenta',
    ...     outlier_marker='x',
    ...     outlier_size=100,
    ...     show_normal=False
    ... ).end()
    >>>
    >>> # 複数の可視化を一つの図に表示
    >>> fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
    >>> collection.ops.visualize_outliers(
    ...     'pressure', window_size=5, ax=ax1
    ... ).end()
    >>> collection.ops.visualize_outliers(
    ...     'temperature', threshold=0.3, ax=ax2
    ... ).end()
    >>> plt.tight_layout()
    >>> plt.show()  # 最後にまとめて表示"""
        ...
    

    def plot_const_x(
        self,
        x_values: list[float],
        y_columns: list[str],
        ax: Optional[Axes] = None,
        **kwargs
    ) -> Axes:
        """指定されたX値（定数リスト）に対して、複数の列の値をYとしてプロットします
注: 単一行のコレクションに対して使用することを想定しています

Args:
    collection: ColumnCollection オブジェクト（通常は1行）
    x_values: X軸の値のリスト
    y_columns: Y軸として使用する列名のリスト
    ax: Axesオブジェクト
    **kwargs: plotの引数

Returns:
    ColumnCollection: 元のコレクション"""
        ...
    

    def iplot(
        self,
        y_values: ndarray,
        x_label: str,
        y_label: str,
        title: str,
        fig: Optional[Any] = None,
        **kwargs
    ) -> Any:
        """インタラクティブなグラフを描画します (Plotly使用)

Args:
    x_values, y_values, x_label, y_label, title: @inject_plot_data により注入されます
    fig: 既存の Plotly Figure オブジェクト
    **kwargs: Plotly backend に渡す追加引数

Returns:
    Any: Plotly Figure オブジェクト (ノートブック環境では自動的に表示される)"""
        ...
    

    def select(
        self,
        columns: Optional[list[str]] = None,
        indices: Optional[list[int]] = None,
        steps: Optional[list[Union[int, float]]] = None,
        by_step_value: bool = True,
        tolerance: Optional[float] = None
    ) -> Union[list[int], tuple[list[int], dict[str, Any]]]:
        """指定した列名、行インデックス、またはステップ値に基づいてデータを抽出します

複数の方法でデータ抽出を行うことができる汎用的な選択操作です。
列の選択、インデックスによる行の選択、ステップ値による行の選択を組み合わせて使用できます。

Args:
    step_values: ステップ値のリストまたは配列 (@inject_step_valuesにより注入)
    columns: (デコレータで処理) 抽出する列名のリスト。None の場合は全列が対象
    indices: 抽出する行インデックスのリスト。None の場合は全行が対象
    steps: 抽出するステップのリスト。None の場合は全行が対象
        by_step_value=True の場合：ステップ値として解釈
        by_step_value=False の場合：インデックスとして解釈
    by_step_value: True の場合は steps をステップ値として解釈、False の場合はインデックスとして解釈
    tolerance: ステップ値検索時の許容範囲（by_step_value=True の場合のみ有効）

Returns:
    Union[List[int], Tuple[List[int], Dict[str, Any]]]: 
        抽出する行インデックスのリスト、および更新するメタデータのタプル"""
        ...
    

    def select_step(
        self,
        steps: list[Union[int, float]],
        columns: Optional[list[str]] = None,
        by_step_value: bool = True,
        tolerance: Optional[float] = None
    ) -> "StrainCollectionOperations":
        """指定した列名とステップ番号に基づいてデータを抽出します (後方互換性)"""
        ...
    

    def fetch_near_step(
        self,
        value: float,
        **kwargs
    ) -> "CollectionListOperations[StrainCollectionOperations]":
        """指定された値に最も近い行を取得します

inject_columnsにより、第一引数がカラム名の場合はそのカラムの値が、
そうでない場合(数値のみ)はデフォルト(通常はStep)の値が注入されます。

Args:
    values: 検索対象の値の配列 (@inject_columnsにより注入)
    value: 検索する値
    **kwargs: inject_columns用の追加引数

Returns:
    List[int]: 最も近い値を持つ行のインデックス（1つ）"""
        ...
    

    def switch_by_step(
        self,
        v1: ndarray,
        v2: ndarray,
        threshold: Union[int, float],
        compare_mode: str = 'value',
        by_step_value: bool = True,
        result_column: Optional[str] = None,
        in_place: bool = False,
        tolerance: Optional[float] = None
    ) -> Any:
        """ステップ値を基準に2つのColumnを切り替える (ベクトル化済み)"""
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
        result_column: Optional[str] = None,
        in_place: bool = False,
        tolerance: Optional[float] = None
    ) -> Any:
        """ステップ値の範囲内で2つのColumnをブレンドする (ベクトル化済み)"""
        ...
    

    def sum_columns(
        self,
        columns: Optional[list[str]] = None
    ) -> Any:
        """複数の列を合計します。

指定した複数の列の値を要素ごとに合計し、結果の配列を返します。

Args:
    data: 列データの辞書 (inject_columnsにより注入)
    columns: 合計対象の列名リスト"""
        ...
    

    def average_columns(
        self,
        columns: Optional[list[str]] = None
    ) -> Any:
        """複数の列の平均値を計算します。

指定した複数の列の値を要素ごとに平均し、結果の配列を返します。

Args:
    data: 列データの辞書 (inject_columnsにより注入)
    columns: 平均対象の列名リスト"""
        ...
    

    def conditional_select(
        self,
        v2: ndarray,
        cond_values: ndarray,
        threshold: Union[int, float] = 0,
        compare: str = '>'
    ) -> Any:
        """条件に基づいて2つの値を選択的に取得します

Args:
    v1: 条件を満たす場合に使用する値
    v2: 条件を満たさない場合に使用する値
    cond_values: 条件判定に使用する値
    threshold: 条件判定の閾値
    compare: 比較演算子"""
        ...
    

    def custom_combine(
        self,
        v2: Any,
        combine_func: Callable[[Any, Any], Any],
        func_name: Optional[str] = None
    ) -> "CollectionListOperations[StrainCollectionOperations]":
        """カスタム関数を使用して2つの値を合成します"""
        ...
    

    def add(
        self,
        v2: Union[ndarray, float],
        **kwargs
    ) -> ndarray:
        """列または定数を加算します"""
        ...
    

    def subtract(
        self,
        v2: Union[ndarray, float],
        **kwargs
    ) -> ndarray:
        """列または定数を減算します"""
        ...
    

    def multiply(
        self,
        v2: Union[ndarray, float],
        **kwargs
    ) -> ndarray:
        """列または定数を乗算します"""
        ...
    

    def divide(
        self,
        v2: Union[ndarray, float],
        **kwargs
    ) -> ndarray:
        """列または定数で除算します"""
        ...
    

    def diff(
        self,
        x_values: ndarray,
        method: str = 'central',
        **kwargs
    ) -> ndarray:
        """指定された 2 つの列間の微分を計算します（dy/dx）"""
        ...
    

    def integrate(
        self,
        x_values: ndarray,
        method: str = 'trapezoid',
        initial_value: float = 0.0,
        **kwargs
    ) -> ndarray:
        """指定された 2 つの列間の積分を計算します（∫y dx）"""
        ...
    

    def evaluate(
        self,
        expression: str,
        result_column: Optional[str] = None,
        in_place: bool = False,
        unit: Optional[str] = None,
        ch: Optional[str] = None
    ) -> Union[list[Optional[float]], ndarray]:
        """数式文字列を評価し、結果を返します

指定された数式を評価し、その結果の値を返します。
数式内では各列の値を変数として参照でき、基本的な数学関数も使用できます。

Args:
    collection: ColumnCollection オブジェクト
    expression: 評価する数式文字列（例: "price * quantity * (1 - discount)"）
    result_column: 結果を格納する列名（この引数はデコレータで使用されます）
    in_place: (デコレータで使用)
    unit: (デコレータで使用)
    ch: (デコレータで使用)

Returns:
     Union[List[Optional[float]], np.ndarray]: 計算結果の値リストまたは配列

Raises:
    KeyError: 指定された列名が存在しない場合
    ValueError: 式の評価中にエラーが発生した場合
    SyntaxError: 式の構文に問題がある場合"""
        ...
    

    def moving_average(
        self,
        window_size: int = 3,
        edge_handling: str = 'asymmetric'
    ) -> Any:
        """指定した列に対して移動平均を計算します

指定された列の各値に対して、周辺値を使用した平均値を算出します。
エッジ処理方法を選択することで、端部の計算方法を調整できます。

Args:
    collection: 処理対象の ColumnCollection
    column: 処理対象の列名
    window_size: 移動平均のウィンドウサイズ（奇数推奨）
    result_column: 結果を格納する列名（None の場合は自動生成）
    edge_handling: エッジ処理方法（"symmetric", "asymmetric"）
    in_place: True の場合、結果を元の列に上書き

Returns:
    ColumnCollection: 移動平均が計算された列を含むコレクション

Raises:
    KeyError: 指定された列が存在しない場合
    ValueError: 無効なエッジ処理方法やウィンドウサイズが指定された場合"""
        ...
    

    def detect_outliers(
        self,
        window_size: int = 3,
        threshold: float = 0.5,
        edge_handling: str = 'asymmetric',
        min_abs_value: float = 1e-10,
        scale_factor: float = 1.0
    ) -> list[int]:
        """移動平均との差分比率を用いた異常値検出を行います

データ値と移動平均の差分比率が閾値を超える場合に、その値を異常値として検出します。
検出結果は新しい列に 0（正常）または 1（異常）のフラグとして格納されます。

Args:
    collection: 処理対象の ColumnCollection
    column: 処理対象の列名
    window_size: 移動平均のウィンドウサイズ（奇数推奨）
    threshold: 異常値とみなす移動平均との差分比率の閾値
    edge_handling: エッジ処理方法（"symmetric", "asymmetric"）
    min_abs_value: 比率計算時の最小絶対値
    scale_factor: スケール調整係数
    result_column: 結果を格納する列名（None の場合は自動生成）

Returns:
    ColumnCollection: 異常値フラグ列を含むコレクション（1=異常値、0=正常値）

Raises:
    KeyError: 指定された列が存在しない場合
    ValueError: 無効なエッジ処理方法やウィンドウサイズが指定された場合、または有効なデータがない場合"""
        ...
    

    def gaussian_filter(
        self,
        sigma: float = 1.0,
        window_size: Optional[int] = None
    ) -> Any:
        """指定した列に対してガウシアンフィルタを適用します

ガウス分布の重みを用いた畳み込み演算により、データを平滑化します。
ノイズ除去特性が優れており、急激な変化を滑らかにします。

Args:
    collection: 処理対象の ColumnCollection
    column: 処理対象の列名
    sigma: ガウス分布の標準偏差（平滑化の強さ）
    window_size: カーネルサイズ（デフォルトは 6*sigma + 1 の奇数）
    result_column: 結果を格納する列名（None の場合は自動生成）
    in_place: True の場合、結果を元の列に上書き

Returns:
    ColumnCollection: 平滑化された列を含むコレクション"""
        ...
    

    def max(
        self,
        
    ) -> float:
        """列の最大値を取得します"""
        ...
    

    def min(
        self,
        
    ) -> float:
        """列の最小値を取得します"""
        ...
    

    def mean(
        self,
        
    ) -> float:
        """列の平均値を取得します"""
        ...
    

    def std(
        self,
        
    ) -> float:
        """列の標準偏差を取得します"""
        ...
    

    def sum(
        self,
        
    ) -> float:
        """列の合計値を取得します"""
        ...
    

    def sin(
        self,
        degrees: bool = False,
        **kwargs
    ) -> ndarray:
        """指定した列の各値に sin 関数を適用します"""
        ...
    

    def cos(
        self,
        degrees: bool = False,
        **kwargs
    ) -> ndarray:
        """指定した列の各値に cos 関数を適用します"""
        ...
    

    def tan(
        self,
        degrees: bool = False,
        **kwargs
    ) -> ndarray:
        """指定した列の各値に tan 関数を適用します"""
        ...
    

    def exp(
        self,
        **kwargs
    ) -> ndarray:
        """指定した列の各値に指数関数(e^x)を適用します"""
        ...
    

    def log(
        self,
        base: float = 2.718281828459045,
        **kwargs
    ) -> ndarray:
        """指定した列の各値に対数関数を適用します"""
        ...
    

    def sqrt(
        self,
        **kwargs
    ) -> ndarray:
        """指定した列の各値の平方根を計算します"""
        ...
    

    def pow(
        self,
        exponent: float,
        **kwargs
    ) -> ndarray:
        """指定した列の各値を指定した指数でべき乗します"""
        ...
    

    def abs_values(
        self,
        **kwargs
    ) -> ndarray:
        """指定した列の各値の絶対値を計算します"""
        ...
    

    def round_values(
        self,
        decimals: int = 0,
        **kwargs
    ) -> ndarray:
        """指定した列の各値を指定した小数点以下の桁数に丸めます"""
        ...
    

    def normalize(
        self,
        method: str = 'minmax',
        **kwargs
    ) -> ndarray:
        """指定した列の値を正規化します"""
        ...
    

    def interpolate(
        self,
        base_column_name: str = 'step',
        x_values: Optional[list[float]] = None,
        point_count: Optional[int] = None,
        method: str = 'linear',
        columns: Optional[list[str]] = None
    ) -> "StrainCollectionOperations":
        """指定した列の値に基づいてデータを内挿します"""
        ...
    

    def split_by_integers(
        self,
        markers: list[int]
    ) -> "CollectionListOperations[StrainCollectionOperations]":
        """整数リストの値でデータを分割します

Args:
    length: データの長さ (Decoratorにより自動注入)
    markers: 各データ値がどのグループに属するかを示す整数リスト（データと同じ長さ）
    
Returns:
    List[ColumnCollection]: 分割後の ColumnCollection オブジェクトのリスト。"""
        ...
    

    def split_at_indices(
        self,
        indices: Union[int, list[int]]
    ) -> "CollectionListOperations[StrainCollectionOperations]":
        """指定されたインデックスでコレクションを分割します

Args:
    length: データの長さ (Decoratorにより自動注入)
    indices: 分割するインデックス（intまたはList[int]）
    
Returns:
    List[ColumnCollection]: 分割後の ColumnCollection オブジェクトのリスト"""
        ...
    

    def test_filter(
        self,
        column_name,
        value
    ) -> Any:
        """テスト用フィルタリング操作"""
        ...
    

    def add_derived_column(
        self,
        formula,
        output_column
    ) -> Any:
        """数式に基づいて派生列を追加"""
        ...
    

    @overload
    def as_domain(self, domain: Literal['core'], **kwargs: Any) -> CoreCollectionOperations:
        ...

    @overload
    def as_domain(self, domain: Literal['load_displacement'], **kwargs: Any) -> LoadDisplacementCollectionOperations:
        ...

    @overload
    def as_domain(self, domain: Literal['coordinate'], **kwargs: Any) -> CoordinateCollectionOperations:
        ...

    def as_domain(self, domain: str, **kwargs: Any) -> Union[CoreCollectionOperations, Any]:
        """現在のコレクションを指定されたドメインに変換
        
        Args:
            domain: 変換先のドメイン名
            **kwargs: 変換に渡す追加の引数
        
        Returns:
            適切なドメイン特化型のCollectionOperationsオブジェクト
        """
        ...
