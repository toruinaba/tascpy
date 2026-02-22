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
        values: column = <class 'str'>,
        value: Any,
        tolerance: Optional[float] = None,
        column: column = <class 'str'>,
        value: Any,
        tolerance: Optional[float] = None
    ) -> ndarray:
        """値がターゲット値と等しいかどうかを判定します。

浮動小数点数の比較には許容誤差 (tolerance) を指定できます。

Args:
    values (Union[np.ndarray, list]): 判定対象の値の配列。
    value (Any): 比較するターゲット値。
    tolerance (float, optional): 許容誤差。指定された場合、`value - tolerance <= x <= value + tolerance` の範囲内であれば等しいとみなされます。

Returns:
    np.ndarray: 条件を満たす要素がTrueとなるブール値配列。"""
        ...
    

    def filter_out_none(
        self,
        data: columns = typing.Optional[typing.List[str]],
        mode: str = 'any',
        column: columns = typing.Optional[typing.List[str]],
        mode: str = 'any'
    ) -> list[bool]:
        """有効な行（欠損値を含まない行）を判定するマスクを返します。

Args:
    data (Dict[str, Union[np.ndarray, list]]): カラム名をキーとするデータ辞書。
    mode (str, optional): 欠損値の扱い。
        'any': 少なくとも1つのカラムが欠損している行を除外（すべて有効な場合に保持）。
        'all': すべてのカラムが欠損している行を除外（少なくとも1つ有効なら保持）。デフォルトは "any"。

Returns:
    List[bool]: 有効な行に対応するブール値リスト。

Raises:
    ValueError: モードが 'any' または 'all' 以外の場合。"""
        ...
    

    def remove_consecutive_duplicates_across(
        self,
        data: columns = typing.Optional[typing.List[str]],
        mode: str = 'consecutive',
        dup_type: str = 'all',
        column: columns = typing.Optional[typing.List[str]],
        mode: str = 'consecutive',
        dup_type: str = 'all'
    ) -> list[int]:
        """重複を除去した後の保持すべきインデックスを返します。

Args:
    data (Dict[str, Union[np.ndarray, list]]): カラム名をキーとするデータ辞書。
    mode (str, optional): 重複判定モード。'consecutive'（連続する重複のみ）または 'all'（全行での重複、未実装）。デフォルトは "consecutive"。
    dup_type (str, optional): 重複判定の厳密さ。
        'all': すべてのカラムが一致する場合に重複とみなす（標準）。
        'any': いずれかのカラムが一致する場合に重複とみなす（厳密、またはテスト用）。デフォルトは "all"。

Returns:
    List[int]: 保持すべき行のインデックスリスト。

Raises:
    ValueError: dup_type が 'all' または 'any' 以外の場合。
    NotImplementedError: mode が 'consecutive' 以外の場合。"""
        ...
    

    def remove_outliers(
        self,
        column: str,
        *args,
        **kwargs
    ) -> Any:
        """"""
        ...
    

    def filter_by_condition(
        self,
        vals: column = <class 'str'>,
        column: column = <class 'str'>,
        condition: <built-in function callable>
    ) -> "CollectionListOperations[StrainCollectionOperations]":
        """条件に基づいて値をフィルタリングするためのマスクを生成します。

Args:
    vals (Any): 入力値（リストまたは配列）。
    condition (callable): 値を引数に取り、保持すべき場合に True を返す関数。

Returns:
    List[bool]: 保持すべき値のブール値リスト。"""
        ...
    

    def remove_steps(
        self,
        steps: list[Any],
        tolerance: Optional[float] = None
    ) -> list[bool]:
        """特定のステップを除去するためのマスクを生成します。

指定されたステップに含まれない値に対して True を返します。

Args:
    step_values (Union[List[Any], np.ndarray]): 入力のステップ値リスト。
    steps (List[Any]): 除去するステップのリスト。
    tolerance (float, optional): ステップ一致判定の許容誤差。デフォルトは None（完全一致）。

Returns:
    List[bool]: 保持すべきステップ（除去対象でない）のブール値リスト。"""
        ...
    

    def search_by_value(
        self,
        values: values = typing.Any,
        column: values = typing.Any,
        op_str: str,
        value: Any
    ) -> list[int]:
        """演算子条件を満たす値のインデックスを返します。

Args:
    values (Union[np.ndarray, list]): 判定対象の値の配列。
    op_str (str): 比較演算子 ('>', '<', '>=', '<=', '==', '!=')。
    value (Any): 比較するターゲット値。

Returns:
    List[int]: 条件を満たす要素のインデックスリスト。"""
        ...
    

    def search_by_range(
        self,
        values: vals = typing.Any,
        column: vals = typing.Any,
        min_value: Any,
        max_value: Any,
        inclusive: bool = True
    ) -> list[int]:
        """指定された範囲内の値のインデックスを返します。

Args:
    values (Union[np.ndarray, list]): 判定対象の値の配列。
    min_value (Any): 範囲の下限。
    max_value (Any): 範囲の上限。
    inclusive (bool, optional): 端点を含めるかどうか。Trueの場合は [min, max]、Falseの場合は (min, max)。デフォルトは True。

Returns:
    List[int]: 範囲内の要素のインデックスリスト。"""
        ...
    

    def search_by_step_range(
        self,
        min: float,
        max: float,
        inclusive: bool = True,
        tolerance: Optional[float] = None,
        by_step_value: bool = True
    ) -> list[int]:
        """ステップ値が指定された範囲内にあるインデックスを返します。

Args:
    steps (Union[np.ndarray, list]): ステップ値の配列。
    min (float): 範囲の下限。
    max (float): 範囲の上限。
    inclusive (bool, optional): 端点を含めるかどうか。デフォルトは True。
    tolerance (float, optional): 許容誤差。デフォルトは None。
    by_step_value (bool, optional): ステップ値に基づいて検索するかどうか。Falseの場合はインデックス自体を対象とします。デフォルトは True。

Returns:
    List[int]: 条件を満たすステップのインデックスリスト。"""
        ...
    

    def search_by_condition(
        self,
        data: columns = typing.Optional[typing.List[str]],
        column: columns = typing.Optional[typing.List[str]],
        condition_func: Callable[[Dict[str, Any]], bool]
    ) -> list[int]:
        """条件関数を満たす行のインデックスを検索します。

Args:
    data (Dict[str, Any]): カラム名をキーとするデータ辞書。
    condition_func (Callable[[Dict[str, Any]], bool]): 行データ（辞書）を受け取り、boolを返す関数。

Returns:
    List[int]: 条件を満たす行のインデックスリスト。"""
        ...
    

    def search_missing_values(
        self,
        data: columns = typing.Optional[typing.List[str]],
        column: columns = typing.Optional[typing.List[str]]
    ) -> list[int]:
        """欠損値を含む行のインデックスを検索します。

Args:
    data (Dict[str, Any]): カラム名をキーとするデータ辞書。

Returns:
    List[int]: いずれかのカラムに欠損値を含む行のインデックスリスト。"""
        ...
    

    def search_top_n(
        self,
        values: vals = typing.Any,
        column: vals = typing.Any,
        n: int,
        descending: bool = True
    ) -> list[int]:
        """上位N個の値のインデックスを返します。

NaNは除外されます。結果のインデックスは昇順にソートされて返されます。

Args:
    values (Union[np.ndarray, list]): 値の配列。
    n (int): 取得する要素数。
    descending (bool, optional): 降順（大きい順）に選択するかどうか。Falseの場合は昇順（小さい順）。デフォルトは True。

Returns:
    List[int]: 選択された要素のインデックスリスト（昇順ソート済み）。"""
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
        """基本プロットを行います (Functional wrapper)。

Args:
    x_values (np.ndarray): x軸のデータ配列。
    y_values (np.ndarray): y軸のデータ配列。
    x_label (str): x軸のラベル。
    y_label (str): y軸のラベル。
    title (str): グラフのタイトル。
    ax (Optional[plt.Axes], optional): 描画先のMatplotlib Axesオブジェクト。Noneの場合は新規作成されます。デフォルトは None。
    **kwargs: その他のプロットオプション（color, marker, linestyleなど）。

Returns:
    plt.Axes: 描画に使用されたAxesオブジェクト。"""
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
    ) -> Axes:
        """異常値を検出し可視化します (Functional implementation)。

Args:
    x_values (Any): x軸のデータ配列。
    y_values (Any): y軸のデータ配列。
    x_label (str): x軸のラベル。
    y_label (str): y軸のラベル。
    title (str): グラフのタイトル。
    window_size (int, optional): 外れ値検出のウィンドウサイズ。デフォルトは 3。
    threshold (float, optional): 外れ値検出の閾値。デフォルトは 0.5。
    highlight_color (str, optional): 異常値のハイライト色。デフォルトは "red"。
    plot_type (str, optional): プロットタイプ ('scatter', 'line' など)。デフォルトは "scatter"。
    show_normal (bool, optional): 正常値を描画するかどうか。デフォルトは True。
    normal_color (str, optional): 正常値の色。デフォルトは "blue"。
    normal_alpha (float, optional): 正常値の透明度。デフォルトは 0.5。
    outlier_marker (str, optional): 異常値のマーカー形状。デフォルトは "o"。
    outlier_size (int, optional): 異常値のマーカーサイズ。デフォルトは 50。
    ax (Optional[plt.Axes], optional): 描画先のAxesオブジェクト。デフォルトは None。
    edge_handling (str, optional): 境界処理の方法。デフォルトは "asymmetric"。
    min_abs_value (float, optional): 最小絶対値（ゼロ除算防止）。デフォルトは 1e-10。
    scale_factor (float, optional): 閾値のスケーリング係数。デフォルトは 1.0。
    **kwargs: その他のプロットオプション。

Returns:
    plt.Axes: 描画に使用されたAxesオブジェクト。"""
        ...
    

    def plot_const_x(
        self,
        y_data: y_columns = typing.List[str],
        x_values: list[float] = None,
        column: y_columns = typing.List[str],
        x_values: list[float],
        show_legend: bool = True,
        ax: Optional[Axes] = None,
        **kwargs
    ) -> Axes:
        """特定のx値に対して複数のy列の値をプロットします。

Args:
    y_data (Dict[str, Any]): プロットするyデータの辞書（キー: 名前, 値: データ列またはスカラー）。
    x_values (List[float]): x軸の値のリスト（y_dataと同じ長さが必要）。
    show_legend (bool, optional): 凡例を表示するかどうか。デフォルトは True。
    ax (Optional[plt.Axes], optional): 描画先のAxesオブジェクト。デフォルトは None。
    **kwargs: その他のプロットオプション (x_label, y_label, titleなど)。

Returns:
    plt.Axes: 描画に使用されたAxesオブジェクト。"""
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
        """インタラクティブなグラフを描画します (Functional wrapper)。

Plotlyを使用してインタラクティブなプロットを作成します。

Args:
    x_values (np.ndarray): x軸のデータ配列。
    y_values (np.ndarray): y軸のデータ配列。
    x_label (str): x軸のラベル。
    y_label (str): y軸のラベル。
    title (str): グラフのタイトル。
    fig (Optional[Any], optional): 既存のPlotly Figureオブジェクト。Noneの場合は新規作成されます。デフォルトは None。
    **kwargs: その他のプロットオプション (name, color, symbol, sizeなど)。

Returns:
    Any: PlotlyのFigureオブジェクト。"""
        ...
    

    def select(
        self,
        columns: Optional[list[str]] = None,
        indices: Optional[list[int]] = None,
        steps: Optional[list[Union[int, float]]] = None,
        by_step_value: bool = True,
        tolerance: Optional[float] = None
    ) -> tuple[list[int], dict[str, Any]]:
        """指定されたステップまたはインデックスに基づいてデータを選択するためのインデックスを計算します。

Args:
    step_values (Union[List[Union[int, float]], np.ndarray]): ステップ値のリストまたは配列。
    columns (Optional[List[str]], optional): 選択するカラム名のリスト（未使用、互換性のため維持）。デフォルトは None。
    indices (Optional[List[int]], optional): 直接指定するインデックスのリスト。デフォルトは None。
    steps (Optional[List[Union[int, float]]], optional): 選択するステップ値またはインデックスのリスト。デフォルトは None。
    by_step_value (bool, optional): `steps` をステップ値として扱うかどうか。Falseの場合はインデックスとして扱います。デフォルトは True。
    tolerance (float, optional): ステップ値一致判定の許容誤差。指定された場合、許容誤差内の最も近い値を選択します。デフォルトは None。

Returns:
    Tuple[List[int], Dict[str, Any]]: 
        (選択されたインデックスのリスト, 実行結果のメタデータ辞書) のタプル。

Raises:
    ValueError: indices と steps の両方が指定された場合。"""
        ...
    

    def fetch_near_step(
        self,
        column: str,
        value: float,
        **kwargs
    ) -> "CollectionListOperations[StrainCollectionOperations]":
        """指定された値に最も近い要素のインデックスを検索します。

Args:
    values (np.ndarray): 検索対象の数値配列。
    value (float): ターゲット値。
    **kwargs: その他のオプション（未使用）。

Returns:
    List[int]: 最も近い値のインデックスを含むリスト（要素数1）。

Raises:
    TypeError: values が数値型でない場合。
    ValueError: 有効なデータが見つからない場合（全てNaNなど）。"""
        ...
    

    def switch_by_step(
        self,
        steps: step_values = <class 'numpy.ndarray'>,
        v1: v1 = typing.Union[str, numpy.ndarray],
        v2: v2 = typing.Union[str, numpy.ndarray],
        threshold: Union[int, float],
        compare_mode: str = 'value',
        by_step_value: bool = True,
        tolerance: Optional[float] = None,
        column: step_values = <class 'numpy.ndarray'>,
        v1: ndarray,
        v2: ndarray,
        threshold: Union[int, float],
        compare_mode: str = 'value',
        by_step_value: bool = True,
        tolerance: Optional[float] = None
    ) -> ndarray:
        """ステップ値またはインデックスに基づいて2つの配列を切り替えます。

Args:
    steps (np.ndarray): ステップ値の配列。
    v1 (np.ndarray): 閾値未満の場合の値の配列。
    v2 (np.ndarray): 閾値以上の場合の値の配列。
    threshold (Union[int, float]): 切り替えの閾値。
    compare_mode (str, optional): 比較モード ('value' または 'index')。デフォルトは "value"。
    by_step_value (bool, optional): ステップ値で比較するかどうか。Falseの場合はインデックスを使用。デフォルトは True。
    tolerance (float, optional): 閾値特定時の許容誤差（compare_mode='index' かつ by_step_value=True の場合に使用）。

Returns:
    np.ndarray: 切り替え後の配列。

Raises:
    ValueError: v1とv2の長さが異なる場合。"""
        ...
    

    def blend_by_step(
        self,
        steps: step_values = <class 'numpy.ndarray'>,
        v1: v1 = <class 'numpy.ndarray'>,
        v2: v2 = <class 'numpy.ndarray'>,
        start: Union[int, float],
        end: Union[int, float],
        compare_mode: str = 'value',
        by_step_value: bool = True,
        blend_method: str = 'linear',
        tolerance: Optional[float] = None,
        column: step_values = <class 'numpy.ndarray'>,
        v1: ndarray,
        v2: ndarray,
        start: Union[int, float],
        end: Union[int, float],
        compare_mode: str = 'value',
        by_step_value: bool = True,
        blend_method: str = 'linear',
        tolerance: Optional[float] = None
    ) -> ndarray:
        """ステップ値またはインデックスに基づいて2つの配列を指定区間でブレンドします。

Args:
    steps (np.ndarray): ステップ値の配列。
    v1 (np.ndarray): ブレンド開始前の値の配列。
    v2 (np.ndarray): ブレンド終了後の値の配列。
    start (Union[int, float]): ブレンド開始値。
    end (Union[int, float]): ブレンド終了値。
    compare_mode (str, optional): 比較モード ('value' または 'index')。デフォルトは "value"。
    by_step_value (bool, optional): ステップ値で比較するかどうか。Falseの場合はインデックスを使用。デフォルトは True。
    blend_method (str, optional): ブレンド方法 ('linear', 'smooth', 'log', 'exp')。デフォルトは "linear"。
    tolerance (float, optional): 開始・終了値特定時の許容誤差（compare_mode='index' かつ by_step_value=True の場合に使用）。

Returns:
    np.ndarray: ブレンド後の配列。

Raises:
    ValueError: v1とv2の長さが異なる場合、終了値が開始値以下の場合、または無効なブレンドメソッドが指定された場合。"""
        ...
    

    def sum_columns(
        self,
        data: columns = typing.Optional[typing.List[str]],
        column: columns = typing.Optional[typing.List[str]],
        columns = None
    ) -> Any:
        """"""
        ...
    

    def average_columns(
        self,
        data: columns = typing.Optional[typing.List[str]],
        column: columns = typing.Optional[typing.List[str]],
        columns = None
    ) -> Any:
        """"""
        ...
    

    def conditional_select(
        self,
        v1: v1 = <class 'numpy.ndarray'>,
        v2: v2 = <class 'numpy.ndarray'>,
        cond_values: cond_values = <class 'numpy.ndarray'>,
        threshold: Union[int, float] = 0,
        compare: str = '>',
        column: v1 = <class 'numpy.ndarray'>,
        v2: ndarray,
        cond_values: ndarray,
        threshold: Union[int, float] = 0,
        compare: str = '>'
    ) -> ndarray:
        """条件に基づいて2つの配列から値を選択します。

cond_values が条件を満たす位置では v1 の値を、そうでない場合は v2 の値を選択します。

Args:
    v1 (np.ndarray): 条件真の場合の値の配列。
    v2 (np.ndarray): 条件偽の場合の値の配列。
    cond_values (np.ndarray): 条件判定に使用する値の配列。
    threshold (Union[int, float], optional): 比較の閾値。デフォルトは 0。
    compare (str, optional): 比較演算子 ('>', '>=', '<', '<=', '==', '!=')。デフォルトは ">"。

Returns:
    np.ndarray: 選択された値の配列。

Raises:
    ValueError: 無効な比較演算子が指定された場合。"""
        ...
    

    def custom_combine(
        self,
        v1: v1 = typing.Any,
        v2: v2 = typing.Any,
        combine_func: combine_func = typing.Callable[[typing.Any, typing.Any], typing.Any],
        column: v1 = typing.Any,
        v2: Any,
        combine_func: Callable[[Any, Any], Any],
        **kwargs
    ) -> "CollectionListOperations[StrainCollectionOperations]":
        """カスタム関数を使用して2つの値または配列を結合します。

Args:
    v1 (Any): 最初の値または配列。
    v2 (Any): 2番目の値または配列。
    combine_func (Callable[[Any, Any], Any]): 2つの引数を取る結合関数。
    **kwargs: 任意の追加引数（ここでは使用されません）。

Returns:
    Any: 結合結果（配列またはリスト）。"""
        ...
    

    def add(
        self,
        column: str,
        v2: Union[ndarray, float]
    ) -> ndarray:
        """2つの値または配列を加算します。

Args:
    v1 (Union[np.ndarray, float]): 最初の値または配列。
    v2 (Union[np.ndarray, float]): 2番目の値または配列。

Returns:
    np.ndarray: 加算結果。"""
        ...
    

    def subtract(
        self,
        column: str,
        v2: Union[ndarray, float]
    ) -> ndarray:
        """v1 から v2 を減算します。

Args:
    v1 (Union[np.ndarray, float]): 最初の値または配列。
    v2 (Union[np.ndarray, float]): 引く値または配列。

Returns:
    np.ndarray: 減算結果。"""
        ...
    

    def multiply(
        self,
        column: str,
        v2: Union[ndarray, float]
    ) -> ndarray:
        """2つの値または配列を乗算します。

Args:
    v1 (Union[np.ndarray, float]): 最初の値または配列。
    v2 (Union[np.ndarray, float]): 2番目の値または配列。

Returns:
    np.ndarray: 乗算結果。"""
        ...
    

    def divide(
        self,
        column: str,
        v2: Union[ndarray, float],
        **kwargs
    ) -> ndarray:
        """v1 を v2 で除算します。

Args:
    v1 (Union[np.ndarray, float]): 分子となる値または配列。
    v2 (Union[np.ndarray, float]): 分母となる値または配列。
    **kwargs: 任意の追加引数。

Returns:
    np.ndarray: 除算結果。"""
        ...
    

    def diff(
        self,
        y: y_values = <class 'numpy.ndarray'>,
        x: x_values = <class 'numpy.ndarray'>,
        method: str = 'central',
        column: y_values = <class 'numpy.ndarray'>,
        x: Union[ndarray, list[float]],
        method: str = 'central'
    ) -> ndarray:
        """x, y座標から微分係数を計算します。

Args:
    y (Union[np.ndarray, List[float]]): y座標の配列。
    x (Union[np.ndarray, List[float]]): x座標の配列。
    method (str, optional): 微分方法 ('central', 'forward', 'backward')。デフォルトは "central"。

Returns:
    np.ndarray: 計算された微分係数の配列。

Raises:
    ValueError: xとyの長さが異なる場合、またはデータ点が2点未満の場合、または無効なメソッドが指定された場合。"""
        ...
    

    def integrate(
        self,
        y: y_values = <class 'numpy.ndarray'>,
        x: x_values = <class 'numpy.ndarray'>,
        method: str = 'trapezoid',
        initial_value: float = 0.0,
        column: y_values = <class 'numpy.ndarray'>,
        x: Union[ndarray, list[float]],
        method: str = 'trapezoid',
        initial_value: float = 0.0
    ) -> ndarray:
        """xに対するyの積分を計算します。

Args:
    y (Union[np.ndarray, List[float]]): y座標の配列。
    x (Union[np.ndarray, List[float]]): x座標の配列。
    method (str, optional): 積分方法。現在は "trapezoid" (台形則) のみサポート。デフォルトは "trapezoid"。
    initial_value (float, optional): 積分初期値。デフォルトは 0.0。

Returns:
    np.ndarray: 計算された積分の配列（累積和）。

Raises:
    ValueError: サポートされていないメソッドが指定された場合、またはxとyの長さが異なる場合。"""
        ...
    

    def evaluate(
        self,
        collection: collection = <class 'tascpy.core.collection.ColumnCollection'>,
        column: collection = <class 'tascpy.core.collection.ColumnCollection'>,
        expression: str,
        **kwargs
    ) -> Union[list[Optional[float]], ndarray]:
        """"""
        ...
    

    def sin(
        self,
        values: values = <class 'numpy.ndarray'>,
        degrees: bool = False,
        column: values = <class 'numpy.ndarray'>,
        degrees: bool = False
    ) -> ndarray:
        """正弦(sin)を計算します。

Args:
    values (np.ndarray): 入力値の配列。
    degrees (bool, optional): 入力が度数法(degree)かどうか。Trueの場合はラジアンに変換してから計算します。デフォルトは False（ラジアン）。

Returns:
    np.ndarray: 計算結果の配列。"""
        ...
    

    def cos(
        self,
        values: values = <class 'numpy.ndarray'>,
        degrees: bool = False,
        column: values = <class 'numpy.ndarray'>,
        degrees: bool = False
    ) -> ndarray:
        """余弦(cos)を計算します。

Args:
    values (np.ndarray): 入力値の配列。
    degrees (bool, optional): 入力が度数法(degree)かどうか。Trueの場合はラジアンに変換してから計算します。デフォルトは False（ラジアン）。

Returns:
    np.ndarray: 計算結果の配列。"""
        ...
    

    def tan(
        self,
        values: values = <class 'numpy.ndarray'>,
        degrees: bool = False,
        column: values = <class 'numpy.ndarray'>,
        degrees: bool = False
    ) -> ndarray:
        """正接(tan)を計算します。

Args:
    values (np.ndarray): 入力値の配列。
    degrees (bool, optional): 入力が度数法(degree)かどうか。Trueの場合はラジアンに変換してから計算します。デフォルトは False（ラジアン）。

Returns:
    np.ndarray: 計算結果の配列。"""
        ...
    

    def exp(
        self,
        values: values = <class 'numpy.ndarray'>,
        column: values = <class 'numpy.ndarray'>
    ) -> ndarray:
        """指数関数(exp)を計算します。

Args:
    values (np.ndarray): 入力値の配列。

Returns:
    np.ndarray: 計算結果の配列。"""
        ...
    

    def log(
        self,
        values: values = <class 'numpy.ndarray'>,
        base: float = 2.718281828459045,
        column: values = <class 'numpy.ndarray'>,
        base: float = 2.718281828459045
    ) -> ndarray:
        """対数(log)を計算します。

0以下の値はNaNになります。

Args:
    values (np.ndarray): 入力値の配列。
    base (float, optional): 対数の底。デフォルトは e（自然対数）。

Returns:
    np.ndarray: 計算結果の配列。"""
        ...
    

    def sqrt(
        self,
        values: values = <class 'numpy.ndarray'>,
        column: values = <class 'numpy.ndarray'>
    ) -> ndarray:
        """平方根(sqrt)を計算します。

負の値はNaNになります。

Args:
    values (np.ndarray): 入力値の配列。

Returns:
    np.ndarray: 計算結果の配列。"""
        ...
    

    def pow(
        self,
        values: column = <class 'str'>,
        exponent: float = 1.0,
        column: column = <class 'str'>,
        exponent: float
    ) -> ndarray:
        """累乗(power)を計算します。

Args:
    values (np.ndarray): 基数の配列。
    exponent (float): 指数。

Returns:
    np.ndarray: 計算結果の配列。"""
        ...
    

    def abs_values(
        self,
        values: column = <class 'str'>,
        column: column = <class 'str'>
    ) -> ndarray:
        """絶対値(absolute value)を計算します。

Args:
    values (np.ndarray): 入力値の配列。

Returns:
    np.ndarray: 計算結果の配列。"""
        ...
    

    def round_values(
        self,
        values: column = <class 'str'>,
        decimals: int = 0,
        column: column = <class 'str'>,
        decimals: int = 0
    ) -> ndarray:
        """値を指定された桁数で丸めます。

Args:
    values (np.ndarray): 入力値の配列。
    decimals (int, optional): 丸める小数点以下の桁数。デフォルトは 0。

Returns:
    np.ndarray: 計算結果の配列。"""
        ...
    

    def normalize(
        self,
        values: column = <class 'str'>,
        method: str = 'minmax',
        column: column = <class 'str'>,
        method: str = 'minmax'
    ) -> ndarray:
        """値を正規化します。

Args:
    values (np.ndarray): 入力値の配列。
    method (str, optional): 正規化方法。
        'minmax': 最小値を0、最大値を1にスケーリング。
        'zscore': 平均を0、標準偏差を1に標準化。デフォルトは "minmax"。

Returns:
    np.ndarray: 正規化された配列。

Raises:
    ValueError: 指定されたメソッドが無効な場合。"""
        ...
    

    def moving_average(
        self,
        vals: vals = typing.Any,
        window_size: int = 3,
        edge_handling: str = 'asymmetric',
        column: vals = typing.Any,
        window_size: int = 3,
        edge_handling: str = 'asymmetric'
    ) -> Any:
        """移動平均を計算します。

Args:
    vals (Union[np.ndarray, List[float]]): 入力値の配列またはリスト。
    window_size (int, optional): ウィンドウサイズ。デフォルトは 3。
    edge_handling (str, optional): 境界処理の方法 ('symmetric', 'asymmetric')。デフォルトは "asymmetric"。

Returns:
    Any: 移動平均処理後の配列（入力の型に依存）。

Raises:
    ValueError: 無効なエッジ処理方法、ウィンドウサイズが1未満、またはデータ長より大きい場合。"""
        ...
    

    def detect_outliers(
        self,
        vals: vals = typing.Any,
        window_size: int = 3,
        threshold: float = 0.5,
        edge_handling: str = 'asymmetric',
        min_abs_value: float = 1e-10,
        scale_factor: float = 1.0,
        column: vals = typing.Any,
        window_size: int = 3,
        threshold: float = 0.5,
        edge_handling: str = 'asymmetric',
        min_abs_value: float = 1e-10,
        scale_factor: float = 1.0
    ) -> list[int]:
        """移動平均を使用して外れ値を検出します。

移動平均からの偏差率が閾値を超える場合を外れ値とみなします。

Args:
    vals (Union[np.ndarray, List[float]]): 入力値の配列またはリスト。
    window_size (int, optional): 移動平均のウィンドウサイズ。デフォルトは 3。
    threshold (float, optional): 外れ値判定の閾値（偏差率）。デフォルトは 0.5。
    edge_handling (str, optional): 境界処理の方法。デフォルトは "asymmetric"。
    min_abs_value (float, optional): 最小絶対値（ゼロ除算防止）。デフォルトは 1e-10。
    scale_factor (float, optional): 基準値（標準偏差等）のスケーリング係数。デフォルトは 1.0。

Returns:
    List[int]: 外れ値フラグのリスト（0: 正常, 1: 外れ値）。

Raises:
    ValueError: 無効な引数、または有効なデータが存在しない場合。"""
        ...
    

    def gaussian_filter(
        self,
        vals: vals = typing.Any,
        sigma: float = 1.0,
        window_size: Optional[int] = None,
        column: vals = typing.Any,
        sigma: float = 1.0,
        window_size: Optional[int] = None
    ) -> Any:
        """ガウシアンフィルタを適用して平滑化を行います。

欠損値は無視して畳み込み計算を行います。

Args:
    vals (Union[np.ndarray, List[float]]): 入力値の配列またはリスト。
    sigma (float, optional): ガウス分布の標準偏差。デフォルトは 1.0。
    window_size (Optional[int], optional): フィルタのウィンドウサイズ。指定しない場合は sigma から自動計算されます。

Returns:
    Any: 平滑化後の配列（NumPy配列）。

Raises:
    ValueError: ウィンドウサイズが1未満の場合。"""
        ...
    

    def max(
        self,
        column: str
    ) -> float:
        """最大値を計算します（NaNは無視されます）。

Args:
    vals (Any): 入力値の配列またはリスト。

Returns:
    float: 最大値。"""
        ...
    

    def min(
        self,
        column: str
    ) -> float:
        """最小値を計算します（NaNは無視されます）。

Args:
    vals (Any): 入力値の配列またはリスト。

Returns:
    float: 最小値。"""
        ...
    

    def mean(
        self,
        column: str
    ) -> float:
        """平均値を計算します（NaNは無視されます）。

Args:
    vals (Any): 入力値の配列またはリスト。

Returns:
    float: 平均値。"""
        ...
    

    def std(
        self,
        column: str
    ) -> float:
        """標準偏差を計算します（NaNは無視されます）。

Args:
    vals (Any): 入力値の配列またはリスト。

Returns:
    float: 標準偏差。"""
        ...
    

    def sum(
        self,
        column: str
    ) -> float:
        """合計値を計算します（NaNは無視されます）。

Args:
    vals (Any): 入力値の配列またはリスト。

Returns:
    float: 合計値。"""
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
        length: length = <class 'int'>,
        markers: markers = typing.List[int],
        column: length = <class 'int'>,
        markers: Union[list[int], ndarray]
    ) -> list[ndarray]:
        """整数マーカーに基づいて分割インデックスを計算します。

ユニークなマーカー値ごとに、そのマーカーに対応するインデックスの配列をリストとして返します。

Args:
    length (int): データの長さ。
    markers (Union[List[int], np.ndarray]): 各要素に対応する整数マーカーのリストまたは配列。長さは `length` と一致する必要があります。

Returns:
    List[np.ndarray]: 各マーカーに対応するインデックス配列のリスト。

Raises:
    ValueError: データ長とマーカーリストの長さが一致しない場合。"""
        ...
    

    def split_at_indices(
        self,
        length: length = <class 'int'>,
        indices: indices = typing.Union[int, typing.List[int]],
        column: length = <class 'int'>,
        indices: Union[int, list[int]]
    ) -> list[slice]:
        """指定されたインデックスで分割するためのスライスを計算します。

Args:
    length (int): データの長さ。
    indices (Union[int, List[int]]): 分割点となるインデックス（またはそのリスト）。

Returns:
    List[slice]: 分割された各セグメントを表すスライスのリスト。

Raises:
    IndexError: インデックスが範囲外 (0-length) の場合。"""
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
