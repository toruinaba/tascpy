# 自動生成されたリストプロキシスタブ - 編集しないでください
from __future__ import annotations
from typing import Optional, Union, List, Dict, Any, Callable, TypeVar, Iterable, Generic, overload, Literal
from tascpy.core.collection import ColumnCollection
from .proxy_base import CollectionOperationsBase
from tascpy.domains.core import ColumnCollection
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
    ) -> Union[CollectionListOperations[C], List[Any]]:
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
    ) -> CollectionListOperations[C]:
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
    def as_domain(self, domain: Literal['core'], **kwargs: Any) -> CollectionListOperations[ColumnCollection]:
        ...

    @overload
    def as_domain(self, domain: Literal['strain'], **kwargs: Any) -> CollectionListOperations[StrainCollection]:
        ...

    @overload
    def as_domain(self, domain: Literal['load_displacement'], **kwargs: Any) -> CollectionListOperations[LoadDisplacementCollection]:
        ...

    @overload
    def as_domain(self, domain: Literal['coordinate'], **kwargs: Any) -> CollectionListOperations[CoordinateCollection]:
        ...

    def as_domain(self, domain: str, **kwargs: Any) -> CollectionListOperations:
        """全てのコレクションを指定されたドメインに変換します
        
        Args:
            domain: 変換先のドメイン名
            **kwargs: 変換に渡す追加引数。ドメインごとに以下の引数が利用可能です。
                - strain: rosettes (Dict), rosette_metadata_key (str)
                - load_displacement: load_column (str), displacement_column (str)
                - coordinate: coordinates (Dict), coordinate_metadata_key (str)
                - timeseries: start_date (str/datetime), frequency (str)
                - signal: sample_rate (float)
            
        Returns:
            変換されたコレクションリスト
        """
        ...

    def filter_by_value(
        self,
        value: Any,
        tolerance: Optional[float] = None
    ) -> List[ndarray]:
        """指定した列の値が条件に一致する行のみを抽出します。

Args:
    collection (ColumnCollection): データコレクション
    column (str): 条件判定の対象となるカラム名
    value (Any): 一致するか比較する値
    tolerance (float, optional): 数値比較時の許容誤差. Defaults to None.
    
Returns:
    ColumnCollection: 条件に一致した行のみを含む新しいコレクション
    
Examples:
    >>> filtered_col = col.ops.filter_by_value("状態", "正常")
    >>> filtered_col = col.ops.filter_by_value("荷重", 100.0, tolerance=0.5)"""
        ...
    

    def filter_out_none(
        self,
        mode: str = 'any'
    ) -> List[list[bool]]:
        """一つでも欠損値（None/NaN）が含まれる行、または全て欠損値の行を除外します。

Args:
    collection (ColumnCollection): データコレクション
    columns (List[str], optional): 判定対象のカラム名リスト. 未指定時はすべて. Defaults to None.
    mode (str, optional): 判定モード ("any": いずれかが欠損なら除外, "all": 全てが欠損なら除外). Defaults to "any".
    
Returns:
    ColumnCollection: 欠損値を含む行が除外された新しいコレクション
    
Examples:
    >>> clean_col = col.ops.filter_out_none() # どこかに欠損があればその行を削除"""
        ...
    

    def remove_consecutive_duplicates_across(
        self,
        mode: str = 'consecutive',
        dup_type: str = 'all'
    ) -> List[list[int]]:
        """連続する重複行を検知し、最初の行だけを残して除外します。

Args:
    collection (ColumnCollection): データコレクション
    columns (List[str], optional): 重複判定の対象となるカラム名リスト. 未指定時はすべて. Defaults to None.
    mode (str, optional): 重複判定モード. Defaults to "consecutive".
    dup_type (str, optional): どの重複を残すか. Defaults to "all".
    
Returns:
    ColumnCollection: 連続重複が排除された新しいコレクション
    
Examples:
    >>> # 値が変化しない静止状態のデータを間引く場合などに有用
    >>> thinned_col = col.ops.remove_consecutive_duplicates_across()"""
        ...
    

    def remove_outliers(
        self,
        *args,
        **kwargs
    ) -> List[Any]:
        """特定の基準（外れ値検知ロジック）に基づいて外れ値と判定された行を除外します。

Args:
    collection (ColumnCollection): データコレクション
    column (str): 外れ値判定の対象となるカラム名
    window_size (int, optional): 移動窓のサイズ. Defaults to 3.
    threshold (float, optional): 外れ値と判定する閾値. Defaults to 0.5.
    edge_handling (str, optional): 端の処理手法. Defaults to "asymmetric".
    min_abs_value (float, optional): 最小絶対値. Defaults to 1e-10.
    scale_factor (float, optional): スケールファクター. Defaults to 1.0.

Returns:
    ColumnCollection: 外れ値が除外された新しいコレクション
    
Examples:
    >>> clean_col = col.ops.remove_outliers("変位", threshold=0.3)"""
        ...
    

    def filter_by_condition(
        self,
        condition: <built-in function callable>
    ) -> CollectionListOperations[C]:
        """コールバック関数を使って、指定カラムの値に対するカスタム条件で行を抽出します。

Args:
    collection (ColumnCollection): データコレクション
    column (str): 条件判定の対象となるカラム名
    condition (Callable[[np.ndarray], np.ndarray]): 真偽値配列を返す条件関数
    
Returns:
    ColumnCollection: 条件関数がTrueを返した行のみを含む新しいコレクション
    
Examples:
    >>> # 荷重が50以上の行だけを抽出
    >>> high_load_col = col.ops.filter_by_condition("荷重", lambda x: x >= 50)"""
        ...
    

    def remove_steps(
        self,
        steps: list[Any],
        tolerance: Optional[float] = None
    ) -> List[list[bool]]:
        """指定されたステップ値のリストに一致する行を除外します。

Args:
    collection (ColumnCollection): データコレクション
    steps (List[float] | np.ndarray): 除外したいステップ値のリスト
    
Returns:
    ColumnCollection: 指定したステップが除外された新しいコレクション
    
Examples:
    >>> filtered_col = col.ops.remove_steps(steps=[1.0, 2.0, 3.0])"""
        ...
    

    def select(
        self,
        columns: Optional[list[str]] = None,
        indices: Optional[list[int]] = None,
        steps: Optional[list[Union[int, float]]] = None,
        by_step_value: bool = True,
        tolerance: Optional[float] = None
    ) -> List[tuple[list[int], dict[str, Any]]]:
        """条件（行や列）に基づいてデータを抽出し、新しいコレクションを作成します。

Args:
    collection (ColumnCollection): データコレクション
    columns (str | List[str], optional): 抽出するカラム名. Defaults to None (全カラム).
    start (int, optional): 抽出開始インデックス. Defaults to None.
    end (int, optional): 抽出終了インデックス. Defaults to None.
    step_min (float, optional): 最小ステップ値. Defaults to None.
    step_max (float, optional): 最大ステップ値. Defaults to None.
    
Returns:
    ColumnCollection: 条件に一致するデータのみを含む新しいコレクション
    
Examples:
    >>> new_col = col.ops.select(columns=["荷重", "変位"])
    >>> sliced_col = col.ops.select(step_min=0.0, step_max=10.0)"""
        ...
    

    def fetch_near_step(
        self,
        value: float
    ) -> CollectionListOperations[C]:
        """指定ステップ値に最も近いデータ行を一つ抽出します。

Args:
    collection (ColumnCollection): データコレクション
    target_step (float): 抽出したい基準ステップ値
    
Returns:
    ColumnCollection: ターゲットに最も近い1行のみを含む新しいコレクション（要素数1）
    
Examples:
    >>> single_row = col.ops.fetch_near_step(5.0)
    >>> print(single_row.step.values[0])"""
        ...
    

    def split_by_integers(
        self,
        markers: Union[list[int], ndarray]
    ) -> CollectionListOperations[C]:
        """整数マーカーに基づいてコレクションを分割します。

ユニークなマーカー値ごとに、そのマーカーに対応するデータを含む
新しい ColumnCollection のリストを返します。

Args:
    collection: 対象の ColumnCollection
    markers: 各要素に対応する整数マーカーのリストまたは配列。長さはコレクションの長さと一致する必要があります。

Returns:
    List[ColumnCollection]: 分割されたコレクションのリスト
    
Examples:
    >>> cycles = col.ops.split_by_integers(markers=[1, 1, 2, 2, 3])"""
        ...
    

    def split_at_indices(
        self,
        indices: Union[int, list[int]]
    ) -> CollectionListOperations[C]:
        """指定されたインデックスでコレクションを分割します。

Args:
    collection: 対象の ColumnCollection
    indices: 分割点となるインデックス（またはそのリスト）

Returns:
    List[ColumnCollection]: 分割されたコレクションのリスト
    
Examples:
    >>> partial_cols = col.ops.split_at_indices([100, 200])"""
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
        """特定のステップ値（またはインデックス）を境にして、2つのデータ列を切り替えます

Args:
    collection (ColumnCollection): データコレクション
    v1 (str | np.ndarray): 切り替え前のデータ（カラム名または配列）
    v2 (str | np.ndarray): 切り替え後のデータ（カラム名または配列）
    threshold (int | float): 切り替えを実行する境界となるステップ値（またはインデックス）
    compare_mode (str, optional): 比較モード ("value", "index"). Defaults to "value".
    by_step_value (bool, optional): 基準軸としてステップ値を使うか. Defaults to True.
    tolerance (float, optional): 比較の許容誤差. Defaults to None.
    
Returns:
    ColumnCollection: 切り替え済みのデータを持つ新しいコレクション
    
Examples:
    >>> switched_col = col.ops.switch_by_step("Phase1", "Phase2", threshold=5.0)"""
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
        """特定のステップ区間において、2つのデータ列を滑らかにブレンド（合成）します

Args:
    collection (ColumnCollection): データコレクション
    v1 (str | np.ndarray): ブレンド前のデータ（始端側）
    v2 (str | np.ndarray): ブレンド後のデータ（終端側）
    start (int | float): ブレンドを開始するステップ値（またはインデックス）
    end (int | float): ブレンドを終了しv2に完全に以降するステップ値（またはインデックス）
    compare_mode (str, optional): 比較モード ("value", "index"). Defaults to "value".
    by_step_value (bool, optional): 基準軸としてステップ値を使うか. Defaults to True.
    blend_method (str, optional): ブレンド手法 ("linear", "cosine", "smoothstep"). Defaults to "linear".
    tolerance (float, optional): 比較の許容誤差. Defaults to None.

Returns:
    ColumnCollection: ブレンド済みのデータを持つ新しいコレクション
    
Examples:
    >>> blended_col = col.ops.blend_by_step("Phase1", "Phase2", start=4.0, end=6.0, blend_method="smoothstep")"""
        ...
    

    def sum_columns(
        self,
        columns = None
    ) -> List[Any]:
        """指定された複数のカラムの要素ごとの合計を計算します

Args:
    collection (ColumnCollection): データコレクション
    columns (List[str], optional): 合計するカラム名のリスト. 未指定時はすべて. Defaults to None.
    
Returns:
    ColumnCollection: 合計値カラムが追加された新しいコレクション
    
Examples:
    >>> sum_col = col.ops.sum_columns(columns=["CH1", "CH2", "CH3"])"""
        ...
    

    def average_columns(
        self,
        columns = None
    ) -> List[Any]:
        """指定された複数のカラムの要素ごとの平均を計算します

Args:
    collection (ColumnCollection): データコレクション
    columns (List[str], optional): 平均するカラム名のリスト. 未指定時はすべて. Defaults to None.
    
Returns:
    ColumnCollection: 平均値カラムが追加された新しいコレクション
    
Examples:
    >>> avg_col = col.ops.average_columns(columns=["CH1", "CH2", "CH3"])"""
        ...
    

    def conditional_select(
        self,
        v2: ndarray,
        cond_values: ndarray,
        threshold: Union[int, float] = 0,
        compare: str = '>'
    ) -> List[ndarray]:
        """条件列の値と閾値の比較結果に基づき、2つの列から値を選択します

Args:
    collection (ColumnCollection): データコレクション
    v1 (str | np.ndarray): 条件付き真(True)の時に選ばれるデータ
    v2 (str | np.ndarray): 条件付き偽(False)の時に選ばれるデータ
    cond_values (str | np.ndarray): 条件判定の基準となるデータ列
    threshold (int | float, optional): 条件判定の閾値. Defaults to 0.
    compare (str, optional): 比較演算子 (">", "<", ">=", "<=", "==", "!="). Defaults to ">".
    
Returns:
    ColumnCollection: 条件に基づいて選択されたデータを持つ新しいコレクション
    
Examples:
    >>> selected_col = col.ops.conditional_select("CH_High", "CH_Low", cond_values="Temperature", threshold=50, compare=">")"""
        ...
    

    def custom_combine(
        self,
        v2: Any,
        combine_func: Callable[[Any, Any], Any],
        **kwargs
    ) -> CollectionListOperations[C]:
        """ユーザー提供のカスタム関数を利用して2つの列を合成します

Args:
    collection (ColumnCollection): データコレクション
    v1 (str | np.ndarray): 第一引数となるデータ列
    v2 (str | np.ndarray): 第二引数となるデータ列
    combine_func (Callable[[Any, Any], Any]): 合成処理を行うコールバック関数
    func_name (str, optional): 関数の名前（結果のカラム名に使用）. Defaults to None.
    
Returns:
    ColumnCollection: カスタム加工されたデータを含む新しいコレクション
    
Examples:
    >>> custom_col = col.ops.custom_combine("CH1", "CH2", combine_func=lambda x, y: x**2 + y**2, func_name="sum_squares")"""
        ...
    

    def add(
        self,
        value1: Union[str, float, ndarray],
        value2: Union[str, float, ndarray],
        result_column: Optional[str] = None,
        unit: Optional[str] = None,
        ch: Optional[str] = None,
        in_place: bool = False
    ) -> CollectionListOperations[C]:
        """複数カラムまたはスカラー値の要素ごとの和を計算します。

Args:
    collection (ColumnCollection): データコレクション
    value1 (Union[str, float, np.ndarray]): 第1引数（カラム名または数値）
    value2 (Union[str, float, np.ndarray]): 第2引数（カラム名または数値）
    result_column (str, optional): 結果を格納するカラム名。指定しない場合は自動生成。
    unit (str, optional): 結果の単位。
    ch (str, optional): 結果のチャネル名。
    in_place (bool, optional): 元のコレクションを上書きするかどうか。デフォルトはFalse。

Returns:
    ColumnCollection: 計算結果カラムが追加された新しいコレクション

Examples:
    >>> col = col.ops.add("CH01", "CH02")
    >>> col = col.ops.add("CH01", 10.5)"""
        ...
    

    def subtract(
        self,
        value1: Union[str, float, ndarray],
        value2: Union[str, float, ndarray],
        result_column: Optional[str] = None,
        unit: Optional[str] = None,
        ch: Optional[str] = None,
        in_place: bool = False
    ) -> CollectionListOperations[C]:
        """第一引数から第二引数の要素ごとの差を計算します。

Args:
    collection (ColumnCollection): データコレクション
    value1 (Union[str, float, np.ndarray]): 第1引数（カラム名または数値）
    value2 (Union[str, float, np.ndarray]): 第2引数（引き算するカラム名または数値）
    result_column (str, optional): 結果を格納するカラム名。指定しない場合は自動生成。
    unit (str, optional): 結果の単位。
    ch (str, optional): 結果のチャネル名。
    in_place (bool, optional): 元のコレクションを上書きするかどうか。デフォルトはFalse。

Returns:
    ColumnCollection: 計算結果カラムが追加された新しいコレクション

Examples:
    >>> col = col.ops.subtract("CH01", "CH02")
    >>> col = col.ops.subtract("CH01", 10.5)"""
        ...
    

    def multiply(
        self,
        value1: Union[str, float, ndarray],
        value2: Union[str, float, ndarray],
        result_column: Optional[str] = None,
        unit: Optional[str] = None,
        ch: Optional[str] = None,
        in_place: bool = False
    ) -> CollectionListOperations[C]:
        """複数カラムまたはスカラー値の要素ごとの積を計算します。

Args:
    collection (ColumnCollection): データコレクション
    value1 (Union[str, float, np.ndarray]): 第1引数（カラム名または数値）
    value2 (Union[str, float, np.ndarray]): 第2引数（カラム名または数値）
    result_column (str, optional): 結果を格納するカラム名。指定しない場合は自動生成。
    unit (str, optional): 結果の単位。
    ch (str, optional): 結果のチャネル名。
    in_place (bool, optional): 元のコレクションを上書きするかどうか。デフォルトはFalse。

Returns:
    ColumnCollection: 計算結果カラムが追加された新しいコレクション

Examples:
    >>> col = col.ops.multiply("CH01", 2.0)"""
        ...
    

    def divide(
        self,
        value1: Union[str, float, ndarray],
        value2: Union[str, float, ndarray],
        result_column: Optional[str] = None,
        unit: Optional[str] = None,
        ch: Optional[str] = None,
        in_place: bool = False
    ) -> CollectionListOperations[C]:
        """第一引数を第二引数で要素ごとに除算します。

Args:
    collection (ColumnCollection): データコレクション
    value1 (Union[str, float, np.ndarray]): 分子（カラム名または数値）
    value2 (Union[str, float, np.ndarray]): 分母（カラム名または数値）
    result_column (str, optional): 結果を格納するカラム名。指定しない場合は自動生成。
    unit (str, optional): 結果の単位。
    ch (str, optional): 結果のチャネル名。
    in_place (bool, optional): 元のコレクションを上書きするかどうか。デフォルトはFalse。

Returns:
    ColumnCollection: 計算結果カラムが追加された新しいコレクション

Examples:
    >>> col = col.ops.divide("荷重", 1000)"""
        ...
    

    def diff(
        self,
        y_column: Union[str, ndarray],
        x_column: Union[str, ndarray],
        method: str = 'central',
        result_column: Optional[str] = None,
        unit: Optional[str] = None,
        ch: Optional[str] = None,
        in_place: bool = False
    ) -> CollectionListOperations[C]:
        """データ系列の離散微分 (dy/dx) を計算します。

Args:
    collection (ColumnCollection): データコレクション
    y_column (Union[str, np.ndarray]): Y軸データとなるカラム名
    x_column (Union[str, np.ndarray]): X軸データとなるカラム名
    method (str, optional): 微分手法 ("forward", "backward", "central"). Defaults to "central".
    result_column (str, optional): 結果を格納するカラム名。指定しない場合は自動生成。
    unit (str, optional): 結果の単位。
    ch (str, optional): 結果のチャネル名。
    in_place (bool, optional): 元のコレクションを上書きするかどうか。デフォルトはFalse。

Returns:
    ColumnCollection: 微分値カラムが追加された新しいコレクション

Examples:
    >>> result = col.ops.diff("変位", "__step__", method="central")"""
        ...
    

    def integrate(
        self,
        y_column: Union[str, ndarray],
        x_column: Union[str, ndarray],
        method: str = 'trapezoid',
        initial_value: float = 0.0,
        result_column: Optional[str] = None,
        unit: Optional[str] = None,
        ch: Optional[str] = None,
        in_place: bool = False
    ) -> CollectionListOperations[C]:
        """データ系列の離散積分 (∫y dx) を計算します。

Args:
    collection (ColumnCollection): データコレクション
    y_column (Union[str, np.ndarray]): Y軸データとなるカラム名
    x_column (Union[str, np.ndarray]): X軸データとなるカラム名
    method (str, optional): 積分手法 ("trapezoid", "cumulative_sum"). Defaults to "trapezoid".
    initial_value (float, optional): 積分定数 (初期値). Defaults to 0.0.
    result_column (str, optional): 結果を格納するカラム名。指定しない場合は自動生成。
    unit (str, optional): 結果の単位。
    ch (str, optional): 結果のチャネル名。
    in_place (bool, optional): 元のコレクションを上書きするかどうか。デフォルトはFalse。

Returns:
    ColumnCollection: 積分値カラムが追加された新しいコレクション

Examples:
    >>> result = col.ops.integrate("速度", "__step__")"""
        ...
    

    def evaluate(
        self,
        expression: str,
        result_column: Optional[str] = None,
        unit: Optional[str] = None,
        ch: Optional[str] = None,
        in_place: bool = False
    ) -> CollectionListOperations[C]:
        """与えられた数式文字列を評価し、新しいカラムを生成します。

Args:
    collection (ColumnCollection): データコレクション
    expression (str): 評価する数式文字列（例: "CH01 * 2 + CH02"）
    result_column (str, optional): 結果を格納するカラム名。指定しない場合は自動生成。
    unit (str, optional): 結果の単位。
    ch (str, optional): 結果のチャネル名。
    in_place (bool, optional): 元のコレクションを上書きするかどうか。デフォルトはFalse。

Returns:
    ColumnCollection: 計算結果カラムが追加された新しいコレクション

Examples:
    >>> result = col.ops.evaluate("荷重 * 2.0 + 10.0")"""
        ...
    

    def log(
        self,
        values: Union[str, ndarray],
        base: float = 2.718281828459045,
        result_column: Optional[str] = None,
        unit: Optional[str] = None,
        ch: Optional[str] = None,
        in_place: bool = False
    ) -> CollectionListOperations[C]:
        """指定されたカラムの対数を計算します。

Args:
    collection (ColumnCollection): データコレクション
    values (Union[str, np.ndarray]): 対象のカラム名または数値配列
    base (float, optional): 対数の底. Defaults to e.
    result_column (str, optional): 結果を格納するカラム名。指定しない場合は自動生成。
    unit (str, optional): 結果の単位。
    ch (str, optional): 結果のチャネル名。
    in_place (bool, optional): 元のコレクションを上書きするかどうか。デフォルトはFalse。

Returns:
    ColumnCollection: 計算結果カラムが追加されたコレクション

Examples:
    >>> result = col.ops.log("CH1", base=10.0)"""
        ...
    

    def sqrt(
        self,
        values: Union[str, ndarray],
        result_column: Optional[str] = None,
        unit: Optional[str] = None,
        ch: Optional[str] = None,
        in_place: bool = False
    ) -> CollectionListOperations[C]:
        """指定されたカラムの平方根を計算します。

Args:
    collection (ColumnCollection): データコレクション
    values (Union[str, np.ndarray]): 対象のカラム名または数値配列
    result_column (str, optional): 結果を格納するカラム名。指定しない場合は自動生成。
    unit (str, optional): 結果の単位。
    ch (str, optional): 結果のチャネル名。
    in_place (bool, optional): 元のコレクションを上書きするかどうか。デフォルトはFalse。

Returns:
    ColumnCollection: 計算結果カラムが追加されたコレクション

Examples:
    >>> result = col.ops.sqrt("CH1")"""
        ...
    

    def pow(
        self,
        values: Union[str, ndarray],
        exponent: float = 1.0,
        result_column: Optional[str] = None,
        unit: Optional[str] = None,
        ch: Optional[str] = None,
        in_place: bool = False
    ) -> CollectionListOperations[C]:
        """指定されたカラムのべき乗を計算します。

Args:
    collection (ColumnCollection): データコレクション
    values (Union[str, np.ndarray]): 対象のカラム名または数値配列
    exponent (float, optional): 指数. Defaults to 1.0.
    result_column (str, optional): 結果を格納するカラム名。指定しない場合は自動生成。
    unit (str, optional): 結果の単位。
    ch (str, optional): 結果のチャネル名。
    in_place (bool, optional): 元のコレクションを上書きするかどうか。デフォルトはFalse。

Returns:
    ColumnCollection: 計算結果カラムが追加されたコレクション

Examples:
    >>> result = col.ops.pow("CH1", exponent=2.0)"""
        ...
    

    def abs_values(
        self,
        values: Union[str, ndarray],
        result_column: Optional[str] = None,
        unit: Optional[str] = None,
        ch: Optional[str] = None,
        in_place: bool = False
    ) -> CollectionListOperations[C]:
        """指定されたカラムの絶対値を計算します。

Args:
    collection (ColumnCollection): データコレクション
    values (Union[str, np.ndarray]): 対象のカラム名または数値配列
    result_column (str, optional): 結果を格納するカラム名。指定しない場合は自動生成。
    unit (str, optional): 結果の単位。
    ch (str, optional): 結果のチャネル名。
    in_place (bool, optional): 元のコレクションを上書きするかどうか。デフォルトはFalse。

Returns:
    ColumnCollection: 計算結果カラムが追加されたコレクション

Examples:
    >>> result = col.ops.abs_values("変位")"""
        ...
    

    def round_values(
        self,
        values: Union[str, ndarray],
        decimals: int = 0,
        result_column: Optional[str] = None,
        unit: Optional[str] = None,
        ch: Optional[str] = None,
        in_place: bool = False
    ) -> CollectionListOperations[C]:
        """指定されたカラムの値を丸めます（四捨五入）。

Args:
    collection (ColumnCollection): データコレクション
    values (Union[str, np.ndarray]): 対象のカラム名または数値配列
    decimals (int, optional): 丸める小数点以下の桁数. Defaults to 0.
    result_column (str, optional): 結果を格納するカラム名。指定しない場合は自動生成。
    unit (str, optional): 結果の単位。
    ch (str, optional): 結果のチャネル名。
    in_place (bool, optional): 元のコレクションを上書きするかどうか。デフォルトはFalse。

Returns:
    ColumnCollection: 計算結果カラムが追加されたコレクション

Examples:
    >>> result = col.ops.round_values("荷重", decimals=2)"""
        ...
    

    def normalize(
        self,
        values: Union[str, ndarray],
        method: str = 'minmax',
        result_column: Optional[str] = None,
        unit: Optional[str] = None,
        ch: Optional[str] = None,
        in_place: bool = False
    ) -> CollectionListOperations[C]:
        """指定されたカラムの値を正規化します。

Args:
    collection (ColumnCollection): データコレクション
    values (Union[str, np.ndarray]): 対象のカラム名または数値配列
    method (str, optional): 正規化手法 ("minmax", "zscore", "max_abs"). Defaults to "minmax".
    result_column (str, optional): 結果を格納するカラム名。指定しない場合は自動生成。
    unit (str, optional): 結果の単位。
    ch (str, optional): 結果のチャネル名。
    in_place (bool, optional): 元のコレクションを上書きするかどうか。デフォルトはFalse。

Returns:
    ColumnCollection: 計算結果カラムが追加されたコレクション

Examples:
    >>> result = col.ops.normalize("荷重", method="minmax")"""
        ...
    

    def average_across(
        self,
        *columns: str,
        ignore_nan: bool = True,
        result_column: Optional[str] = None,
        unit: Optional[str] = None,
        ch: Optional[str] = None,
        in_place: bool = False
    ) -> CollectionListOperations[C]:
        """複数カラムの値を行ごとに平均し、新しいカラムとして追加します。

Args:
    collection (ColumnCollection): データコレクション
    *columns (str): 平均を計算対象とする複数列のカラム名
    ignore_nan (bool, optional): 欠損値（NaN）を無視するかどうか。デフォルトはTrue。
    result_column (str, optional): 結果を格納するカラム名。指定しない場合は自動生成。
    unit (str, optional): 結果の単位。
    ch (str, optional): 結果のチャネル名。
    in_place (bool, optional): 元のコレクションを上書きするかどうか。デフォルトはFalse。

Returns:
    ColumnCollection: 計算結果カラムが追加されたコレクション

Examples:
    >>> result = col.ops.average_across("センサ1", "センサ2", "センサ3", result_column="平均値")"""
        ...
    

    def moving_average(
        self,
        window_size: int = 3,
        edge_handling = 'asymmetric'
    ) -> CollectionListOperations[C]:
        """指定されたウィンドウサイズで移動平均を計算します

Args:
    collection (ColumnCollection): データコレクション
    column_name (str): 計算対象のカラム名
    window_size (int, optional): 移動平均のウィンドウサイズ. Defaults to 3.
    edge_handling (str, optional): 端の処理方法 ("asymmetric", "symmetric", "constant", "mirror", "wrap"). Defaults to "asymmetric".
    
Returns:
    ColumnCollection: 移動平均値が追加された新しいコレクション
    
Examples:
    >>> smoothed_col = col.ops.moving_average("荷重", window_size=5)"""
        ...
    

    def detect_outliers(
        self,
        window_size: int = 3,
        threshold: float = 0.5,
        edge_handling: str = 'asymmetric',
        min_abs_value: float = 1e-10,
        scale_factor: float = 1.0
    ) -> List[list[int]]:
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
    ColumnCollection: 異常値フラグが追加された新しいコレクション
    
