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
        mode: str = 'any'
    ) -> List[list[bool]]:
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
        mode: str = 'consecutive',
        dup_type: str = 'all'
    ) -> List[list[int]]:
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
        *args,
        **kwargs
    ) -> List[Any]:
        """"""
        ...
    

    def filter_by_condition(
        self,
        condition: <built-in function callable>
    ) -> "CollectionListOperations[C]":
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
    ) -> List[list[bool]]:
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
        op_str: str,
        value: Any
    ) -> List[list[int]]:
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
        min_value: Any,
        max_value: Any,
        inclusive: bool = True
    ) -> List[list[int]]:
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
    ) -> List[list[int]]:
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
        condition_func: Callable[[Dict[str, Any]], bool]
    ) -> List[list[int]]:
        """条件関数を満たす行のインデックスを検索します。

Args:
    data (Dict[str, Any]): カラム名をキーとするデータ辞書。
    condition_func (Callable[[Dict[str, Any]], bool]): 行データ（辞書）を受け取り、boolを返す関数。

Returns:
    List[int]: 条件を満たす行のインデックスリスト。"""
        ...
    

    def search_missing_values(
        self,
        
    ) -> List[list[int]]:
        """欠損値を含む行のインデックスを検索します。

Args:
    data (Dict[str, Any]): カラム名をキーとするデータ辞書。

Returns:
    List[int]: いずれかのカラムに欠損値を含む行のインデックスリスト。"""
        ...
    

    def search_top_n(
        self,
        n: int,
        descending: bool = True
    ) -> List[list[int]]:
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
    ) -> List[Axes]:
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
    ) -> List[Axes]:
        """異常値を検出し可視化します"""
        ...
    

    def plot_const_x(
        self,
        x_values: list[float],
        y_columns: list[str],
        ax: Optional[Axes] = None,
        **kwargs
    ) -> List[Axes]:
        """共通のX軸に対して複数のY列をプロットします"""
        ...
    

    def iplot(
        self,
        y_column: str,
        x_column: Optional[str] = None,
        **kwargs
    ) -> List[Any]:
        """インタラクティブなプロットを行います（Jupyter用）"""
        ...
    

    def select(
        self,
        columns: Optional[list[str]] = None,
        indices: Optional[list[int]] = None,
        steps: Optional[list[Union[int, float]]] = None,
        by_step_value: bool = True,
        tolerance: Optional[float] = None
    ) -> List[tuple[list[int], dict[str, Any]]]:
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
        value: float,
        **kwargs
    ) -> "CollectionListOperations[C]":
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
    ) -> "CollectionListOperations[C]":
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
    ) -> "CollectionListOperations[C]":
        """指定されたインデックスでコレクションを分割します。

Args:
    collection: 対象の ColumnCollection
    indices: 分割点となるインデックス（またはそのリスト）

Returns:
    List[ColumnCollection]: 分割されたコレクションのリスト"""
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
        v1: ndarray,
        v2: ndarray,
        start: Union[int, float],
        end: Union[int, float],
        compare_mode: str = 'value',
        by_step_value: bool = True,
        blend_method: str = 'linear',
        tolerance: Optional[float] = None
    ) -> List[ndarray]:
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
        v2: Any,
        combine_func: Callable[[Any, Any], Any],
        **kwargs
    ) -> "CollectionListOperations[C]":
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
        v2: Union[ndarray, float]
    ) -> List[ndarray]:
        """2つの値または配列を加算します。

Args:
    v1 (Union[np.ndarray, float]): 最初の値または配列。
    v2 (Union[np.ndarray, float]): 2番目の値または配列。

Returns:
    np.ndarray: 加算結果。"""
        ...
    

    def subtract(
        self,
        v2: Union[ndarray, float]
    ) -> List[ndarray]:
        """v1 から v2 を減算します。

Args:
    v1 (Union[np.ndarray, float]): 最初の値または配列。
    v2 (Union[np.ndarray, float]): 引く値または配列。

Returns:
    np.ndarray: 減算結果。"""
        ...
    

    def multiply(
        self,
        v2: Union[ndarray, float]
    ) -> List[ndarray]:
        """2つの値または配列を乗算します。

Args:
    v1 (Union[np.ndarray, float]): 最初の値または配列。
    v2 (Union[np.ndarray, float]): 2番目の値または配列。

Returns:
    np.ndarray: 乗算結果。"""
        ...
    

    def divide(
        self,
        v2: Union[ndarray, float],
        **kwargs
    ) -> List[ndarray]:
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
        x: Union[ndarray, list[float]],
        method: str = 'central'
    ) -> List[ndarray]:
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
        x: Union[ndarray, list[float]],
        method: str = 'trapezoid',
        initial_value: float = 0.0
    ) -> List[ndarray]:
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
        expression: str,
        **kwargs
    ) -> List[Union[list[Optional[float]], ndarray]]:
        """"""
        ...
    

    def sin(
        self,
        degrees: bool = False
    ) -> List[ndarray]:
        """正弦(sin)を計算します。

Args:
    values (np.ndarray): 入力値の配列。
    degrees (bool, optional): 入力が度数法(degree)かどうか。Trueの場合はラジアンに変換してから計算します。デフォルトは False（ラジアン）。

Returns:
    np.ndarray: 計算結果の配列。"""
        ...
    

    def cos(
        self,
        degrees: bool = False
    ) -> List[ndarray]:
        """余弦(cos)を計算します。

Args:
    values (np.ndarray): 入力値の配列。
    degrees (bool, optional): 入力が度数法(degree)かどうか。Trueの場合はラジアンに変換してから計算します。デフォルトは False（ラジアン）。

Returns:
    np.ndarray: 計算結果の配列。"""
        ...
    

    def tan(
        self,
        degrees: bool = False
    ) -> List[ndarray]:
        """正接(tan)を計算します。

Args:
    values (np.ndarray): 入力値の配列。
    degrees (bool, optional): 入力が度数法(degree)かどうか。Trueの場合はラジアンに変換してから計算します。デフォルトは False（ラジアン）。

Returns:
    np.ndarray: 計算結果の配列。"""
        ...
    

    def exp(
        self,
        
    ) -> List[ndarray]:
        """指数関数(exp)を計算します。

Args:
    values (np.ndarray): 入力値の配列。

Returns:
    np.ndarray: 計算結果の配列。"""
        ...
    

    def log(
        self,
        base: float = 2.718281828459045
    ) -> List[ndarray]:
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
        
    ) -> List[ndarray]:
        """平方根(sqrt)を計算します。

負の値はNaNになります。

Args:
    values (np.ndarray): 入力値の配列。

Returns:
    np.ndarray: 計算結果の配列。"""
        ...
    

    def pow(
        self,
        exponent: float
    ) -> List[ndarray]:
        """累乗(power)を計算します。

Args:
    values (np.ndarray): 基数の配列。
    exponent (float): 指数。

Returns:
    np.ndarray: 計算結果の配列。"""
        ...
    

    def abs_values(
        self,
        
    ) -> List[ndarray]:
        """絶対値(absolute value)を計算します。

Args:
    values (np.ndarray): 入力値の配列。

Returns:
    np.ndarray: 計算結果の配列。"""
        ...
    

    def round_values(
        self,
        decimals: int = 0
    ) -> List[ndarray]:
        """値を指定された桁数で丸めます。

Args:
    values (np.ndarray): 入力値の配列。
    decimals (int, optional): 丸める小数点以下の桁数。デフォルトは 0。

Returns:
    np.ndarray: 計算結果の配列。"""
        ...
    

    def normalize(
        self,
        method: str = 'minmax'
    ) -> List[ndarray]:
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
        edge_handling = 'asymmetric'
    ) -> "CollectionListOperations[C]":
        """"""
        ...
    

    def detect_outliers(
        self,
        window_size: int = 3,
        threshold: float = 0.5,
        edge_handling: str = 'asymmetric',
        min_abs_value: float = 1e-10,
        scale_factor: float = 1.0
    ) -> List[list[int]]:
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
        sigma: float = 1.0,
        window_size: Optional[int] = None
    ) -> List[Any]:
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
        
    ) -> List[float]:
        """最大値を計算します（NaNは無視されます）。

Args:
    vals (Any): 入力値の配列またはリスト。

Returns:
    float: 最大値。"""
        ...
    

    def min(
        self,
        
    ) -> List[float]:
        """最小値を計算します（NaNは無視されます）。

Args:
    vals (Any): 入力値の配列またはリスト。

Returns:
    float: 最小値。"""
        ...
    

    def mean(
        self,
        
    ) -> List[float]:
        """平均値を計算します（NaNは無視されます）。

Args:
    vals (Any): 入力値の配列またはリスト。

Returns:
    float: 平均値。"""
        ...
    

    def std(
        self,
        
    ) -> List[float]:
        """標準偏差を計算します（NaNは無視されます）。

Args:
    vals (Any): 入力値の配列またはリスト。

Returns:
    float: 標準偏差。"""
        ...
    

    def sum(
        self,
        
    ) -> List[float]:
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
    ) -> "CollectionListOperations[C]":
        """指定した列の値に基づいてデータを内挿します"""
        ...
    

    def test_filter(
        self,
        column_name,
        value
    ) -> List[Any]:
        """テスト用フィルタリング操作"""
        ...
    

    def add_derived_column(
        self,
        formula,
        output_column
    ) -> List[Any]:
        """数式に基づいて派生列を追加"""
        ...
    

    def extract_coordinates(
        self,
        y_array: Optional[ndarray] = None,
        z_array: Optional[ndarray] = None,
        length: int = 1
    ) -> List[dict[str, ndarray]]:
        """各列の座標値を新しい列としてコレクションに追加します

座標情報が設定されている列の x、y、z 座標値を取得し、それぞれを独立した列として
コレクションに追加します。新しい列名には指定された接頭辞が付与されます。

Args:
    collection: 座標コレクション
    result_prefix: 結果列の接頭辞 (デフォルト: "coord_")

Returns:
    CoordinateCollection: 座標列を追加したコレクション"""
        ...
    

    def calculate_distance(
        self,
        p1_y: float,
        p2_x: float,
        p2_y: float,
        p1_z: float = None,
        p2_z: float = None
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
        n_neighbors: int
    ) -> List[list[tuple[str, float]]]:
        """指定した列に最も近い座標を持つ近傍列を探します

指定された列を基準として、座標空間上で最も近い n 個の列を探索します。
結果はメタデータに保存され、近傍情報も新しい列として追加されます。

Args:
    collection: 座標コレクション
    column: 基準となる列名
    n_neighbors: 取得する近傍の数 (デフォルト: 3)
    result_column: 結果列名（None の場合、自動生成）

Returns:
    CoordinateCollection: 近傍情報を含むコレクション"""
        ...
    

    def spatial_clustering(
        self,
        n_clusters: int,
        max_iter: int = 100
    ) -> List[ndarray]:
        """座標情報に基づいてクラスタリングを行います

列の座標位置に基づいて、類似した位置にある列をグループ化します。
クラスタリング結果はメタデータに保存され、各列のクラスタ情報も追加されます。

Args:
    collection: 座標コレクション
    n_clusters: クラスタ数 (デフォルト: 2)
    columns: クラスタリング対象の列名リスト（None の場合は座標を持つ全列）
    result_column: 結果列名 (デフォルト: "cluster")
    algorithm: クラスタリングアルゴリズム (デフォルト: "kmeans")

Returns:
    CoordinateCollection: クラスタリング結果を含むコレクション"""
        ...
    

    def distance(
        self,
        p1_y: float,
        p2_x: float,
        p2_y: float,
        p1_z: float = None,
        p2_z: float = None
    ) -> List[float]:
        """calculate_distance のエイリアス"""
        ...
    

    def nearest_neighbors(
        self,
        n_neighbors: int
    ) -> List[list[tuple[str, float]]]:
        """find_nearest_neighbors のエイリアス"""
        ...
    

    def cluster(
        self,
        n_clusters: int,
        max_iter: int = 100
    ) -> List[ndarray]:
        """spatial_clustering のエイリアス"""
        ...
    

    def interpolate_at_point(
        self,
        x: float,
        y: float,
        z: Optional[float],
        method: str,
        power: float
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
    CoordinateCollection: 補間結果を含むコレクション"""
        ...
    

    def interpolate_grid(
        self,
        x_grid: ndarray,
        y_grid: ndarray,
        method: str,
        power: float
    ) -> List[ndarray]:
        """指定した領域のグリッド上で値を補間します

指定された x-y 平面上の矩形領域をグリッドに分割し、各グリッド点での値を補間します。
補間結果はメタデータと結果列に保存されます。

Args:
    collection: 座標コレクション
    x_range: X 座標の範囲 (min, max)
    y_range: Y 座標の範囲 (min, max)
    grid_size: グリッドサイズ (nx, ny) (デフォルト: (10, 10))
    target_column: 補間対象の列名
    method: 補間方法 ("inverse_distance", "nearest", "linear")
    power: 逆距離加重法のパワーパラメータ
    result_prefix: 結果列の接頭辞

Returns:
    CoordinateCollection: グリッド補間結果を含むコレクション"""
        ...
    

    def spatial_interpolation_to_points(
        self,
        target_coords: list[dict[str, Any]],
        is_3d: bool,
        method: str,
        power: float
    ) -> List[list[float]]:
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
    CoordinateCollection: 補間結果を含むコレクション"""
        ...
    

    def interp_point(
        self,
        x: float,
        y: float,
        z: Optional[float],
        method: str,
        power: float
    ) -> "CollectionListOperations[C]":
        """interpolate_at_point のエイリアス"""
        ...
    

    def interp_grid(
        self,
        x_grid: ndarray,
        y_grid: ndarray,
        method: str,
        power: float
    ) -> List[ndarray]:
        """interpolate_grid のエイリアス"""
        ...
    

    def calculate_rosette_strains(
        self,
        e2: ndarray,
        e3: ndarray,
        r_type: str = 'rectangular',
        angle_offset: float = 0.0
    ) -> List[tuple[ndarray, ndarray, ndarray, ndarray]]:
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
        area: float
    ) -> List[ndarray]:
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
        strain: ndarray,
        lateral_strain: Optional[ndarray] = None,
        elastic_range: tuple[float, float] = (0.0005, 0.0025),
        offset: float = 0.002
    ) -> List[tuple[float, float, float, float]]:
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
    Tuple: E, yield_strain, yield_stress, nu"""
        ...
    

    def calculate_slopes(
        self,
        load_data: ndarray
    ) -> List[ndarray]:
        """変位と荷重の間の点ごとの傾きを計算します。

