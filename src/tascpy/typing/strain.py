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
        column_name: str,
        value: Any,
        tolerance: Optional[float] = None
    ) -> "StrainCollectionOperations":
        """指定された列の値が指定された値と等しい行をフィルタリングします

指定された列の値が特定の値と一致する行だけを含む新しいコレクションを返します。
許容誤差（tolerance）を指定すると、その範囲内の値も含めることができます。

Args:
    collection: ColumnCollection オブジェクト
    column_name: フィルタリングする列の名前
    value: フィルタリングする値
    tolerance: 値の許容範囲（デフォルトは None）

Returns:
    ColumnCollection: フィルタリングされた ColumnCollection オブジェクト

Raises:
    KeyError: 指定された列名が存在しない場合
    TypeError: 指定された列が Column オブジェクトでない場合"""
        ...
    

    def filter_out_none(
        self,
        columns: Optional[list[str]] = None,
        mode: str = 'any'
    ) -> "StrainCollectionOperations":
        """None値およびNaN値を含む行をフィルタリングして除外します

指定された列にNone値またはNaN値を含む行を除外した新しいコレクションを返します。
モードによって、いずれかの列が欠損値の場合に除外するか、全ての列が欠損値の場合に除外するかを選択できます。

Args:
    collection: ColumnCollection オブジェクト
    columns: フィルタリングする対象の列名リスト（デフォルトは None、すべての列が対象）
    mode: フィルタリングモード 'any'（いずれかの列が欠損値の行を除外）または
          'all'（すべての列が欠損値の行を除外）

Returns:
    ColumnCollection: フィルタリングされた ColumnCollection オブジェクト

Raises:
    ValueError: 不正なモードが指定された場合
    KeyError: 指定された列名が存在しない場合"""
        ...
    

    def remove_consecutive_duplicates_across(
        self,
        columns: list[str],
        dup_type: str = 'all'
    ) -> "StrainCollectionOperations":
        """複数の列間で共通の連続重複データを削除した新しい ColumnCollection オブジェクトを返します

すべての指定された列で、連続するデータポイントが同じ値を持つ場合にのみ、
その重複を 1 つだけ残して削除します。重複判定のタイプによって動作が変わります。

Args:
    collection: 処理する ColumnCollection オブジェクト
    columns: 処理対象の列名リスト
    dup_type: 重複判定のタイプ
             'all': すべての列で値に変化がない場合に重複と判定
             'any': 一部の列だけでも値に変化がある場合は重複と判定しない

Returns:
    ColumnCollection: 連続する重複を削除したデータを持つ新しい ColumnCollection オブジェクト

Raises:
    ValueError: 不正な dup_type が指定された場合
    KeyError: 指定された列名が存在しない場合

Examples:
    >>> # collection["A"] = [1.0, 1.0, 2.0, 2.0, 3.0, 3.0]
    >>> # collection["B"] = [10.0, 20.0, 30.0, 30.0, 40.0, 50.0]
    >>> # collection["C"] = [5, 5, 2, 2, 8, 8]
    >>> result = remove_consecutive_duplicates_across(collection, ["A", "B", "C"])
    >>> # result["A"] = [1.0, 1.0, 2.0, 3.0, 3.0]
    >>> # result["B"] = [10.0, 20.0, 30.0, 40.0, 50.0]
    >>> # result["C"] = [5, 5, 2, 8, 8]"""
        ...
    

    def remove_outliers(
        self,
        column: str,
        window_size: int = 3,
        threshold: float = 0.5,
        edge_handling: str = 'asymmetric',
        min_abs_value: float = 1e-10,
        scale_factor: float = 1.0
    ) -> "StrainCollectionOperations":
        """異常値を検出して除去した新しいコレクションを返します

移動平均との差分比率を用いた異常値検出を行い、異常値とみなされた行を除外します。
異常値の検出には detect_outliers 関数を使用します。

Args:
    collection: 処理対象の ColumnCollection
    column: 異常値を検出する列の名前
    window_size: 移動平均のウィンドウサイズ（奇数推奨）
    threshold: 異常値とみなす移動平均との差分比率の閾値
    edge_handling: エッジ処理方法（"symmetric", "asymmetric"）
    min_abs_value: 比率計算時の最小絶対値
    scale_factor: スケール調整係数

Returns:
    ColumnCollection: 異常値を除去した新しい ColumnCollection オブジェクト

Raises:
    KeyError: 指定された列が存在しない場合
    ValueError: 無効なエッジ処理方法やウィンドウサイズが指定された場合、または有効なデータがない場合"""
        ...
    

    def filter_by_condition(
        self,
        column_name: str,
        condition: <built-in function callable>
    ) -> "StrainCollectionOperations":
        """指定された列の値が条件を満たす行をフィルタリングします

Args:
    collection: ColumnCollection オブジェクト
    column_name: 条件を適用する列の名前
    condition: 値を引数に取り、bool値を返す関数

Returns:
    ColumnCollection: 条件を満たす行のみを含む新しいコレクション"""
        ...
    

    def remove_steps(
        self,
        steps: list[Any],
        tolerance: Optional[float] = None
    ) -> "StrainCollectionOperations":
        """指定されたステップ値を持つ行を削除します

Args:
    collection: ColumnCollection オブジェクト
    steps: 削除するステップ値のリスト
    tolerance: ステップ値の比較における許容誤差

Returns:
    ColumnCollection: 指定ステップが削除された新しいコレクション"""
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
        column_name: str,
        op_str: str,
        value: Any
    ) -> "StrainCollectionOperations":
        """値による検索を行います

指定された列の値に対して比較演算子を適用し、条件に一致する行を抽出します。

Args:
    collection: 対象コレクション
    column_name: 列名
    op_str: 演算子文字列 (">", "<", ">=", "<=", "==", "!=")
    value: 比較する値

Returns:
    ColumnCollection: フィルタリングされたコレクション

Raises:
    ValueError: 無効な演算子が指定された場合
    KeyError: 指定された列が存在しない場合"""
        ...
    

    def search_by_range(
        self,
        column_name: str,
        min_value: Any,
        max_value: Any,
        inclusive: bool = True
    ) -> "StrainCollectionOperations":
        """範囲による検索を行います

指定された列の値が特定の範囲内にある行を抽出します。
境界値を含めるかどうかを選択できます。

Args:
    collection: 対象コレクション
    column_name: 列名
    min_value: 最小値
    max_value: 最大値
    inclusive: 境界値を含むかどうか（True の場合は境界値を含む）

Returns:
    ColumnCollection: フィルタリングされたコレクション

Raises:
    KeyError: 指定された列が存在しない場合"""
        ...
    

    def search_by_step_range(
        self,
        min: Union[int, float],
        max: Union[int, float],
        inclusive: bool = True,
        by_step_value: bool = True,
        tolerance: Optional[float] = None
    ) -> "StrainCollectionOperations":
        """ステップ範囲による検索を行います

指定されたステップ範囲またはインデックス範囲に該当する行を抽出します。
ステップ値での検索とインデックスでの検索を選択できます。

Args:
    collection: 対象コレクション
    min: 最小ステップ値（by_step_value=True の場合）または最小インデックス（by_step_value=False の場合）
    max: 最大ステップ値（by_step_value=True の場合）または最大インデックス（by_step_value=False の場合）
    inclusive: 境界値を含むかどうか（True の場合は境界値を含む）
    by_step_value: True の場合はステップ値として解釈、False の場合はインデックスとして解釈
    tolerance: ステップ値検索時の許容範囲（by_step_value=True の場合のみ有効）

Returns:
    ColumnCollection: フィルタリングされたコレクション"""
        ...
    

    def search_by_condition(
        self,
        condition_func: Callable[[Dict[str, Any]], bool]
    ) -> "StrainCollectionOperations":
        """条件関数による検索を行います

各行のデータを辞書形式で条件関数に渡し、結果が True となる行だけを抽出します。
任意の複雑な条件を柔軟に適用することができます。

Args:
    collection: 対象コレクション
    condition_func: 各行データを受け取り、真偽値を返す関数。引数は {列名: 値} の辞書形式

Returns:
    ColumnCollection: フィルタリングされたコレクション"""
        ...
    

    def search_missing_values(
        self,
        columns: Optional[list[str]] = None
    ) -> "StrainCollectionOperations":
        """欠損値がある行を検索します

指定された列に欠損値（None）を含む行だけを抽出します。
データのクリーニングや欠損値の分析に役立ちます。

Args:
    collection: 対象コレクション
    columns: 検査対象の列名リスト（None の場合は全列）

Returns:
    ColumnCollection: 欠損値を持つ行だけのコレクション

Raises:
    KeyError: 指定された列が存在しない場合"""
        ...
    

    def search_top_n(
        self,
        column_name: str,
        n: int,
        descending: bool = True
    ) -> "StrainCollectionOperations":
        """指定した列の上位 N 件を検索します

指定した列の値に基づいて、上位（または下位）N 件のデータを抽出します。
ソート順序を指定することで、最大値または最小値の上位を取得できます。

Args:
    collection: 対象コレクション
    column_name: 値の基準となる列名
    n: 抽出する件数
    descending: True の場合は降順ソート（大きい順）、False の場合は昇順ソート（小さい順）

Returns:
    ColumnCollection: フィルタリングされたコレクション

Raises:
    KeyError: 指定された列が存在しない場合"""
        ...
    

    def plot(
        self,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        plot_type: str = 'scatter',
        ax: Optional[Axes] = None,
        **kwargs
    ) -> Axes:
        """グラフを描画します

(backend_mpl.plot を使用)"""
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
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        plot_type: str = 'scatter',
        fig: Optional[Any] = None,
        **kwargs
    ) -> Any:
        """インタラクティブなグラフを描画します (Plotly使用)

Args:
    collection: 対象コレクション
    x_column: x軸の列名（None の場合は step を使用）
    y_column: y軸の列名（None の場合は step を使用）
    plot_type: プロットの種類（'scatter' または 'line'）
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
    ) -> "StrainCollectionOperations":
        """指定した列名、行インデックス、またはステップ値に基づいてデータを抽出します

