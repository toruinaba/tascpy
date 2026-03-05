# 自動生成されたload_displacementドメインのスタブファイル - 編集しないでください
from typing import Optional, Union, List, Dict, Any, Callable, TypeVar, cast, Generic, overload, Literal
from tascpy.core.collection import ColumnCollection
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
    ) -> "LoadDisplacementCollectionOperations":
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
        """calculate_stiffness のエイリアス"""
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
    ) -> "LoadDisplacementCollectionOperations":
        """find_yield_point のエイリアス"""
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
    ) -> "LoadDisplacementCollectionOperations":
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
    ) -> "LoadDisplacementCollectionOperations":
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
        data: column = <class 'float'>,
        column: column = <class 'float'>,
        step: float = 0.5
    ) -> "LoadDisplacementCollectionOperations":
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
    ) -> "CollectionListOperations[LoadDisplacementCollectionOperations]":
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
        column: str,
        disps: ndarray,
        markers: ndarray,
        *args,
        **kwargs
    ) -> "LoadDisplacementCollectionOperations":
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
        column: str,
        disps: ndarray,
        markers: ndarray,
        *args,
        **kwargs
    ) -> "LoadDisplacementCollectionOperations":
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
        data: column = <class 'float'>,
        distance: int = 1,
        threshold: float = None,
        column: column = <class 'float'>,
        distance: int = 1,
        threshold: Optional[float] = None
    ) -> "LoadDisplacementCollectionOperations":
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
    

    def filter_by_value(
        self,
        values: column = <class 'str'>,
        tolerance: Optional[float] = None,
        column: column = <class 'str'>,
        value: Any,
        tolerance: Optional[float] = None
    ) -> ndarray:
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
        mode: str = 'any',
        column: str,
        mode: str = 'any'
    ) -> list[bool]:
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
        data: columns = typing.Optional[typing.List[str]],
        dup_type: str = 'all',
        column: columns = typing.Optional[typing.List[str]],
        mode: str = 'consecutive',
        dup_type: str = 'all'
    ) -> list[int]:
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
    ) -> Any:
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
        vals: column = <class 'str'>,
        column: column = <class 'str'>,
        condition: <built-in function callable>
    ) -> "CollectionListOperations[LoadDisplacementCollectionOperations]":
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
    ) -> list[bool]:
        """指定されたステップ値のリストに一致する行を除外します。

Args:
    collection (ColumnCollection): データコレクション
    steps (List[float] | np.ndarray): 除外したいステップ値のリスト
    
Returns:
    ColumnCollection: 指定したステップが除外された新しいコレクション
    
Examples:
    >>> filtered_col = col.ops.remove_steps(steps=[1.0, 2.0, 3.0])"""
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
    np.ndarray: 一致したインデックスの配列
    
Examples:
    >>> indices = col.ops.search_by_value("状態", "エラー")"""
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
    np.ndarray: 範囲内に収まるインデックスの配列
    
Examples:
    >>> indices = col.ops.search_by_range("荷重", min=10.0, max=50.0)"""
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
    np.ndarray: 条件に一致したインデックスの配列
    
Examples:
    >>> indices = col.ops.search_by_step_range(min=0.0, max=10.0)"""
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
    np.ndarray: 一致したインデックスの配列
    
Examples:
    >>> indices = col.ops.search_by_condition(columns=["荷重"], condition=lambda x: x > 100)"""
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
    np.ndarray: 欠損値を含むインデックスの配列
    
