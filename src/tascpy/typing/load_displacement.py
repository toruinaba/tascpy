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


    def calculate_slopes(
        self,
        disp_data: column = <class 'float'>,
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
        has_decrease: bool = False,
        decrease_type: str = 'envelope',
        column: str,
        displacements: ndarray,
        markers: ndarray,
        has_decrease: bool = False,
        decrease_type: str = 'envelope',
        *args,
        **kwargs
    ) -> tuple[list[float], list[float]]:
        """荷重-変位データからスケルトン曲線（包絡線）を生成します

Args:
    collection (LoadDisplacementCollection): 荷重-変位コレクション
    load_column (str, optional): 荷重データのカラム名（None時は自動解決）
    displacement_column (str, optional): 変位データのカラム名（None時は自動解決）
    cycle_marker_column (str, optional): サイクルマーカーカラム名（None時は自動解決）
    has_decrease (bool, optional): 剛性低下を考慮するかどうか. Defaults to False.
    decrease_type (str, optional): 剛性低下の計算手法. Defaults to "envelope".
    
Returns:
    LoadDisplacementCollection: スケルトン曲線データが結果として追加された新しいコレクション"""
        ...
    

    def create_cumulative_curve(
        self,
        displacements: ndarray,
        markers: ndarray,
        *args,
        **kwargs
    ) -> tuple[list[float], list[float]]:
        """荷重-変位データから累積塑性変形-荷重曲線を生成します

Args:
    collection (LoadDisplacementCollection): 荷重-変位コレクション
    load_column (str, optional): 荷重データのカラム名（None時は自動解決）
    displacement_column (str, optional): 変位データのカラム名（None時は自動解決）
    cycle_marker_column (str, optional): サブサイクル判定用のマーカーカラム名
    
Returns:
    LoadDisplacementCollection: 累積曲線データが結果として追加された新しいコレクション"""
        ...
    

    def cycle_count(
        self,
        data: column = <class 'float'>,
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
        column: str,
        disps: ndarray,
        markers: ndarray,
        *args,
        **kwargs
    ) -> tuple[float, float, float, float, float, float]:
        """各サイクルのヒステリシスエネルギー（面積）と最大/最小荷重・変位を計算します

Args:
    collection (LoadDisplacementCollection): 荷重-変位コレクション
    cycle_column (str, optional): サイクル番号のカラム名（None時は自動解決）
    load_column (str, optional): 荷重データのカラム名（None時は自動解決）
    displacement_column (str, optional): 変位データのカラム名（None時は自動解決）
    cycle_marker_column (str, optional): サブサイクル判定用のマーカーカラム名
    
Returns:
    LoadDisplacementCollection: サイクルごとの統計量を持つ新しいコレクション"""
        ...
    

    def analyze_stiffness_degradation(
        self,
        column: str,
        disps: ndarray,
        markers: ndarray,
        *args,
        **kwargs
    ) -> tuple[float, float]:
        """各サイクルの割線剛性（剛性低下）を評価します

Args:
    collection (LoadDisplacementCollection): 荷重-変位コレクション
    cycle_column (str, optional): サイクル番号のカラム名（None時は自動解決）
    load_column (str, optional): 荷重データのカラム名（None時は自動解決）
    displacement_column (str, optional): 変位データのカラム名（None時は自動解決）
    cycle_marker_column (str, optional): サブサイクル判定用のマーカーカラム名
    
Returns:
    LoadDisplacementCollection: サイクルごとの割線剛性を持つ新しいコレクション"""
        ...
    

    def find_peaks_and_valleys(
        self,
        data: column = <class 'float'>,
        distance: int = 1,
        threshold: float = None,
        column: column = <class 'float'>,
        distance: int = 1,
        threshold: Optional[float] = None
    ) -> ndarray:
        """配列内の極大値(1)と極小値(-1)を検出します。

Args:
    data: 対象データ配列
    distance: ピーク間の最小距離（インデックス数）
    threshold: 隣接点との最小差
    
Returns:
    np.ndarray: ピーク(1)、バレー(-1)、その他(0)のフラグ配列"""
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
        """複数カラムの要素ごとの和を計算します"""
        ...
    

    def subtract(
        self,
        column: str,
        v2: Union[ndarray, float]
    ) -> ndarray:
        """第一カラムから第二カラムの要素ごとの差を計算します"""
        ...
    

    def multiply(
        self,
        column: str,
        v2: Union[ndarray, float]
    ) -> ndarray:
        """複数カラムの要素ごとの積を計算します"""
        ...
    

    def divide(
        self,
        column: str,
        v2: Union[ndarray, float],
        **kwargs
    ) -> ndarray:
        """第一カラムを第二カラムで要素ごとに除算します"""
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
        """データ系列の離散微分 (dy/dx) を計算します

Args:
    collection (ColumnCollection): データコレクション
    y_column (str): Y軸データとなるカラム名
    x_column (str): X軸データとなるカラム名
    method (str, optional): 微分手法 ("forward", "backward", "central"). Defaults to "central".
    
Returns:
    ColumnCollection: 微分値カラムが追加された新しいコレクション"""
        ...
    

    def integrate(
        self,
        y: y_values = <class 'numpy.ndarray'>,
        x: x_values = <class 'numpy.ndarray'>,
        method: str = 'trapezoidal',
        initial_value: float = 0.0,
        column: y_values = <class 'numpy.ndarray'>,
        x: Union[ndarray, list[float]],
        method: str = 'trapezoid',
        initial_value: float = 0.0
    ) -> ndarray:
        """データ系列の離散積分 (∫ y dx) を計算します

Args:
    collection (ColumnCollection): データコレクション
    y_column (str): Y軸データとなるカラム名
    x_column (str): X軸データとなるカラム名
    method (str, optional): 積分手法 ("trapezoidal", "cumulative_sum"). Defaults to "trapezoidal".
    initial_value (float, optional): 積分定数 (初期値). Defaults to 0.0.
    
Returns:
    ColumnCollection: 積分値カラムが追加された新しいコレクション"""
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
        """指定されたウィンドウサイズで移動平均を計算します

Args:
    collection (ColumnCollection): データコレクション
    column_name (str): 計算対象のカラム名
    window_size (int, optional): 移動平均のウィンドウサイズ. Defaults to 3.
    edge_handling (str, optional): 端の処理方法 ("asymmetric", "symmetric", "constant", "mirror", "wrap"). Defaults to "asymmetric".
    
Returns:
    ColumnCollection: 移動平均値が追加された新しいコレクション"""
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
        """異常値を検出します

Args:
    collection (ColumnCollection): データコレクション
    column_name (str): 計算対象のカラム名
    window_size (int, optional): 移動平均などのウィンドウサイズ. Defaults to 3.
    threshold (float, optional): 異常と判定する閾値. Defaults to 0.5.
    edge_handling (str, optional): 端の処理方法. Defaults to "asymmetric".
    min_abs_value (float, optional): ゼロ除算を防ぐための最小絶対値. Defaults to 1e-10.
    scale_factor (float, optional): スケールファクタ. Defaults to 1.0.

Returns:
    ColumnCollection: 異常値フラグが追加された新しいコレクション"""
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
        """ガウシアンフィルターを適用します

Args:
    collection (ColumnCollection): データコレクション
    column_name (str): 計算対象のカラム名
    sigma (float, optional): ガウス関数の標準偏差. Defaults to 1.0.
    window_size (Optional[int], optional): ウィンドウサイズ. Defaults to None.
    
Returns:
    ColumnCollection: フィルター処理後の値が追加された新しいコレクション"""
        ...
    

    def max(
        self,
        column: str
    ) -> float:
        """カラムの最大値を計算します"""
        ...
    

    def min(
        self,
        column: str
    ) -> float:
        """カラムの最小値を計算します"""
        ...
    

    def mean(
        self,
        column: str
    ) -> float:
        """カラムの平均値を計算します"""
        ...
    

    def std(
        self,
        column: str
    ) -> float:
        """カラムの標準偏差を計算します"""
        ...
    

    def sum(
        self,
        column: str
    ) -> float:
        """カラムの合計値を計算します"""
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