複数の方法でデータ抽出を行うことができる汎用的な選択操作です。
列の選択、インデックスによる行の選択、ステップ値による行の選択を組み合わせて使用できます。

Args:
    collection: 元の ColumnCollection
    columns: 抽出する列名のリスト。None の場合は全列が対象
    indices: 抽出する行インデックスのリスト。None の場合は全行が対象
    steps: 抽出するステップのリスト。None の場合は全行が対象
        by_step_value=True の場合：ステップ値として解釈
        by_step_value=False の場合：インデックスとして解釈
    by_step_value: True の場合は steps をステップ値として解釈、False の場合はインデックスとして解釈
    tolerance: ステップ値検索時の許容範囲（by_step_value=True の場合のみ有効）

Returns:
    ColumnCollection: 選択されたデータを含む新しい ColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合
    IndexError: 明示的に指定された indices が範囲外の場合（steps の場合は無視される）
    ValueError: indices と steps の両方が指定された場合"""
        ...
    

    def select_step(
        self,
        steps: list[Union[int, float]],
        columns: Optional[list[str]] = None,
        by_step_value: bool = True,
        tolerance: Optional[float] = None
    ) -> "StrainCollectionOperations":
        """指定した列名とステップ番号に基づいてデータを抽出します

注: この関数は後方互換性のために残されています。
新しいコードでは select() 関数を使用することが推奨されます。

