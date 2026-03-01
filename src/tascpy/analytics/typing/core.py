# 自動生成されたcoreドメインのスタブファイル - 編集しないでください
from typing import Optional, Union, List, Dict, Any, Callable, TypeVar, cast, Generic, overload, Literal
from tascpy.core.collection import ColumnCollection
from .proxy_base import CollectionOperationsBase
from .list_proxy import CollectionListOperations

from .strain import StrainCollectionOperations
from .load_displacement import LoadDisplacementCollectionOperations
from .coordinate import CoordinateCollectionOperations

class CoreCollectionOperations(CollectionOperationsBase[ColumnCollection]):
    """coreドメインの操作メソッドスタブ定義
    
    このクラスはPylanceの型チェックとオートコンプリートのためのスタブです。
    実際の実行には使用されません。
    """

    def end(self) -> ColumnCollection:
        """操作チェーンを終了し、最終的なColumnCollectionを取得"""
        ...

    def debug(self, message: Optional[str] = None) -> "CoreCollectionOperations":
        """デバッグメッセージを表示
        
        Args:
            message: デバッグメッセージ
        
        Returns:
            CoreCollectionOperations: 自身を返す
        """
        ...


    def filter_by_value(
        self,
        values: column = <class 'str'>,
        tolerance: Optional[float] = None,
        column: column = <class 'str'>,
        value: Any,
        tolerance: Optional[float] = None
    ) -> ndarray:
        """指定した列の値が条件に一致する行のみを抽出します

Args:
    collection (ColumnCollection): データコレクション
    column (str): 条件判定の対象となるカラム名
    value (Any): 一致するか比較する値
    tolerance (float, optional): 数値比較時の許容誤差. Defaults to None.
    
Returns:
    ColumnCollection: 条件に一致した行のみを含む新しいコレクション"""
        ...
    

    def filter_out_none(
        self,
        mode: str = 'any',
        column: str,
        mode: str = 'any'
    ) -> list[bool]:
        """一つでも欠損値（None/NaN）が含まれる行、または全て欠損値の行を除外します

Args:
    collection (ColumnCollection): データコレクション
    columns (List[str], optional): 判定対象のカラム名リスト. 未指定時はすべて. Defaults to None.
    mode (str, optional): 判定モード ("any": いずれかが欠損なら除外, "all": 全てが欠損なら除外). Defaults to "any".
    
Returns:
    ColumnCollection: 欠損値を含む行が除外された新しいコレクション"""
        ...
    

    def remove_consecutive_duplicates_across(
        self,
        data: columns = typing.Optional[typing.List[str]],
        dup_type: str = 'all',
        column: columns = typing.Optional[typing.List[str]],
        mode: str = 'consecutive',
        dup_type: str = 'all'
    ) -> list[int]:
        """連続する重複行を検知し、最初の行だけを残して除外します

Args:
    collection (ColumnCollection): データコレクション
    columns (List[str], optional): 重複判定の対象となるカラム名リスト. 未指定時はすべて. Defaults to None.
    mode (str, optional): 重複判定モード. Defaults to "consecutive".
    dup_type (str, optional): どの重複を残すか. Defaults to "all".
    
Returns:
    ColumnCollection: 連続重複が排除された新しいコレクション"""
        ...
    

    def remove_outliers(
        self,
        column: str,
        *args,
        **kwargs
    ) -> Any:
        """特定の基準（外れ値検知ロジック）に基づいて外れ値と判定された行を除外します

Args:
    collection (ColumnCollection): データコレクション
    column (str): 外れ値判定の対象となるカラム名
    window_size (int, optional): 移動窓のサイズ. Defaults to 3.
    threshold (float, optional): 外れ値と判定する閾値. Defaults to 0.5.
    edge_handling (str, optional): 端の処理手法. Defaults to "asymmetric".
    min_abs_value (float, optional): 最小絶対値. Defaults to 1e-10.
    scale_factor (float, optional): スケールファクター. Defaults to 1.0.

Returns:
    ColumnCollection: 外れ値が除外された新しいコレクション"""
        ...
    

    def filter_by_condition(
        self,
        vals: column = <class 'str'>,
        column: column = <class 'str'>,
        condition: <built-in function callable>
    ) -> "CollectionListOperations[CoreCollectionOperations]":
        """コールバック関数を使って、指定カラムの値に対するカスタム条件で行を抽出します

Args:
    collection (ColumnCollection): データコレクション
    column (str): 条件判定の対象となるカラム名
    condition (Callable[[np.ndarray], np.ndarray]): 真偽値配列を返す条件関数
    
Returns:
    ColumnCollection: 条件関数がTrueを返した行のみを含む新しいコレクション"""
        ...
    

    def remove_steps(
        self,
        steps: list[Any],
        tolerance: Optional[float] = None
    ) -> list[bool]:
        """指定されたステップ値のリストに一致する行を除外します

Args:
    collection (ColumnCollection): データコレクション
    steps (List[float] | np.ndarray): 除外したいステップ値のリスト
    
Returns:
    ColumnCollection: 指定したステップが除外された新しいコレクション"""
        ...
    

    def search_by_value(
        self,
        values: values = typing.Any,
        column: values = typing.Any,
        op_str: str,
        value: Any
    ) -> list[int]:
        """指定された値に一致するデータのインデックスリストを返します（抽出は行いません）

Args:
    collection (ColumnCollection): データコレクション
    values (str | np.ndarray): 検索対象のカラム名または配列
    value (Any): 検索する値
    tolerance (float, optional): 許容誤差. Defaults to None.
    
Returns:
    np.ndarray: 一致したインデックスの配列"""
        ...
    

    def search_by_range(
        self,
        values: vals = typing.Any,
        column: vals = typing.Any,
        min_value: Any,
        max_value: Any,
        inclusive: bool = True
    ) -> list[int]:
        """指定したカラムの値が一定の範囲に収まるインデックスリストを返します

Args:
    collection (ColumnCollection): データコレクション
    vals (str | np.ndarray): 検索対象のカラム名または配列
    min (float, optional): 最小値. Defaults to None.
    max (float, optional): 最大値. Defaults to None.
    inclusive (bool, optional): 境界値を含むか. Defaults to True.
    
Returns:
    np.ndarray: 範囲内に収まるインデックスの配列"""
        ...
    

    def search_by_step_range(
        self,
        min: float,
        max: float,
        inclusive: bool = True,
        tolerance: Optional[float] = None,
        by_step_value: bool = True
    ) -> list[int]:
        """ステップ値が一定の範囲に収まるインデックスリストを返します

Args:
    collection (ColumnCollection): データコレクション
    min (float, optional): 最小ステップ値. Defaults to None.
    max (float, optional): 最大ステップ値. Defaults to None.
    inclusive (bool, optional): 境界値を含むか. Defaults to True.
    compare_mode (str, optional): 比較モード ("value", "index"). Defaults to "value".
    by_step_value (bool, optional): 基準軸としてステップ値を使うか. Defaults to True.
    
Returns:
    np.ndarray: 条件に一致したインデックスの配列"""
        ...
    

    def search_by_condition(
        self,
        data: columns = typing.Optional[typing.List[str]],
        column: columns = typing.Optional[typing.List[str]],
        condition_func: Callable[[Dict[str, Any]], bool]
    ) -> list[int]:
        """複数のカラムに対して、指定した条件関数を満たすインデックスリストを返します

Args:
    collection (ColumnCollection): データコレクション
    columns (List[str], optional): 検索対象のカラム名リスト. 未指定時はすべて. Defaults to None.
    condition (Callable[[np.ndarray], np.ndarray]): 真偽値配列を返す条件関数
    mode (str, optional): 判定モード ("any" または "all"). Defaults to "any".
    
Returns:
    np.ndarray: 一致したインデックスの配列"""
        ...
    

    def search_missing_values(
        self,
        data: columns = typing.Optional[typing.List[str]],
        column: columns = typing.Optional[typing.List[str]]
    ) -> list[int]:
        """欠損値（None/NaN）が含まれるインデックスリストを返します

Args:
    collection (ColumnCollection): データコレクション
    columns (List[str], optional): 検索対象のカラム名リスト. 未指定時はすべて. Defaults to None.
    mode (str, optional): 判定モード ("any" または "all"). Defaults to "any".
    
Returns:
    np.ndarray: 欠損値を含むインデックスの配列"""
        ...
    

    def search_top_n(
        self,
        values: vals = typing.Any,
        column: vals = typing.Any,
        n: int,
        descending: bool = True
    ) -> list[int]:
        """指定されたカラムから上位または下位N件のインデックスリストを返します

Args:
    collection (ColumnCollection): データコレクション
    vals (str | np.ndarray): 対象のカラム名または配列
    n (int, optional): 取得件数. Defaults to 5.
    largest (bool, optional): Trueなら大きい順、Falseなら小さい順. Defaults to True.
    
Returns:
    np.ndarray: 上位（下位）N件のインデックスの配列"""
        ...
    

    def select(
        self,
        columns: Optional[list[str]] = None,
        indices: Optional[list[int]] = None,
        steps: Optional[list[Union[int, float]]] = None,
        by_step_value: bool = True,
        tolerance: Optional[float] = None
    ) -> tuple[list[int], dict[str, Any]]:
        """条件（行や列）に基づいてデータを抽出し、新しいコレクションを作成します

Args:
    collection (ColumnCollection): データコレクション
    columns (str | List[str], optional): 抽出するカラム名. Defaults to None (全カラム).
    start (int, optional): 抽出開始インデックス. Defaults to None.
    end (int, optional): 抽出終了インデックス. Defaults to None.
    step_min (float, optional): 最小ステップ値. Defaults to None.
    step_max (float, optional): 最大ステップ値. Defaults to None.
    
Returns:
    ColumnCollection: 条件に一致するデータのみを含む新しいコレクション"""
        ...
    

    def fetch_near_step(
        self,
        column: str,
        value: float,
        **kwargs
    ) -> "CollectionListOperations[CoreCollectionOperations]":
        """指定ステップ値に最も近いデータ行を一つ抽出します

Args:
    collection (ColumnCollection): データコレクション
    target_step (float): 抽出したい基準ステップ値
    
Returns:
    ColumnCollection: ターゲットに最も近い1行のみを含む新しいコレクション（要素数1）"""
        ...
    

    def split_by_integers(
        self,
        markers: Union[list[int], ndarray]
    ) -> "CollectionListOperations[CoreCollectionOperations]":
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
    ) -> "CollectionListOperations[CoreCollectionOperations]":
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
    ColumnCollection: 切り替え済みのデータを持つ新しいコレクション"""
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
    ColumnCollection: ブレンド済みのデータを持つ新しいコレクション"""
        ...
    

    def sum_columns(
        self,
        data: columns = typing.Optional[typing.List[str]],
        column: columns = typing.Optional[typing.List[str]],
        columns = None
    ) -> Any:
        """指定された複数のカラムの要素ごとの合計を計算します

Args:
    collection (ColumnCollection): データコレクション
    columns (List[str], optional): 合計するカラム名のリスト. 未指定時はすべて. Defaults to None.
    
Returns:
    ColumnCollection: 合計値カラムが追加された新しいコレクション"""
        ...
    

    def average_columns(
        self,
        data: columns = typing.Optional[typing.List[str]],
        column: columns = typing.Optional[typing.List[str]],
        columns = None
    ) -> Any:
        """指定された複数のカラムの要素ごとの平均を計算します

Args:
    collection (ColumnCollection): データコレクション
    columns (List[str], optional): 平均するカラム名のリスト. 未指定時はすべて. Defaults to None.
    
Returns:
    ColumnCollection: 平均値カラムが追加された新しいコレクション"""
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
        """条件列の値と閾値の比較結果に基づき、2つの列から値を選択します

Args:
    collection (ColumnCollection): データコレクション
    v1 (str | np.ndarray): 条件付き真(True)の時に選ばれるデータ
    v2 (str | np.ndarray): 条件付き偽(False)の時に選ばれるデータ
    cond_values (str | np.ndarray): 条件判定の基準となるデータ列
    threshold (int | float, optional): 条件判定の閾値. Defaults to 0.
    compare (str, optional): 比較演算子 (">", "<", ">=", "<=", "==", "!="). Defaults to ">".
    
Returns:
    ColumnCollection: 条件に基づいて選択されたデータを持つ新しいコレクション"""
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
    ) -> "CollectionListOperations[CoreCollectionOperations]":
        """ユーザー提供のカスタム関数を利用して2つの列を合成します

Args:
    collection (ColumnCollection): データコレクション
    v1 (str | np.ndarray): 第一引数となるデータ列
    v2 (str | np.ndarray): 第二引数となるデータ列
    combine_func (Callable[[Any, Any], Any]): 合成処理を行うコールバック関数
    func_name (str, optional): 関数の名前（結果のカラム名に使用）. Defaults to None.
    
Returns:
    ColumnCollection: カスタム加工されたデータを含む新しいコレクション"""
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
    ) -> "CollectionListOperations[CoreCollectionOperations]":
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
    ) -> "CoreCollectionOperations":
        """指定した列の値を基準にしてデータを内挿（リスサンプリング）します

Args:
    collection (ColumnCollection): データコレクション
    base_column_name (str, optional): 新たな共有x軸として設定するカラム名. Defaults to "step".
    x_values (List[float], optional): 明示的な新しいx軸の配列. Defaults to None.
    point_count (int, optional): 自動生成時の内挿点数. Defaults to None.
    method (str, optional): 補間方法 ("linear", "nearest" 等). Defaults to "linear".
    columns (List[str], optional): 明示的に線形補間対象とするカラム名のリスト. 未指定時はすべて自動判定. Defaults to None.
    
Returns:
    ColumnCollection: 内挿後のデータを持つ新しいコレクション"""
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
    def as_domain(self, domain: Literal['strain'], **kwargs: Any) -> StrainCollectionOperations:
        ...

    @overload
    def as_domain(self, domain: Literal['load_displacement'], **kwargs: Any) -> LoadDisplacementCollectionOperations:
        ...

    @overload
    def as_domain(self, domain: Literal['coordinate'], **kwargs: Any) -> CoordinateCollectionOperations:
        ...

    def as_domain(self, domain: str, **kwargs: Any) -> Any:
        """現在のコレクションを指定されたドメインに変換
        
        Args:
            domain: 変換先のドメイン名
            **kwargs: 変換に渡す追加の引数
        
        Returns:
            適切なドメイン特化型のCollectionOperationsオブジェクト
        """
        ...