Examples:
    >>> nan_indices = col.ops.search_missing_values()"""
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
    np.ndarray: 上位（下位）N件のインデックスの配列
    
Examples:
    >>> top_5_idx = col.ops.search_top_n("荷重", n=5, largest=True)"""
        ...
    

    def select(
        self,
        columns: Optional[list[str]] = None,
        indices: Optional[list[int]] = None,
        steps: Optional[list[Union[int, float]]] = None,
        by_step_value: bool = True,
        tolerance: Optional[float] = None
    ) -> tuple[list[int], dict[str, Any]]:
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
    ) -> "CollectionListOperations[LoadDisplacementCollectionOperations]":
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
    ) -> "CollectionListOperations[LoadDisplacementCollectionOperations]":
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
    ) -> "CollectionListOperations[LoadDisplacementCollectionOperations]":
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
    ) -> "LoadDisplacementCollectionOperations":
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
    ) -> "LoadDisplacementCollectionOperations":
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
        data: columns = typing.Optional[typing.List[str]],
        column: columns = typing.Optional[typing.List[str]],
        columns = None
    ) -> "LoadDisplacementCollectionOperations":
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
        data: columns = typing.Optional[typing.List[str]],
        column: columns = typing.Optional[typing.List[str]],
        columns = None
    ) -> "LoadDisplacementCollectionOperations":
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
    ) -> "LoadDisplacementCollectionOperations":
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
        v1: v1 = typing.Any,
        v2: v2 = typing.Any,
        combine_func: combine_func = typing.Callable[[typing.Any, typing.Any], typing.Any],
        column: v1 = typing.Any,
        v2: Any,
        combine_func: Callable[[Any, Any], Any],
        **kwargs
    ) -> "CollectionListOperations[LoadDisplacementCollectionOperations]":
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
    ) -> "LoadDisplacementCollectionOperations":
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
    ) -> "LoadDisplacementCollectionOperations":
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
    ) -> "LoadDisplacementCollectionOperations":
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
    ) -> "LoadDisplacementCollectionOperations":
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
        y: y_values = <class 'numpy.ndarray'>,
        x: x_values = <class 'numpy.ndarray'>,
        method: str = 'central',
        column: y_values = <class 'numpy.ndarray'>,
        x: Union[ndarray, list[float]],
        method: str = 'central'
    ) -> "LoadDisplacementCollectionOperations":
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
        y: y_values = <class 'numpy.ndarray'>,
        x: x_values = <class 'numpy.ndarray'>,
        method: str = 'trapezoidal',
        initial_value: float = 0.0,
        column: y_values = <class 'numpy.ndarray'>,
        x: Union[ndarray, list[float]],
        method: str = 'trapezoid',
        initial_value: float = 0.0
    ) -> "LoadDisplacementCollectionOperations":
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
        collection: collection = <class 'tascpy.core.collection.ColumnCollection'>,
        column: collection = <class 'tascpy.core.collection.ColumnCollection'>,
        expression: str,
        **kwargs
    ) -> "LoadDisplacementCollectionOperations":
        """与えられた数式文字列を評価し、新しい列を生成します。

Args:
    collection (ColumnCollection): データコレクション
    expression (str): 評価する数式文字列（例: "CH01 * 2 + CH02"）
    
Returns:
    ColumnCollection: 計算結果カラムが追加された新しいコレクション
    
Examples:
    >>> res_col = col.ops.evaluate("荷重 * 2.0 + 10.0")"""
        ...
    

    def sin(
        self,
        values: values = <class 'numpy.ndarray'>,
        degrees: bool = False,
        column: values = <class 'numpy.ndarray'>,
        degrees: bool = False
    ) -> "LoadDisplacementCollectionOperations":
        """指定されたカラムの正弦（Sine）を計算します。

Args:
    collection (ColumnCollection): データコレクション
    values (str | np.ndarray): 対象のカラム名
    degrees (bool, optional): 角度を度数法で扱うか. Defaults to False.
    
Returns:
    ColumnCollection: 計算結果カラムが追加されたコレクション
    
Examples:
    >>> sin_col = col.ops.sin("Angle", degrees=True)"""
        ...
    

    def cos(
        self,
        values: values = <class 'numpy.ndarray'>,
        degrees: bool = False,
        column: values = <class 'numpy.ndarray'>,
        degrees: bool = False
    ) -> "LoadDisplacementCollectionOperations":
        """指定されたカラムの余弦（Cosine）を計算します。

Args:
    collection (ColumnCollection): データコレクション
    values (str | np.ndarray): 対象のカラム名
    degrees (bool, optional): 角度を度数法で扱うか. Defaults to False.
    
Returns:
    ColumnCollection: 計算結果カラムが追加されたコレクション
    
Examples:
    >>> cos_col = col.ops.cos("Angle", degrees=True)"""
        ...
    

    def tan(
        self,
        values: values = <class 'numpy.ndarray'>,
        degrees: bool = False,
        column: values = <class 'numpy.ndarray'>,
        degrees: bool = False
    ) -> "LoadDisplacementCollectionOperations":
        """指定されたカラムの正接（Tangent）を計算します。

Args:
    collection (ColumnCollection): データコレクション
    values (str | np.ndarray): 対象のカラム名
    degrees (bool, optional): 角度を度数法で扱うか. Defaults to False.
    
Returns:
    ColumnCollection: 計算結果カラムが追加されたコレクション
    
Examples:
    >>> tan_col = col.ops.tan("Angle", degrees=True)"""
        ...
    

    def exp(
        self,
        values: values = <class 'numpy.ndarray'>,
        column: values = <class 'numpy.ndarray'>
    ) -> "LoadDisplacementCollectionOperations":
        """指定されたカラムの指数関数（e^x）を計算します。

Args:
    collection (ColumnCollection): データコレクション
    values (str | np.ndarray): 対象のカラム名
    
Returns:
    ColumnCollection: 計算結果カラムが追加されたコレクション
    
Examples:
    >>> exp_col = col.ops.exp("CH1")"""
        ...
    

    def log(
        self,
        values: values = <class 'numpy.ndarray'>,
        base: float = 2.718281828459045,
        column: values = <class 'numpy.ndarray'>,
        base: float = 2.718281828459045
    ) -> "LoadDisplacementCollectionOperations":
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
        values: values = <class 'numpy.ndarray'>,
        column: values = <class 'numpy.ndarray'>
    ) -> "LoadDisplacementCollectionOperations":
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
        values: column = <class 'str'>,
        exponent: float = 1.0,
        column: column = <class 'str'>,
        exponent: float
    ) -> "LoadDisplacementCollectionOperations":
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
        values: column = <class 'str'>,
        column: column = <class 'str'>
    ) -> "LoadDisplacementCollectionOperations":
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
        values: column = <class 'str'>,
        decimals: int = 0,
        column: column = <class 'str'>,
        decimals: int = 0
    ) -> "LoadDisplacementCollectionOperations":
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
        values: column = <class 'str'>,
        method: str = 'minmax',
        column: column = <class 'str'>,
        method: str = 'minmax'
    ) -> "LoadDisplacementCollectionOperations":
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
        ignore_nan: bool = True,
        column: str,
        ignore_nan: bool = True
    ) -> "LoadDisplacementCollectionOperations":
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
    ColumnCollection: 移動平均値が追加された新しいコレクション
    