Args:
    collection: 元の ColumnCollection
    steps: 抽出するステップ番号のリスト（by_step_value=True の場合）または
           インデックスのリスト（by_step_value=False の場合）
    columns: 抽出する列名のリスト。None の場合は全列が対象
    by_step_value: True の場合はステップ値として解釈、False の場合はインデックスとして解釈
    tolerance: ステップ値検索時の許容範囲（by_step_value=True の場合のみ有効）

Returns:
    ColumnCollection: 選択されたデータを含む新しい ColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合"""
        ...
    

    def fetch_near_step(
        self,
        column_name: str,
        value: float
    ) -> "StrainCollectionOperations":
        """指定された値に最も近い行を取得します

Args:
    collection: ColumnCollection オブジェクト
    column_name: 値を検索する列名
    value: 検索する値

Returns:
    ColumnCollection: 最も近い値を持つ1行だけのコレクション"""
        ...
    

    def switch_by_step(
        self,
        column1: str,
        column2: str,
        threshold: Union[int, float],
        compare_mode: str = 'value',
        by_step_value: bool = True,
        result_column: Optional[str] = None,
        in_place: bool = False,
        tolerance: Optional[float] = None
    ) -> "StrainCollectionOperations":
        """ステップ値を基準に2つのColumnを切り替える