Args:
    disp_data: 変位データの配列
    load_data: 荷重データの配列
    
Returns:
    np.ndarray: 計算された傾きの配列（最初の要素は NaN）"""
        ...
    

    def calculate_stiffness(
        self,
        load_data: ndarray,
        range_start: float = 0.2,
        range_end: float = 0.8,
        method: str = 'linear_regression'
    ) -> List[float]:
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
        load_data: ndarray,
        method: str = 'offset',
        offset_value: float = 0.002,
        range_start: float = 0.1,
        range_end: float = 0.3,
        factor: float = 0.33,
        debug_mode: bool = False,
        fail_silently: bool = False
    ) -> List[tuple[bool, float, float, dict[str, Any]]]:
        """"""
        ...
    

    def create_skeleton_curve(
        self,
        displacements: ndarray,
        markers: ndarray,
        has_decrease: bool = False,
        decrease_type: str = 'envelope',
        *args,
        **kwargs
    ) -> List[tuple[list[float], list[float]]]:
        """荷重-変位データからスケルトン曲線を計算します。

Args:
    loads: 荷重データ
    displacements: 変位データ
    markers: サイクルマーカー
    has_decrease: 減少部分も含めるか
    decrease_type: 減少部分の処理方法 ('envelope', 'continuous_only', 'both')
    