Examples:
    >>> smoothed_col = col.ops.moving_average("荷重", window_size=5)"""
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
    ) -> "LoadDisplacementCollectionOperations":
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
        vals: vals = typing.Any,
        sigma: float = 1.0,
        window_size: Optional[int] = None,
        column: vals = typing.Any,
        sigma: float = 1.0,
        window_size: Optional[int] = None
    ) -> "LoadDisplacementCollectionOperations":
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
    

    def max(
        self,
        column: str
    ) -> float:
        """指定されたカラムの最大値を計算します。

Args:
    collection (ColumnCollection): データコレクション
    column_name (str): 計算対象のカラム名
    
Returns:
    ColumnCollection: 統計量として最大値が記録された新しいコレクション
    
Examples:
    >>> col = col.ops.max("荷重")
    >>> max_val = col.results["max(荷重)"].value"""
        ...
    

    def min(
        self,
        column: str
    ) -> float:
        """指定されたカラムの最小値を計算します。

Args:
    collection (ColumnCollection): データコレクション
    column_name (str): 計算対象のカラム名
    
Returns:
    ColumnCollection: 統計量として最小値が記録された新しいコレクション
    
Examples:
    >>> col = col.ops.min("変位")"""
        ...
    

    def mean(
        self,
        column: str
    ) -> float:
        """指定されたカラムの平均値を計算します。

Args:
    collection (ColumnCollection): データコレクション
    column_name (str): 計算対象のカラム名
    
Returns:
    ColumnCollection: 統計量として平均値が記録された新しいコレクション
    
Examples:
    >>> col = col.ops.mean("変位")"""
        ...
    

    def std(
        self,
        column: str
    ) -> float:
        """指定されたカラムの標準偏差を計算します。

Args:
    collection (ColumnCollection): データコレクション
    column_name (str): 計算対象のカラム名
    
Returns:
    ColumnCollection: 統計量として標準偏差が記録された新しいコレクション
    
Examples:
    >>> col = col.ops.std("荷重")"""
        ...
    

    def sum(
        self,
        column: str
    ) -> float:
        """指定されたカラムの合計値を計算します。

Args:
    collection (ColumnCollection): データコレクション
    column_name (str): 計算対象のカラム名
    
Returns:
    ColumnCollection: 統計量として合計値が記録された新しいコレクション
    
Examples:
    >>> col = col.ops.sum("エネルギー")
    >>> total_energy = col.results["sum(エネルギー)"].value"""
        ...
    

    def interpolate(
        self,
        base_column_name: str = 'step',
        x_values: Optional[list[float]] = None,
        point_count: Optional[int] = None,
        method: str = 'linear',
        columns: Optional[list[str]] = None
    ) -> "LoadDisplacementCollectionOperations":
        """指定した列の値を基準にしてデータを内挿（リスサンプリング）します

Args:
    collection (ColumnCollection): データコレクション
    base_column_name (str, optional): 新たな共有x軸として設定するカラム名. Defaults to "step".
    x_values (List[float], optional): 明示的な新しいx軸の配列. Defaults to None.
    point_count (int, optional): 自動生成時の内挿点数. Defaults to None.
    method (str, optional): 補間方法 ("linear", "nearest" 等). Defaults to "linear".
    columns (List[str], optional): 明示的に線形補間対象とするカラム名のリスト. 未指定時はすべて自動判定. Defaults to None.
    
Returns:
    ColumnCollection: 内挿後のデータを持つ新しいコレクション
    
Examples:
    >>> interp_col = col.ops.interpolate(base_column_name="Time", point_count=1000)"""
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
