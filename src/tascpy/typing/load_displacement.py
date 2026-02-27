# 自動生成されたload_displacementドメインのスタブファイル - 編集しないでください
from typing import Optional, Union, List, Dict, Any, Callable, TypeVar, cast, Generic, overload, Literal
from ..core.collection import ColumnCollection
from ..domains.load_displacement import LoadDisplacementCollection
from .proxy_base import CollectionOperationsBase
from .list_proxy import CollectionListOperations
from .core import CoreCollectionOperations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .strain import StrainCollectionOperations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .coordinate import CoordinateCollectionOperations

class LoadDisplacementCollectionOperations(CollectionOperationsBase[LoadDisplacementCollection]):
    """load_displacementドメインの操作メソッドスタブ定義
    
    このクラスはPylanceの型チェックとオートコンプリートのためのスタブです。
    実際の実行には使用されません。
    """

    def end(self) -> LoadDisplacementCollection:
        """操作チェーンを終了し、最終的なColumnCollectionを取得"""
        ...

    def debug(self, message: Optional[str] = None) -> "LoadDisplacementCollectionOperations":
        """デバッグメッセージを表示
        
        Args:
            message: デバッグメッセージ
        
        Returns:
            LoadDisplacementCollectionOperations: 自身を返す
        """
        ...


    def get_load_column(
        self,
        
    ) -> str:
        """荷重データのカラム名を取得

Args:
    collection: 荷重-変位コレクション

Returns:
    str: 荷重データのカラム名"""
        ...
    

    def get_displacement_column(
        self,
        
    ) -> str:
        """変位データのカラム名を取得

Args:
    collection: 荷重-変位コレクション

Returns:
    str: 変位データのカラム名"""
        ...
    

    def get_load_data(
        self,
        
    ) -> ndarray:
        """荷重データを取得

Args:
    collection: 荷重-変位コレクション

Returns:
    np.ndarray: 荷重データの配列"""
        ...
    

    def get_displacement_data(
        self,
        
    ) -> ndarray:
        """変位データを取得

Args:
    collection: 荷重-変位コレクション

Returns:
    np.ndarray: 変位データの配列"""
        ...
    

    def get_valid_data_mask(
        self,
        
    ) -> ndarray:
        """有効なデータポイントのマスクを取得

Args:
    collection: 荷重-変位コレクション

Returns:
    np.ndarray: 有効なデータのブールマスク"""
        ...
    

    def get_valid_data(
        self,
        
    ) -> tuple[ndarray, ndarray]:
        """有効な荷重と変位のデータ組を取得

Args:
    collection: 荷重-変位コレクション

Returns:
    Tuple[np.ndarray, np.ndarray]: 有効な(変位, 荷重)データの組"""
        ...
    

    def calculate_slopes(
        self,
        disp_data: column = <class 'float'>,
        load_data: column = <class 'float'>,
        column: column = <class 'float'>,
        load_data: ndarray
    ) -> ndarray:
        """変位と荷重の間の点ごとの傾きを計算します。

Args:
    disp_data: 変位データの配列
    load_data: 荷重データの配列
    
Returns:
    np.ndarray: 計算された傾きの配列（最初の要素は NaN）"""
        ...
    

    def calculate_stiffness(
        self,
        disp_data: column = <class 'float'>,
        load_data: column = <class 'float'>,
        range_start: float = 0.2,
        range_end: float = 0.8,
        method: str = 'linear_regression',
        column: column = <class 'float'>,
        load_data: ndarray,
        range_start: float = 0.2,
        range_end: float = 0.8,
        method: str = 'linear_regression'
    ) -> float:
        """指定範囲における剛性（傾き）を計算します。

Args:
    disp_data: 変位データの配列 (NaN/None 除去済み)
    load_data: 荷重データの配列 (NaN/None 除去済み)
    range_start: 最大荷重に対する計算開始点の割合
    range_end: 最大荷重に対する計算終了点の割合
    method: 計算方法 ("linear_regression" または "secant")

Returns:
    float: 計算された剛性値"""
        ...
    

    def find_yield_point(
        self,
        disp_data: column = <class 'float'>,
        load_data: column = <class 'float'>,
        method: str = 'offset',
        offset_value: float = 0.002,
        range_start: float = 0.1,
        range_end: float = 0.3,
        factor: float = 0.33,
        debug_mode: bool = False,
        fail_silently: bool = False,
        column: column = <class 'float'>,
        load_data: ndarray,
        method: str = 'offset',
        offset_value: float = 0.002,
        range_start: float = 0.1,
        range_end: float = 0.3,
        factor: float = 0.33,
        debug_mode: bool = False,
        fail_silently: bool = False
    ) -> tuple[bool, float, float, dict[str, Any]]:
        """"""
        ...
    

    def create_skeleton_curve(
        self,
        load_column: Optional[str] = None,
        displacement_column: Optional[str] = None,
        cycle_marker_column: Optional[str] = None,
        has_decrease: bool = False,
        decrease_type: str = 'envelope'
    ) -> tuple[ndarray, ndarray, dict]:
        """"""
        ...
    

    def create_cumulative_curve(
        self,
        load_column: Optional[str] = None,
        displacement_column: Optional[str] = None,
        cycle_marker_column: Optional[str] = None
    ) -> tuple[ndarray, ndarray, dict]:
        """"""
        ...
    

    def cycle_count(
        self,
        data: column = <class 'float'>,
        step: float = 0.5,
        column: column = <class 'float'>,
        step: float = 0.5
    ) -> ndarray:
        """データの符号反転からサイクル数をカウントします。

Args:
    data: 対象データ配列
    step: サイクルカウントの増分
    
Returns:
    np.ndarray: サイクルマーカーの配列"""
        ...
    

    def split_by_cycles(
        self,
        cycle_column: Optional[str] = None
    ) -> "CollectionListOperations[LoadDisplacementCollectionOperations]":
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
    ) -> "LoadDisplacementCollectionOperations":
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
    ) -> "LoadDisplacementCollectionOperations":
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
    ) -> "LoadDisplacementCollectionOperations":
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
    

    def plot_load_displacement(
        self,
        ax: Optional[Axes] = None,
        **kwargs
    ) -> Axes:
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
    ) -> Axes:
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
    ) -> Axes:
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
    ) -> Axes:
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
    ) -> Axes:
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
    ) -> Axes:
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
    ) -> Axes:
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
    ) -> "CollectionListOperations[LoadDisplacementCollectionOperations]":
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
        y_column: str,
        x_column: Optional[str] = None,
        ax: Optional[Axes] = None,
        **kwargs
    ) -> Axes:
        """基本的なプロットを行います"""
        ...
    

    def visualize_outliers(
        self,
        column: str,
        x_column: Optional[str] = None,
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
        """異常値を検出し可視化します"""
        ...
    

    def plot_const_x(
        self,
        x_values: list[float],
        y_columns: list[str],
        ax: Optional[Axes] = None,
        **kwargs
    ) -> Axes:
        """共通のX軸に対して複数のY列をプロットします"""
        ...
    

    def iplot(
        self,
        y_column: str,
        x_column: Optional[str] = None,
        **kwargs
    ) -> Any:
        """インタラクティブなプロットを行います（Jupyter用）"""
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
    ) -> "CollectionListOperations[LoadDisplacementCollectionOperations]":
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
    

    def split_by_integers(
        self,
        markers: Union[list[int], ndarray]
    ) -> "CollectionListOperations[LoadDisplacementCollectionOperations]":
        """整数マーカーに基づいてコレクションを分割します。

ユニークなマーカー値ごとに、そのマーカーに対応するデータを含む
新しい ColumnCollection のリストを返します。

Args:
    collection: 対象の ColumnCollection
    markers: 各要素に対応する整数マーカーのリストまたは配列。長さはコレクションの長さと一致する必要があります。

Returns:
    List[ColumnCollection]: 分割されたコレクションのリスト"""
        ...
    

    def split_at_indices(
        self,
        indices: Union[int, list[int]]
    ) -> "CollectionListOperations[LoadDisplacementCollectionOperations]":
        """指定されたインデックスでコレクションを分割します。

Args:
    collection: 対象の ColumnCollection
    indices: 分割点となるインデックス（またはそのリスト）

Returns:
    List[ColumnCollection]: 分割されたコレクションのリスト"""
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
    ) -> "CollectionListOperations[LoadDisplacementCollectionOperations]":
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
        window_size: int = 3,
        edge_handling: str = 'asymmetric',
        column: str,
        window_size: int = 3,
        edge_handling = 'asymmetric'
    ) -> "CollectionListOperations[LoadDisplacementCollectionOperations]":
        """"""
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
    ) -> "LoadDisplacementCollectionOperations":
        """指定した列の値に基づいてデータを内挿します"""
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
    def as_domain(self, domain: Literal['strain'], **kwargs: Any) -> StrainCollectionOperations:
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