指定されたステップ値またはインデックスを境界として、それより前はcolumn1、
それ以降はcolumn2の値を使用した新しいColumnを生成します。

Args:
    collection: ColumnCollectionオブジェクト
    column1: 閾値より前（または以下）の値を取得する列名
    column2: 閾値より後（または以上）の値を取得する列名
    threshold: 切り替え基準となる値
        by_step_value=True かつ compare_mode="value" の場合：ステップ値
        by_step_value=True かつ compare_mode="index" の場合：ステップ値でインデックスを検索
        by_step_value=False の場合：インデックス値
    compare_mode: 比較モード ("value": ステップの値, "index": インデックス位置)
    by_step_value: Trueの場合はステップ値として解釈、Falseの場合はインデックスとして解釈
    result_column: 結果を格納する列名（デフォルトはNone、自動生成）
    in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成
    tolerance: ステップ値検索時の許容範囲（by_step_value=Trueの場合のみ有効）

Returns:
    ColumnCollection: 切り替え結果の列を含むColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合
    ValueError: 列の長さが一致しない場合、または無効な値が指定された場合"""
        ...
    

    def blend_by_step(
        self,
        column1: str,
        column2: str,
        start: Union[int, float],
        end: Union[int, float],
        compare_mode: str = 'value',
        by_step_value: bool = True,
        blend_method: str = 'linear',
        result_column: Optional[str] = None,
        in_place: bool = False,
        tolerance: Optional[float] = None
    ) -> "StrainCollectionOperations":
        """ステップ値の範囲内で2つのColumnをブレンドする

指定された開始点から終了点までの間で、column1からcolumn2へ徐々に
ブレンドした新しいColumnを生成します。開始点より前はcolumn1、終了点より後は
column2の値のみを使用します。

Args:
    collection: ColumnCollectionオブジェクト
    column1: ブレンド開始時（または範囲外の低い方）の値を取得する列名
    column2: ブレンド終了時（または範囲外の高い方）の値を取得する列名
    start: ブレンド開始点
        by_step_value=True かつ compare_mode="value" の場合：ステップ値
        by_step_value=True かつ compare_mode="index" の場合：ステップ値でインデックスを検索
        by_step_value=False の場合：インデックス値
    end: ブレンド終了点
        by_step_value=True かつ compare_mode="value" の場合：ステップ値
        by_step_value=True かつ compare_mode="index" の場合：ステップ値でインデックスを検索
        by_step_value=False の場合：インデックス値
    compare_mode: 比較モード ("value": ステップの値, "index": インデックス位置)
    by_step_value: Trueの場合はステップ値として解釈、Falseの場合はインデックスとして解釈
    blend_method: ブレンド方法 ("linear", "smooth", "log", "exp")
    result_column: 結果を格納する列名（デフォルトはNone、自動生成）
    in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成
    tolerance: ステップ値検索時の許容範囲（by_step_value=Trueの場合のみ有効）

Returns:
    ColumnCollection: ブレンド結果の列を含むColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合
    ValueError: 列の長さが一致しない場合、または無効な値や範囲が指定された場合"""
        ...
    

    def conditional_select(
        self,
        column1: str,
        column2: str,
        condition_column: str,
        threshold: Union[int, float] = 0,
        compare: str = '>',
        result_column: Optional[str] = None,
        in_place: bool = False
    ) -> "StrainCollectionOperations":
        """条件に基づいて2つのColumnから選択的に値を取得

指定された条件列の値と閾値を比較し、条件を満たす場合はcolumn1、
それ以外の場合はcolumn2の値を使用した新しいColumnを生成します。

Args:
    collection: ColumnCollectionオブジェクト
    column1: 条件を満たす場合に使用する列名
    column2: 条件を満たさない場合に使用する列名
    condition_column: 条件判定に使用する列名
    threshold: 条件判定の閾値
    compare: 比較演算子 (">", ">=", "<", "<=", "==", "!=")
    result_column: 結果を格納する列名（デフォルトはNone、自動生成）
    in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成