Examples:
    >>> flagged_col = col.ops.detect_outliers("変位", threshold=3.0)"""
        ...
    

    def gaussian_filter(
        self,
        sigma: float = 1.0,
        window_size: Optional[int] = None
    ) -> List[Any]:
        """ガウシアンフィルターを適用します

Args:
    collection (ColumnCollection): データコレクション
    column_name (str): 計算対象のカラム名
    sigma (float, optional): ガウス関数の標準偏差. Defaults to 1.0.
    window_size (Optional[int], optional): ウィンドウサイズ. Defaults to None.
    
Returns:
    ColumnCollection: フィルター処理後の値が追加された新しいコレクション
    
Examples:
    >>> filtered_col = col.ops.gaussian_filter("荷重", sigma=2.0)"""
        ...
    

    def interpolate_at_point(
        self,
        x: float,
        y: float,
        z: Optional[float],
        method: str,
        power: float
    ) -> CollectionListOperations[C]:
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
    
Examples:
    >>> interp_col = col.ops.interpolate_at_point(
    ...     x=10.0, y=20.0, method="inverse_distance"
    ... )"""
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
    CoordinateCollection: グリッド補間結果を含むコレクション
    
Examples:
    >>> grid_col = col.ops.interpolate_grid(x_range=(0, 100), y_range=(0, 100), grid_size=(20, 20), target_column="Temperature")"""
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
    CoordinateCollection: 補間結果を含むコレクション
    
Examples:
    >>> mapped_col = col.ops.spatial_interpolation_to_points(
    ...     source_columns=["Sensor1", "Sensor2"],
    ...     target_columns=["NodeA", "NodeB"],
    ...     method="inverse_distance"
    ... )"""
        ...
    

    def interp_point(
        self,
        x: float,
        y: float,
        z: Optional[float],
        method: str,
        power: float
    ) -> CollectionListOperations[C]:
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
    StrainCollection: 計算結果（e_max, e_min, gamma_max, theta）が追加されたコレクション
    
