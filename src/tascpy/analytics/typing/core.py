# 自動生成されたcoreドメインのスタブファイル - 編集しないでください
from __future__ import annotations
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
        column: str,
        value: Any,
        tolerance: Optional[float] = None
    ) -> CoreCollectionOperations:
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
        column: str,
        mode: str = 'any'
    ) -> CoreCollectionOperations:
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
        columns: Optional[list[str]],
        mode: str = 'consecutive',
        dup_type: str = 'all'
    ) -> CoreCollectionOperations:
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
        column: str,
        *args,
        **kwargs
    ) -> CoreCollectionOperations:
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
        column: str,
        condition: <built-in function callable>
    ) -> "CollectionListOperations[CoreCollectionOperations]":
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
    ) -> CoreCollectionOperations:
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
    ) -> CoreCollectionOperations:
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
        column: str,
        value: float
    ) -> "CollectionListOperations[CoreCollectionOperations]":
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
    ) -> "CollectionListOperations[CoreCollectionOperations]":
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
    ) -> "CollectionListOperations[CoreCollectionOperations]":
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
        step_values: ndarray,
        v1: Union[str, ndarray],
        v2: Union[str, ndarray],
        threshold: Union[int, float],
        compare_mode: str = 'value',
        by_step_value: bool = True,
        tolerance: Optional[float] = None
    ) -> CoreCollectionOperations:
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
        step_values: ndarray,
        v1: ndarray,
        v2: ndarray,
        start: Union[int, float],
        end: Union[int, float],
        compare_mode: str = 'value',
        by_step_value: bool = True,
        blend_method: str = 'linear',
        tolerance: Optional[float] = None
    ) -> CoreCollectionOperations:
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
        columns: Optional[list[str]],
        columns = None
    ) -> CoreCollectionOperations:
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
        columns: Optional[list[str]],
        columns = None
    ) -> CoreCollectionOperations:
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
        column: str,
        v2: ndarray,
        cond_values: ndarray,
        threshold: Union[int, float] = 0,
        compare: str = '>'
    ) -> CoreCollectionOperations:
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
        column: str,
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
    ColumnCollection: カスタム加工されたデータを含む新しいコレクション
    
Examples:
    >>> custom_col = col.ops.custom_combine("CH1", "CH2", combine_func=lambda x, y: x**2 + y**2, func_name="sum_squares")"""
        ...
    

    def add(
        self,
        column: str,
        v2: Union[ndarray, float]
    ) -> CoreCollectionOperations:
        """複数カラムまたはスカラー値の要素ごとの和を計算します。

Args:
    collection (ColumnCollection): データコレクション
    value1 (Union[str, float]): 第1引数（カラム名または数値）
    value2 (Union[str, float]): 第2引数（カラム名または数値）
    
Returns:
    ColumnCollection: 計算結果カラムが追加された新しいコレクション
    