Returns:
    ColumnCollection: 条件選択結果の列を含むColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合
    ValueError: 列の長さが一致しない場合、または無効な比較演算子が指定された場合"""
        ...
    

    def custom_combine(
        self,
        column1: str,
        column2: str,
        combine_func: Callable[[Any, Any], Any],
        result_column: Optional[str] = None,
        func_name: Optional[str] = None,
        in_place: bool = False
    ) -> "StrainCollectionOperations":
        """カスタム関数を使用して2つのColumnを合成

指定されたカスタム関数を使用して、2つの列の値を要素ごとに合成した
新しいColumnを生成します。

Args:
    collection: ColumnCollectionオブジェクト
    column1: 1つ目の入力列名
    column2: 2つ目の入力列名
    combine_func: 2つの値を受け取り1つの値を返す関数
    result_column: 結果を格納する列名（デフォルトはNone、自動生成）
    func_name: 関数名（自動生成される列名で使用される識別子）
    in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成

Returns:
    ColumnCollection: カスタム合成結果の列を含むColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合
    ValueError: 列の長さが一致しない場合"""
        ...
    

    def sum_columns(
        self,
        columns: Optional[list[str]] = None,
        result_column: Optional[str] = None,
        in_place: bool = False
    ) -> "StrainCollectionOperations":
        """複数の列を合計して新しい列を作成します。

指定した複数の列の値を要素ごとに合計し、新しい列として追加します。
列名を指定しない場合は、すべての数値列が対象となります。

Args:
    collection: ColumnCollection オブジェクト
    columns: 合計対象の列名リスト（省略時はすべての数値列）
    result_column: 結果を格納する列名（デフォルトは None で自動生成）
    in_place: True の場合は元のオブジェクトを変更、False の場合は新しいオブジェクトを作成

Returns:
    ColumnCollection: 合計列を含む ColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合
    ValueError: 列の長さが一致しない場合"""
        ...
    

    def average_columns(
        self,
        columns: Optional[list[str]] = None,
        result_column: Optional[str] = None,
        in_place: bool = False
    ) -> "StrainCollectionOperations":
        """複数の列の平均値を計算して新しい列を作成します。

指定した複数の列の値を要素ごとに平均し、新しい列として追加します。
列名を指定しない場合は、すべての数値列が対象となります。

Args:
    collection: ColumnCollection オブジェクト
    columns: 平均対象の列名リスト（省略時はすべての数値列）
    result_column: 結果を格納する列名（デフォルトは None で自動生成）
    in_place: True の場合は元のオブジェクトを変更、False の場合は新しいオブジェクトを作成

Returns:
    ColumnCollection: 平均列を含む ColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合
    ValueError: 列の長さが一致しない場合"""
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
    

    def moving_average(
        self,
        column: str,
        window_size: int = 3,
        result_column: Optional[str] = None,
        edge_handling: str = 'asymmetric',
        in_place: bool = False
    ) -> "StrainCollectionOperations":
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
        column: str,
        window_size: int = 3,
        threshold: float = 0.5,
        edge_handling: str = 'asymmetric',
        min_abs_value: float = 1e-10,
        scale_factor: float = 1.0,
        result_column: Optional[str] = None
    ) -> "StrainCollectionOperations":
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
        column: str,
        sigma: float = 1.0,
        window_size: Optional[int] = None,
        result_column: Optional[str] = None,
        in_place: bool = False
    ) -> "StrainCollectionOperations":
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
    

    def smooth(
        self,
        column: str,
        method: str = 'moving_average',
        window_size: int = 3,
        sigma: float = 1.0,
        result_column: Optional[str] = None,
        in_place: bool = False,
        **kwargs
    ) -> "StrainCollectionOperations":
        """指定した列のデータを平滑化します

移動平均またはガウシアンフィルタを使用して、データのノイズを低減します。

Args:
    collection: 処理対象の ColumnCollection
    column: 処理対象の列名
    method: 平滑化手法 ("moving_average" または "gaussian")
    window_size: ウィンドウサイズ（移動平均用、ガウシアンの場合はフィルタサイズに影響）
    sigma: ガウシアンフィルタの標準偏差
    result_column: 結果を格納する列名
    in_place: True の場合、結果を元の列に上書き
    **kwargs: その他の引数（moving_averageのedge_handlingなど）