Examples:
    >>> # カラム名指定で直交ロゼットを計算
    >>> col = col.ops.calculate_rosette_strains(
    ...     columns=["CH1", "CH2", "CH3"], rosette_type="rectangular"
    ... )"""
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
    StrainCollection: 応力カラムが追加されたコレクション
    
Examples:
    >>> col = col.ops.calculate_stress(load_column="荷重", area=10.0, result_column="応力")"""
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
        """find_yield_point のエイリアス"""
        ...
    

    def calculate_slopes(
        self,
        load_data: ndarray
    ) -> List[ndarray]:
        """荷重-変位データから区間ごとの傾き（スロープ）を計算します。

Args:
    collection (LoadDisplacementCollection): 荷重-変位コレクション
    disp_data (str, optional): 変位データのカラム名（None時は自動解決）
    load_data (str, optional): 荷重データのカラム名（None時は自動解決）
    
Returns:
    LoadDisplacementCollection: 算出された傾きデータが追加された新しいコレクション
    
Examples:
    >>> col = col.ops.calculate_slopes()"""
        ...
    

    def calculate_stiffness(
        self,
        load_data: ndarray,
        range_start: float = 0.2,
        range_end: float = 0.8,
        method: str = 'linear_regression'
    ) -> List[float]:
        """calculate_stiffness のエイリアス"""
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
        """荷重-変位データからスケルトン曲線（包絡線）を生成します。

Args:
    collection (LoadDisplacementCollection): 荷重-変位コレクション
    load_column (str, optional): 荷重データのカラム名（None時は自動解決）
    displacement_column (str, optional): 変位データのカラム名（None時は自動解決）
    cycle_marker_column (str, optional): サイクルマーカーカラム名（None時は自動解決）
    has_decrease (bool, optional): 剛性低下を考慮するかどうか. Defaults to False.
    decrease_type (str, optional): 剛性低下の計算手法. Defaults to "envelope".
    
Returns:
    LoadDisplacementCollection: スケルトン曲線データが結果として追加された新しいコレクション
    
Examples:
    >>> col = col.ops.create_skeleton_curve(has_decrease=True, decrease_type="envelope")"""
        ...
    

    def create_cumulative_curve(
        self,
        displacements: ndarray,
        markers: ndarray,
        *args,
        **kwargs
    ) -> List[tuple[list[float], list[float]]]:
        """荷重-変位データから累積塑性変形-荷重曲線を生成します。

Args:
    collection (LoadDisplacementCollection): 荷重-変位コレクション
    load_column (str, optional): 荷重データのカラム名（None時は自動解決）
    displacement_column (str, optional): 変位データのカラム名（None時は自動解決）
    cycle_marker_column (str, optional): サブサイクル判定用のマーカーカラム名
    
Returns:
    LoadDisplacementCollection: 累積曲線データが結果として追加された新しいコレクション
    
Examples:
    >>> col = col.ops.create_cumulative_curve()"""
        ...
    

    def cycle_count(
        self,
        step: float = 0.5
    ) -> List[ndarray]:
        """荷重データの符号反転に基づいてサイクルをカウントします。

Args:
    collection (LoadDisplacementCollection): 荷重-変位コレクション
    data (str, optional): 荷重データのカラム名（None時はメタデータから解決）
    step (float, optional): ノイズ除去のための変化判定ステップ幅. Defaults to 0.5.
    
Returns:
    LoadDisplacementCollection: サイクル番号が追加された新しいコレクション
    
Examples:
    >>> col = col.ops.cycle_count(step=1.0)"""
        ...
    

    def split_by_cycles(
        self,
        cycle_column: Optional[str] = None
    ) -> CollectionListOperations[C]:
        """サイクル番号ごとにデータを分割します。

データをサイクル番号ごとに分割し、各サイクルの
荷重-変位コレクションのリストを返します。

Args:
    collection: 荷重-変位コレクション
    cycle_column: サイクル番号を含む列名（指定がない場合は自動検出/生成）

Returns:
    List[LoadDisplacementCollection]: サイクルごとに分割されたコレクションのリスト
    
Examples:
    >>> cycle_list = col.ops.split_by_cycles()
    >>> first_cycle = cycle_list[0]"""
        ...
    

    def analyze_hysteresis(
        self,
        disps: ndarray,
        markers: ndarray,
        *args,
        **kwargs
    ) -> List[tuple[float, float, float, float, float, float]]:
        """各サイクルのヒステリシスエネルギー（面積）と最大/最小荷重・変位を計算します。

Args:
    collection (LoadDisplacementCollection): 荷重-変位コレクション
    cycle_column (str, optional): サイクル番号のカラム名（None時は自動解決）
    load_column (str, optional): 荷重データのカラム名（None時は自動解決）
    displacement_column (str, optional): 変位データのカラム名（None時は自動解決）
    cycle_marker_column (str, optional): サブサイクル判定用のマーカーカラム名
    
Returns:
    LoadDisplacementCollection: サイクルごとの統計量を持つ新しいコレクション
    
Examples:
    >>> stats_col = col.ops.analyze_hysteresis()
    >>> energy = stats_col["energy"].values"""
        ...
    

    def analyze_stiffness_degradation(
        self,
        disps: ndarray,
        markers: ndarray,
        *args,
        **kwargs
    ) -> List[tuple[float, float]]:
        """各サイクルの割線剛性（剛性低下）を評価します。

Args:
    collection (LoadDisplacementCollection): 荷重-変位コレクション
    cycle_column (str, optional): サイクル番号のカラム名（None時は自動解決）
    load_column (str, optional): 荷重データのカラム名（None時は自動解決）
    displacement_column (str, optional): 変位データのカラム名（None時は自動解決）
    cycle_marker_column (str, optional): サブサイクル判定用のマーカーカラム名
    
Returns:
    LoadDisplacementCollection: サイクルごとの割線剛性を持つ新しいコレクション
    
Examples:
    >>> stiffness_col = col.ops.analyze_stiffness_degradation()"""
        ...
    

    def find_peaks_and_valleys(
        self,
        distance: int = 1,
        threshold: Optional[float] = None
    ) -> List[ndarray]:
        """荷重データのピーク（極大値）とバレー（極小値）を検出します。

Args:
    collection (LoadDisplacementCollection): 荷重-変位コレクション
    data (str, optional): 荷重データのカラム名（None時は自動解決）
    distance (int, optional): 隣接するピーク間の最小距離. Defaults to 1.
    threshold (float, optional): ピークとして認識するための閾値
    prominence (float, optional): 周囲からの最低の突出度
    
Returns:
    LoadDisplacementCollection: ピーク（1）、バレー（-1）、その他（0）を示すマーカーカラムが追加された新しいコレクション
    
Examples:
    >>> col = col.ops.find_peaks_and_valleys(distance=10, prominence=0.5)"""
        ...
    