Returns:
    Tuple[List[float], List[float]]: スケルトン曲線の(変位, 荷重)リスト"""
        ...
    

    def create_cumulative_curve(
        self,
        displacements: ndarray,
        markers: ndarray,
        *args,
        **kwargs
    ) -> List[tuple[list[float], list[float]]]:
        """荷重-変位データから累積曲線を計算します。

Args:
    loads: 荷重データ
    displacements: 変位データ
    markers: サイクルマーカー
    
Returns:
    Tuple[List[float], List[float]]: 累積曲線の(変位, 荷重)リスト"""
        ...
    

    def cycle_count(
        self,
        step: float = 0.5
    ) -> List[ndarray]:
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
        disps: ndarray,
        markers: ndarray,
        *args,
        **kwargs
    ) -> List[tuple[float, float, float, float, float, float]]:
        """1サイクルのヒステリシス解析結果と各種統計情報をまとめて計算します。

Args:
    loads: 荷重データ配列
    disps: 変位データ配列
    markers: サイクルマーカーの配列。先頭要素をサイクル番号として抽出します。
    
Returns:
    Tuple: (サイクル番号, エネルギー, 最大荷重, 最小荷重, 最大変位, 最小変位)"""
        ...
    

    def analyze_stiffness_degradation(
        self,
        disps: ndarray,
        markers: ndarray,
        *args,
        **kwargs
    ) -> List[tuple[float, float]]:
        """1サイクルの剛性推移（割線剛性）を計算します。

Args:
    loads: 荷重データ配列
    disps: 変位データ配列
    markers: サイクルマーカーの配列。先頭要素をサイクル番号として抽出します。
    
Returns:
    Tuple: (サイクル番号, 割線剛性)"""
        ...
    

    def find_peaks_and_valleys(
        self,
        distance: int = 1,
        threshold: Optional[float] = None
    ) -> List[ndarray]:
        """配列内の極大値(1)と極小値(-1)を検出します。

Args:
    data: 対象データ配列
    distance: ピーク間の最小距離（インデックス数）
    threshold: 隣接点との最小差
    
Returns:
    np.ndarray: ピーク(1)、バレー(-1)、その他(0)のフラグ配列"""
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
    