Returns:
    ColumnCollection: 平滑化された列を含むコレクション"""
        ...
    

    def ma(
        self,
        column: str,
        window_size: int = 3,
        result_column: Optional[str] = None,
        edge_handling: str = 'asymmetric',
        in_place: bool = False
    ) -> "StrainCollectionOperations":
        """moving_average のエイリアス"""
        ...
    

    def outliers(
        self,
        column: str,
        window_size: int = 3,
        threshold: float = 0.5,
        edge_handling: str = 'asymmetric',
        min_abs_value: float = 1e-10,
        scale_factor: float = 1.0,
        result_column: Optional[str] = None
    ) -> "StrainCollectionOperations":
        """detect_outliers のエイリアス"""
        ...
    

    def max(
        self,
        column: str
    ) -> float:
        """列の最大値を取得します

Args:
    collection: 対象のコレクション
    column: 列名
    
Returns:
    float: 最大値"""
        ...
    

    def min(
        self,
        column: str
    ) -> float:
        """列の最小値を取得します

Args:
    collection: 対象のコレクション
    column: 列名
    
Returns:
    float: 最小値"""
        ...
    

    def mean(
        self,
        column: str
    ) -> float:
        """列の平均値を取得します

Args:
    collection: 対象のコレクション
    column: 列名
    
Returns:
    float: 平均値"""
        ...
    

    def std(
        self,
        column: str
    ) -> float:
        """列の標準偏差を取得します

Args:
    collection: 対象のコレクション
    column: 列名
    
Returns:
    float: 標準偏差"""
        ...
    

    def sum(
        self,
        column: str
    ) -> float:
        """列の合計値を取得します

Args:
    collection: 対象のコレクション
    column: 列名
    
Returns:
    float: 合計値"""
        ...
    

    def sin(
        self,
        column: str,
        result_column: Optional[str] = None,
        in_place: bool = False,
        degrees: bool = False
    ) -> "StrainCollectionOperations":
        """指定した列の各値に sin 関数を適用します

指定された列の値に対して三角関数の sin を計算し、新しい列に結果を格納します。
角度の入力形式としてラジアンまたは度を選択できます。

Args:
    collection: ColumnCollection オブジェクト
    column: 処理対象の列名
    result_column: 結果を格納する列名（None の場合は "sin({column})" を使用）
    in_place: True の場合は元のオブジェクトを変更、False の場合は新しいオブジェクトを作成
    degrees: True の場合、入力を degree として扱う（デフォルトは False、ラジアン）

Returns:
    ColumnCollection: 結果の列を含む ColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合"""
        ...
    

    def cos(
        self,
        column: str,
        result_column: Optional[str] = None,
        in_place: bool = False,
        degrees: bool = False
    ) -> "StrainCollectionOperations":
        """指定した列の各値に cos 関数を適用します

指定された列の値に対して三角関数の cos を計算し、新しい列に結果を格納します。
角度の入力形式としてラジアンまたは度を選択できます。

Args:
    collection: ColumnCollection オブジェクト
    column: 処理対象の列名
    result_column: 結果を格納する列名（None の場合は "cos({column})" を使用）
    in_place: True の場合は元のオブジェクトを変更、False の場合は新しいオブジェクトを作成
    degrees: True の場合、入力を degree として扱う（デフォルトは False、ラジアン）

Returns:
    ColumnCollection: 結果の列を含む ColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合"""
        ...
    

    def tan(
        self,
        column: str,
        result_column: Optional[str] = None,
        in_place: bool = False,
        degrees: bool = False
    ) -> "StrainCollectionOperations":
        """指定した列の各値に tan 関数を適用します

指定された列の値に対して三角関数の tan を計算し、新しい列に結果を格納します。
角度の入力形式としてラジアンまたは度を選択できます。

Args:
    collection: ColumnCollection オブジェクト
    column: 処理対象の列名
    result_column: 結果を格納する列名（None の場合は "tan({column})" を使用）
    in_place: True の場合は元のオブジェクトを変更、False の場合は新しいオブジェクトを作成
    degrees: True の場合、入力を degree として扱う（デフォルトは False、ラジアン）

Returns:
    ColumnCollection: 結果の列を含む ColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合"""
        ...
    

    def exp(
        self,
        column: str,
        result_column: Optional[str] = None,
        in_place: bool = False
    ) -> "StrainCollectionOperations":
        """指定した列の各値に指数関数(e^x)を適用します