Examples:
    >>> col = col.ops.add("CH01", "CH02")      # CH01 + CH02 -> 新しい列に追加
    >>> col = col.ops.add("CH01", 10.5)        # CH01に10.5を加算"""
        ...
    

    def subtract(
        self,
        column: str,
        v2: Union[ndarray, float]
    ) -> CoreCollectionOperations:
        """第一引数から第二引数の要素ごとの差を計算します。

Args:
    collection (ColumnCollection): データコレクション
    value1 (Union[str, float]): 第1引数（カラム名または数値）
    value2 (Union[str, float]): 第2引数（引き算するカラム名または数値）

Returns:
    ColumnCollection: 計算結果カラムが追加された新しいコレクション
    
Examples:
    >>> col = col.ops.subtract("CH01", "CH02") # CH01 - CH02
    >>> col = col.ops.subtract("CH01", 10.5)   # CH01 - 10.5"""
        ...
    

    def multiply(
        self,
        column: str,
        v2: Union[ndarray, float]
    ) -> CoreCollectionOperations:
        """複数カラムまたはスカラー値の要素ごとの積を計算します。

Args:
    collection (ColumnCollection): データコレクション
    value1 (Union[str, float]): 第1引数（カラム名または数値）
    value2 (Union[str, float]): 第2引数（カラム名または数値）

Returns:
    ColumnCollection: 計算結果カラムが追加された新しいコレクション
    
Examples:
    >>> col = col.ops.multiply("CH01", 2.0)    # CH01 * 2.0"""
        ...
    

    def divide(
        self,
        column: str,
        v2: Union[ndarray, float],
        **kwargs
    ) -> CoreCollectionOperations:
        """第一引数を第二引数で要素ごとに除算します。

Args:
    collection (ColumnCollection): データコレクション
    value1 (Union[str, float]): 分子（カラム名または数値）
    value2 (Union[str, float]): 分母（カラム名または数値）
    
Returns:
    ColumnCollection: 計算結果カラムが追加された新しいコレクション
    
Examples:
    >>> col = col.ops.divide("CH01", 1000)     # CH01 / 1000 (例: N -> kN変換など)"""
        ...
    

    def diff(
        self,
        y_values: ndarray,
        x_values: ndarray,
        method: str = 'central'
    ) -> CoreCollectionOperations:
        """データ系列の離散微分 (dy/dx) を計算します

Args:
    collection (ColumnCollection): データコレクション
    y_column (str): Y軸データとなるカラム名
    x_column (str): X軸データとなるカラム名
    method (str, optional): 微分手法 ("forward", "backward", "central"). Defaults to "central".
    
Returns:
    ColumnCollection: 微分値カラムが追加された新しいコレクション
    
Examples:
    >>> diff_col = col.ops.diff(y_column="変位", x_column="__step__", method="central")"""
        ...
    

    def integrate(
        self,
        y_values: ndarray,
        x_values: ndarray,
        method: str = 'trapezoidal',
        initial_value: float = 0.0
    ) -> CoreCollectionOperations:
        """データ系列の離散積分 (∫ y dx) を計算します

Args:
    collection (ColumnCollection): データコレクション
    y_column (str): Y軸データとなるカラム名
    x_column (str): X軸データとなるカラム名
    method (str, optional): 積分手法 ("trapezoidal", "cumulative_sum"). Defaults to "trapezoidal".
    initial_value (float, optional): 積分定数 (初期値). Defaults to 0.0.
    
Returns:
    ColumnCollection: 積分値カラムが追加された新しいコレクション
    
Examples:
    >>> int_col = col.ops.integrate(y_column="速度", x_column="__step__")"""
        ...
    

    def evaluate(
        self,
        column: str,
        expression: str,
        **kwargs
    ) -> CoreCollectionOperations:
        """与えられた数式文字列を評価し、新しい列を生成します。

Args:
    collection (ColumnCollection): データコレクション
    expression (str): 評価する数式文字列（例: "CH01 * 2 + CH02"）
    
Returns:
    ColumnCollection: 計算結果カラムが追加された新しいコレクション
    
Examples:
    >>> res_col = col.ops.evaluate("荷重 * 2.0 + 10.0")"""
        ...
    

    def log(
        self,
        column: str,
        base: float = 2.718281828459045
    ) -> CoreCollectionOperations:
        """指定されたカラムの対数（Log）を計算します。

Args:
    collection (ColumnCollection): データコレクション
    values (str | np.ndarray): 対象のカラム名
    base (float, optional): 対数の底. Defaults to e.
    
Returns:
    ColumnCollection: 計算結果カラムが追加されたコレクション
    
Examples:
    >>> log_col = col.ops.log("CH1", base=10.0)"""
        ...
    

    def sqrt(
        self,
        column: str
    ) -> CoreCollectionOperations:
        """指定されたカラムの平方根（Square Root）を計算します。

Args:
    collection (ColumnCollection): データコレクション
    values (str | np.ndarray): 対象のカラム名
    
Returns:
    ColumnCollection: 計算結果カラムが追加されたコレクション
    
Examples:
    >>> sqrt_col = col.ops.sqrt("CH1")"""
        ...
    

    def pow(
        self,
        column: str,
        exponent: float = 1.0
    ) -> CoreCollectionOperations:
        """指定されたカラムのべき乗（Power）を計算します。

Args:
    collection (ColumnCollection): データコレクション
    values (str): 対象のカラム名
    exponent (float, optional): べき乗の指数. Defaults to 1.0.
    
Returns:
    ColumnCollection: 計算結果カラムが追加されたコレクション
    
Examples:
    >>> pow_col = col.ops.pow("CH1", exponent=2.0)"""
        ...
    

    def abs_values(
        self,
        column: str
    ) -> CoreCollectionOperations:
        """指定されたカラムの絶対値（Absolute value）を計算します。

Args:
    collection (ColumnCollection): データコレクション
    values (str): 対象のカラム名
    
Returns:
    ColumnCollection: 計算結果カラムが追加されたコレクション
    
Examples:
    >>> abs_col = col.ops.abs_values("変位")"""
        ...
    

    def round_values(
        self,
        column: str,
        decimals: int = 0
    ) -> CoreCollectionOperations:
        """指定されたカラムの値を丸めます（四捨五入）。

Args:
    collection (ColumnCollection): データコレクション
    values (str): 対象のカラム名
    decimals (int, optional): 丸める小数点以下の桁数. Defaults to 0.
    
Returns:
    ColumnCollection: 計算結果カラムが追加されたコレクション
    
Examples:
    >>> rounded_col = col.ops.round_values("荷重", decimals=2)"""
        ...
    

    def normalize(
        self,
        column: str,
        method: str = 'minmax'
    ) -> CoreCollectionOperations:
        """指定されたカラムの値を正規化します。

Args:
    collection (ColumnCollection): データコレクション
    values (str): 対象のカラム名
    method (str, optional): 正規化手法 ("minmax", "zscore", "max_abs"). Defaults to "minmax".
    
Returns:
    ColumnCollection: 計算結果カラムが追加されたコレクション
    
Examples:
    >>> norm_col = col.ops.normalize("荷重", method="minmax")"""
        ...
    

    def average_across(
        self,
        *column: str,
        ignore_nan: bool = True
    ) -> CoreCollectionOperations:
        """複数カラムの値を行ごとに平均し、新しいカラムとして追加します。

Args:
    collection (ColumnCollection): データコレクション
    *columns (str): 平均を計算対象とする複数列のカラム名
    ignore_nan (bool, optional): 欠損値（NaN）を無視するかどうか。デフォルトはTrue。
    result_column (str, optional): 結果を格納するカラム名。指定しない場合は自動生成。

Returns:
    ColumnCollection: 計算結果カラムが追加されたコレクション

Examples:
    >>> avg_col = col.ops.average_across("センサ1", "センサ2", "センサ3", result_column="平均値")
    >>> avg_col = col.ops.average_across("CH01", "CH02", ignore_nan=False)"""
        ...
    

    def moving_average(
        self,
        column: str,
        window_size: int = 3,
        edge_handling: str = 'asymmetric'
    ) -> "CollectionListOperations[CoreCollectionOperations]":
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
        column: str,
        window_size: int = 3,
        threshold: float = 0.5,
        edge_handling: str = 'asymmetric',
        min_abs_value: float = 1e-10,
        scale_factor: float = 1.0
    ) -> CoreCollectionOperations:
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
        column: str,
        sigma: float = 1.0,
        window_size: Optional[int] = None
    ) -> CoreCollectionOperations:
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
            **kwargs: 変換に渡す追加の引数。ドメインごとに以下の引数が利用可能です。
                - strain: rosettes (Dict), rosette_metadata_key (str)
                - load_displacement: load_column (str), displacement_column (str)
                - coordinate: coordinates (Dict), coordinate_metadata_key (str)
                - timeseries: start_date (str/datetime), frequency (str)
                - signal: sample_rate (float)
        
        Returns:
            適切なドメイン特化型のCollectionOperationsオブジェクト
        """
        ...