指定された列の各値に対して自然指数関数 e^x を計算し、結果を新しい列に格納します。
入力データが None の場合は結果も None になります。

Args:
    collection: ColumnCollection オブジェクト
    column: 処理対象の列名
    result_column: 結果を格納する列名（None の場合は "exp({column})" を使用）
    in_place: True の場合は元のオブジェクトを変更、False の場合は新しいオブジェクトを作成

Returns:
    ColumnCollection: 結果の列を含む ColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合"""
        ...
    

    def log(
        self,
        column: str,
        base: float = 2.718281828459045,
        result_column: Optional[str] = None,
        in_place: bool = False
    ) -> "StrainCollectionOperations":
        """指定した列の各値に対数関数を適用します

指定された列の各値に対して対数関数を計算し、結果を新しい列に格納します。
対数の底を指定できるほか、自然対数（底が e）やログ 10 なども計算できます。

Args:
    collection: ColumnCollection オブジェクト
    column: 処理対象の列名
    base: 対数の底（デフォルトは e）
    result_column: 結果を格納する列名（None の場合は "log({column})" または "log{base}({column})" を使用）
    in_place: True の場合は元のオブジェクトを変更、False の場合は新しいオブジェクトを作成

Returns:
    ColumnCollection: 結果の列を含む ColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合
    ValueError: 0 以下の値に対して対数を適用しようとした場合"""
        ...
    

    def sqrt(
        self,
        column: str,
        result_column: Optional[str] = None,
        in_place: bool = False
    ) -> "StrainCollectionOperations":
        """指定した列の各値の平方根を計算します

指定された列の各値の平方根を計算し、結果を新しい列に格納します。
負の値に対しては None が格納されます。

Args:
    collection: ColumnCollection オブジェクト
    column: 処理対象の列名
    result_column: 結果を格納する列名（None の場合は "sqrt({column})" を使用）
    in_place: True の場合は元のオブジェクトを変更、False の場合は新しいオブジェクトを作成

Returns:
    ColumnCollection: 結果の列を含む ColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合
    ValueError: 負の値に対して平方根を適用しようとした場合"""
        ...
    

    def pow(
        self,
        column: str,
        exponent: float,
        result_column: Optional[str] = None,
        in_place: bool = False
    ) -> "StrainCollectionOperations":
        """指定した列の各値を指定した指数でべき乗します

指定された列の各値を指定された指数でべき乗し、結果を新しい列に格納します。
非数値データや計算エラーが発生した場合は None が格納されます。

Args:
    collection: ColumnCollection オブジェクト
    column: 処理対象の列名
    exponent: べき指数
    result_column: 結果を格納する列名（None の場合は "{column}^{exponent}" を使用）
    in_place: True の場合は元のオブジェクトを変更、False の場合は新しいオブジェクトを作成

Returns:
    ColumnCollection: 結果の列を含む ColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合"""
        ...
    

    def abs_values(
        self,
        column: str,
        result_column: Optional[str] = None,
        in_place: bool = False
    ) -> "StrainCollectionOperations":
        """指定した列の各値の絶対値を計算します

指定された列の各値の絶対値を計算し、結果を新しい列に格納します。
None 値は結果でも None として維持されます。

Args:
    collection: ColumnCollection オブジェクト
    column: 処理対象の列名
    result_column: 結果を格納する列名（None の場合は "abs({column})" を使用）
    in_place: True の場合は元のオブジェクトを変更、False の場合は新しいオブジェクトを作成

Returns:
    ColumnCollection: 結果の列を含む ColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合"""
        ...
    

    def round_values(
        self,
        column: str,
        decimals: int = 0,
        result_column: Optional[str] = None,
        in_place: bool = False
    ) -> "StrainCollectionOperations":
        """指定した列の各値を指定した小数点以下の桁数に丸めます

指定された列の各値を指定された小数点以下の桁数で四捨五入し、結果を新しい列に格納します。
None 値は結果でも None として維持されます。

Args:
    collection: ColumnCollection オブジェクト
    column: 処理対象の列名
    decimals: 丸める小数点以下の桁数（デフォルトは 0、整数）
    result_column: 結果を格納する列名（None の場合は "round({column}, {decimals})" を使用）
    in_place: True の場合は元のオブジェクトを変更、False の場合は新しいオブジェクトを作成

Returns:
    ColumnCollection: 結果の列を含む ColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合"""
        ...
    

    def normalize(
        self,
        column: str,
        result_column: Optional[str] = None,
        in_place: bool = False,
        method: str = 'minmax'
    ) -> "StrainCollectionOperations":
        """指定した列の値を正規化します

指定された列の値を指定された方法で正規化します。
"minmax" 法では [0, 1] の範囲に、"zscore" 法では平均 0、標準偏差 1 に正規化します。

Args:
    collection: ColumnCollection オブジェクト
    column: 処理対象の列名
    result_column: 結果を格納する列名（None の場合は "norm_{method}({column})" を使用）
    in_place: True の場合は元のオブジェクトを変更、False の場合は新しいオブジェクトを作成
    method: 正規化方法
        "minmax": [0, 1] の範囲に正規化
        "zscore": 平均 0、標準偏差 1 に正規化

Returns:
    ColumnCollection: 結果の列を含む ColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合
    ValueError: 不正な method 値が指定された場合、または値が一定で正規化できない場合"""
        ...
    

    def interpolate(
        self,
        base_column_name: str = 'step',
        x_values: Optional[list[float]] = None,
        point_count: Optional[int] = None,
        method: str = 'linear',
        columns: Optional[list[str]] = None
    ) -> "StrainCollectionOperations":
        """指定した列の値に基づいてデータを内挿します

基準となる列の値に基づいて、他の列のデータを線形内挿します。
等間隔の内挿点を生成するか、特定の値での内挿を行うかを選択できます。

Args:
    collection: 内挿を行う ColumnCollection オブジェクト
    base_column_name: 内挿の基準となる列名（デフォルト: "step"）
    x_values: 内挿する目標値のリスト
    point_count: 等間隔内挿を行う場合のポイント数
    method: 内挿方法（現在は 'linear' のみサポート）
    columns: 値の計算に使用する列名リスト（None の場合はすべての数値型列）

Returns:
    ColumnCollection: 内挿された新しい ColumnCollection

Raises:
    ValueError: x_values と point_count の両方が指定された場合、または両方が指定されていない場合
    KeyError: 指定された列が存在しない場合
    TypeError: 指定された列が数値型でない場合

Examples:
    # ステップ値に基づいて内挿
    >>> result = collection.ops.interpolate(point_count=100)

    # 特定のステップ値で内挿
    >>> result = collection.ops.interpolate(x_values=[1.0, 2.5, 3.0, 4.5])

    # position列の値に基づいて内挿
    >>> result = collection.ops.interpolate(
    ...     base_column_name="position", point_count=100
    ... )"""
        ...
    

    def split_by_integers(
        self,
        markers: list[int]
    ) -> "CollectionListOperations[StrainCollectionOperations]":
        """整数リストの値でデータを分割します

同じマーカー値を持つデータは同じグループに集約されます。
マーカー値の種類に応じて複数のコレクションを生成します。

Args:
    collection: 分割する ColumnCollection オブジェクト
    markers: 各データ値がどのグループに属するかを示す整数リスト（データと同じ長さ）

Returns:
    List[ColumnCollection]: 分割後の ColumnCollection オブジェクトのリスト。
    各 ColumnCollection は同じマーカー値を持つデータで構成され、
    マーカー値に基づいて昇順に並べられます。

Raises:
    ValueError: データとマーカーの長さが一致しない場合

Examples:
    # データ値を 3 つのグループに分類
    markers = [2, 1, 2, 3, 1, 3]  # マーカー値が示す分類グループ
    collection_groups = split_by_integers(collection, markers)
    # 結果: [グループ 1 の Collection, グループ 2 の Collection, グループ 3 の Collection]"""
        ...
    

    def split_at_indices(
        self,
        indices: Union[int, list[int]]
    ) -> "CollectionListOperations[StrainCollectionOperations]":
        """指定されたインデックスでコレクションを分割します

Args:
    collection: 分割する ColumnCollection オブジェクト
    indices: 分割するインデックス（intまたはList[int]）

Returns:
    List[ColumnCollection]: 分割後の ColumnCollection オブジェクトのリスト"""
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
