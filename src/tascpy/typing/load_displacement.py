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
        result_column: Optional[str] = None,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None
    ) -> "LoadDisplacementCollectionOperations":
        """変位と荷重の間の傾きを計算

変位と荷重の間の点ごとの傾きを計算します。
デフォルトでは変位列を独立変数（X軸）、荷重列を従属変数（Y軸）として使用します。

Args:
    collection: 荷重-変位コレクション
    result_column: 結果を格納する列名
    x_column: X軸データの列名（指定がない場合は変位列を使用）
    y_column: Y軸データの列名（指定がない場合は荷重列を使用）

Returns:
    LoadDisplacementCollection: 傾きデータを含むコレクション"""
        ...
    

    def calculate_stiffness(
        self,
        range_start: float = 0.2,
        range_end: float = 0.8,
        method: str = 'linear_regression'
    ) -> float:
        """荷重-変位曲線から剛性を計算

指定された範囲内のデータを使用して荷重-変位間の剛性（傾き）を計算します。

Args:
    collection: 荷重-変位コレクション
    range_start: 最大荷重に対する計算開始点の割合
    range_end: 最大荷重に対する計算終了点の割合
    method: 剛性計算方法 ("linear_regression" または "secant")

Returns:
    float: 剛性値"""
        ...
    

    def find_yield_point(
        self,
        method: str = 'offset',
        offset_value: float = 0.002,
        range_start: float = 0.1,
        range_end: float = 0.3,
        factor: float = 0.33,
        result_prefix: Optional[str] = 'yield',
        debug_mode: bool = False,
        fail_silently: bool = False
    ) -> "LoadDisplacementCollectionOperations":
        """降伏点を計算

荷重-変位データから降伏点を計算します。
オフセット法または一般降伏法から選択できます。

Args:
    collection: 荷重-変位コレクション
    method: 計算方法 ('offset', 'general')
    offset_value: オフセット降伏法でのオフセット量
    range_start: 初期勾配計算の範囲開始（最大荷重に対する比率）
    range_end: 初期勾配計算の範囲終了（最大荷重に対する比率）
    factor: 一般降伏法での勾配比率
    result_prefix: 結果列の接頭辞
    debug_mode: 詳細な計算過程情報を出力するかどうか
    fail_silently: 降伏点が見つからない場合に例外を発生させずに情報を返すかどうか

Returns:
    LoadDisplacementCollection: 降伏点情報または計算過程情報を含むコレクション

Raises:
    ValueError: 降伏点が見つかりず、fail_silently=False の場合"""
        ...
    

    def stiffness(
        self,
        range_start: float = 0.2,
        range_end: float = 0.8,
        method: str = 'linear_regression'
    ) -> float:
        """calculate_stiffness のエイリアス"""
        ...
    

    def yield_point(
        self,
        method: str = 'offset',
        offset_value: float = 0.002,
        range_start: float = 0.1,
        range_end: float = 0.3,
        factor: float = 0.33,
        result_prefix: Optional[str] = 'yield',
        debug_mode: bool = False,
        fail_silently: bool = False
    ) -> "LoadDisplacementCollectionOperations":
        """find_yield_point のエイリアス"""
        ...
    

    def cycle_count(
        self,
        column: Optional[str] = None,
        step: float = 0.5,
        result_column: Optional[str] = None
    ) -> "LoadDisplacementCollectionOperations":
        """データの荷重符号反転からサイクル数をカウント

荷重の符号変化（正負の反転）からサイクル数をカウントし、
新しい列として追加します。

Args:
    collection: 荷重-変位コレクション
    column: サイクルをカウントする列（指定がない場合は荷重列を使用）
    step: サイクルカウントの増分
    result_column: 結果を格納する列名

Returns:
    LoadDisplacementCollection: サイクル数を含むコレクション"""
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
    

    def get_curve_data(
        self,
        curve_name: str
    ) -> dict[str, Any]:
        """メタデータに格納された曲線データを取得

Args:
    collection: 荷重-変位コレクション
    curve_name: 曲線名（例: "skeleton_curve", "cumulative_curve"）

Returns:
    Dict[str, Any]: 曲線データ（x, y, metadataを含む辞書）

Raises:
    ValueError: 指定した曲線が存在しない場合"""
        ...
    

    def get_curve_columns(
        self,
        curve_name: str
    ) -> tuple[Optional[Column], Optional[Column]]:
        """メタデータに格納された曲線データをColumnオブジェクトとして取得

Args:
    collection: 荷重-変位コレクション
    curve_name: 曲線名（例: "skeleton_curve", "cumulative_curve"）

Returns:
    Tuple[Optional[Column], Optional[Column]]:
        (x軸のColumn, y軸のColumn)のタプル。曲線が存在しない場合は(None, None)

Raises:
    ValueError: 指定した曲線データにColumnが含まれていない場合
    ValueError: 指定した曲線が存在しない場合"""
        ...
    

    def list_available_curves(
        self,
        
    ) -> list[str]:
        """利用可能な曲線の一覧を取得

Args:
    collection: 荷重-変位コレクション

Returns:
    List[str]: 利用可能な曲線名のリスト"""
        ...
    

    def create_skeleton_curve(
        self,
        has_decrease: bool = False,
        decrease_type: str = 'envelope',
        cycle_column: Optional[str] = None,
        result_load_column: Optional[str] = None,
        result_disp_column: Optional[str] = None,
        store_as_columns: bool = False
    ) -> "LoadDisplacementCollectionOperations":
        """荷重-変位データからスケルトン曲線を作成

複数サイクルの荷重-変位データから、包絡線（スケルトン曲線）を作成します。
スケルトン曲線は、各サイクルの最大応答値を結んだ曲線です。

デフォルトでは、スケルトン曲線はメタデータの "curves" セクションに格納されます。
これにより、列の長さが異なるデータを格納できます。
また、メタデータ内にColumnオブジェクトとしても格納されるため、いつでも取得可能です。

Args:
    collection: 荷重-変位コレクション
    has_decrease: 減少部分も含めるか
    decrease_type: 減少部分の処理方法 ('envelope', 'continuous_only', 'both')
    cycle_column: サイクル列名（指定なしの場合は自動生成）
    result_load_column: 結果の荷重列名（指定なしの場合は自動生成）
    result_disp_column: 結果の変位列名（指定なしの場合は自動生成）
    store_as_columns: Trueの場合、旧形式との互換性のために列としても格納

Returns:
    LoadDisplacementCollection: スケルトン曲線データを含むコレクション"""
        ...
    

    def create_cumulative_curve(
        self,
        cycle_column: Optional[str] = None,
        result_load_column: Optional[str] = None,
        result_disp_column: Optional[str] = None,
        store_as_columns: bool = False
    ) -> "LoadDisplacementCollectionOperations":
        """荷重-変位データから累積曲線を作成

複数サイクルの荷重-変位データから、累積変形曲線を作成します。
累積曲線は、各サイクルの変形を累積的に加算した曲線です。

デフォルトでは、累積曲線はメタデータの "curves" セクションに格納されます。
これにより、列の長さが異なるデータを格納できます。
また、メタデータ内にColumnオブジェクトとしても格納されるため、いつでも取得可能です。

Args:
    collection: 荷重-変位コレクション
    cycle_column: サイクル列名（指定なしの場合は自動生成）
    result_load_column: 結果の荷重列名（指定なしの場合は自動生成）
    result_disp_column: 結果の変位列名（指定なしの場合は自動生成）
    store_as_columns: Trueの場合、旧形式との互換性のために列としても格納

Returns:
    LoadDisplacementCollection: 累積曲線データを含むコレクション"""
        ...
    

    def export_curve_to_csv(
        self,
        curve_name: str,
        file_path: str,
        columns: tuple[str, str] = ('x', 'y'),
        encoding: str = 'utf-8',
        include_header: bool = True
    ) -> None:
        """メタデータに格納された曲線データを CSV ファイルにエクスポートします。

Args:
    collection: LoadDisplacementCollection オブジェクト
    curve_name: エクスポートする曲線名（"skeleton_curve" や "cumulative_curve" など）
    file_path: 出力先の CSV ファイルパス
    columns: エクスポートするカラム名タプル（デフォルトは ("x", "y")）
    encoding: ファイルエンコーディング（デフォルトは "utf-8"）
    include_header: ヘッダー行を含めるかどうか

Raises:
    ValueError: 指定した曲線が存在しない場合、またはデータが不正な場合
    IOError: ファイル書き込みに失敗した場合"""
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
        """Check if values are equal to target value.
Supports tolerance for float comparisons."""
        ...
    

    def filter_out_none(
        self,
        data: columns = typing.Optional[typing.List[str]],
        mode: str = 'any',
        column: columns = typing.Optional[typing.List[str]],
        mode: str = 'any'
    ) -> list[bool]:
        """Return boolean mask for valid rows (no None/NaN).
mode='any': Keep row if ALL columns are valid. (Wait, logic check below)
mode='all': Keep row if ANY column is valid. 

Standard 'dropna' logic:
any: if any value is NA, drop row. (So keep if ALL valid)
all: if all values are NA, drop row. (So keep if ANY valid)

The original implementation said:
mode='any': keep if all valid (drop if any invalid?) 
  -> "mode='any': ひとつでも無効なら除外" (If any invalid, exclude -> dropna(how='any'))
mode='all': keep if any valid (drop if all invalid)
  -> "mode='all': すべて無効なら除外" (If all invalid, exclude -> dropna(how='all'))"""
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
        """Return indices to KEEP after removing duplicates.

Args:
    data: Dict of columns
    mode: 
        'consecutive': Remove if previous row is identical (keep first).
        'all': Not implemented yet, reserved for unique rows.
    dup_type:
        'all': Remove row if ALL columns match previous row value (standard).
        'any': Remove row if ANY column matches previous row value (strict)."""
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
        """Filter values by condition.
Returns boolean mask (True to keep)."""
        ...
    

    def remove_steps(
        self,
        steps: list[Any],
        tolerance: Optional[float] = None
    ) -> list[bool]:
        """Generate mask to remove specific steps.
Returns True for kept steps."""
        ...
    

    def search_by_value(
        self,
        values: values = typing.Any,
        column: values = typing.Any,
        op_str: str,
        value: Any
    ) -> list[int]:
        """Return indices where values satisfy the operator condition."""
        ...
    

    def search_by_range(
        self,
        values: vals = typing.Any,
        column: vals = typing.Any,
        min_value: Any,
        max_value: Any,
        inclusive: bool = True
    ) -> list[int]:
        """Return indices where values are within range."""
        ...
    

    def search_by_step_range(
        self,
        min: float,
        max: float,
        inclusive: bool = True,
        tolerance: Optional[float] = None,
        by_step_value: bool = True
    ) -> list[int]:
        """Return indices where steps are within range, with optional tolerance.
If by_step_value is False, searches within indices matching the step length."""
        ...
    

    def search_by_condition(
        self,
        data: columns = typing.Optional[typing.List[str]],
        column: columns = typing.Optional[typing.List[str]],
        condition_func: Callable[[Dict[str, Any]], bool]
    ) -> list[int]:
        """Find indices where condition_func(row_dict) is True."""
        ...
    

    def search_missing_values(
        self,
        data: columns = typing.Optional[typing.List[str]],
        column: columns = typing.Optional[typing.List[str]]
    ) -> list[int]:
        """Find indices of rows with any missing values."""
        ...
    

    def search_top_n(
        self,
        values: vals = typing.Any,
        column: vals = typing.Any,
        n: int,
        descending: bool = True
    ) -> list[int]:
        """Return indices of top N values.
Handles NaN by excluding them."""
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
        """基本プロット関数 (Functional wrapper)"""
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
        """異常値を可視化する (Functional implementation)"""
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
        """特定のx値に対して複数のy列の値をプロットします"""
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
        """インタラクティブなグラフを描画します (Functional wrapper)"""
        ...
    

    def select(
        self,
        columns: Optional[list[str]] = None,
        indices: Optional[list[int]] = None,
        steps: Optional[list[Union[int, float]]] = None,
        by_step_value: bool = True,
        tolerance: Optional[float] = None
    ) -> tuple[list[int], dict[str, Any]]:
        """Select indices based on steps or direct indices.
Returns: (final_indices, metadata_update)"""
        ...
    

    def fetch_near_step(
        self,
        column: str,
        value: float,
        **kwargs
    ) -> "CollectionListOperations[LoadDisplacementCollectionOperations]":
        """Find index of nearest value.
Returns list containing single index."""
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
        """Switch between v1 and v2 based on steps/index."""
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
        """Blend v1 and v2 based on steps/index."""
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
        """Select from v1 or v2 based on condition."""
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
        """Combine v1 and v2 using custom function."""
        ...
    

    def add(
        self,
        column: str,
        v2: Union[ndarray, float]
    ) -> ndarray:
        """Add two values or arrays."""
        ...
    

    def subtract(
        self,
        column: str,
        v2: Union[ndarray, float]
    ) -> ndarray:
        """Subtract v2 from v1."""
        ...
    

    def multiply(
        self,
        column: str,
        v2: Union[ndarray, float]
    ) -> ndarray:
        """Multiply two values or arrays."""
        ...
    

    def divide(
        self,
        column: str,
        v2: Union[ndarray, float],
        **kwargs
    ) -> ndarray:
        """Divide v1 by v2."""
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
        """Calculate differential coefficient from x, y coordinates."""
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
        """Calculate integral of y with respect to x."""
        ...
    

    def evaluate(
        self,
        collection: collection = <class 'tascpy.core.collection.ColumnCollection'>,
        expression: str,
        column: collection = <class 'tascpy.core.collection.ColumnCollection'>,
        expression: str,
        **kwargs
    ) -> Union[list[Optional[float]], ndarray]:
        """"""
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
        """Calculate moving average."""
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
        """Detect outliers using moving average."""
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
        """Apply gaussian filter."""
        ...
    

    def max(
        self,
        column: str
    ) -> float:
        """Get max value."""
        ...
    

    def min(
        self,
        column: str
    ) -> float:
        """Get min value."""
        ...
    

    def mean(
        self,
        column: str
    ) -> float:
        """Get mean value."""
        ...
    

    def std(
        self,
        column: str
    ) -> float:
        """Get standard deviation."""
        ...
    

    def sum(
        self,
        column: str
    ) -> float:
        """Get sum."""
        ...
    

    def sin(
        self,
        values: values = <class 'numpy.ndarray'>,
        degrees: bool = False,
        column: values = <class 'numpy.ndarray'>,
        degrees: bool = False
    ) -> ndarray:
        """Calculate sine of values."""
        ...
    

    def cos(
        self,
        values: values = <class 'numpy.ndarray'>,
        degrees: bool = False,
        column: values = <class 'numpy.ndarray'>,
        degrees: bool = False
    ) -> ndarray:
        """Calculate cosine of values."""
        ...
    

    def tan(
        self,
        values: values = <class 'numpy.ndarray'>,
        degrees: bool = False,
        column: values = <class 'numpy.ndarray'>,
        degrees: bool = False
    ) -> ndarray:
        """Calculate tangent of values."""
        ...
    

    def exp(
        self,
        values: values = <class 'numpy.ndarray'>,
        column: values = <class 'numpy.ndarray'>
    ) -> ndarray:
        """Calculate exponential of values."""
        ...
    

    def log(
        self,
        values: values = <class 'numpy.ndarray'>,
        base: float = 2.718281828459045,
        column: values = <class 'numpy.ndarray'>,
        base: float = 2.718281828459045
    ) -> ndarray:
        """Calculate logarithm of values."""
        ...
    

    def sqrt(
        self,
        values: values = <class 'numpy.ndarray'>,
        column: values = <class 'numpy.ndarray'>
    ) -> ndarray:
        """Calculate square root of values."""
        ...
    

    def pow(
        self,
        values: values = <class 'numpy.ndarray'>,
        exponent: float = 1.0,
        column: values = <class 'numpy.ndarray'>,
        exponent: float
    ) -> ndarray:
        """Calculate power of values."""
        ...
    

    def abs_values(
        self,
        values: values = <class 'numpy.ndarray'>,
        column: values = <class 'numpy.ndarray'>
    ) -> ndarray:
        """Calculate absolute values."""
        ...
    

    def round_values(
        self,
        values: values = <class 'numpy.ndarray'>,
        decimals: int = 0,
        column: values = <class 'numpy.ndarray'>,
        decimals: int = 0
    ) -> ndarray:
        """Round values to specified decimals."""
        ...
    

    def normalize(
        self,
        values: values = <class 'numpy.ndarray'>,
        method: str = 'minmax',
        column: values = <class 'numpy.ndarray'>,
        method: str = 'minmax'
    ) -> ndarray:
        """Normalize values using specified method."""
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
    

    def split_by_integers(
        self,
        length: length = <class 'int'>,
        markers: markers = typing.List[int],
        column: length = <class 'int'>,
        markers: Union[list[int], ndarray]
    ) -> list[ndarray]:
        """Calculate split indices based on integer markers."""
        ...
    

    def split_at_indices(
        self,
        length: length = <class 'int'>,
        indices: indices = typing.Union[int, typing.List[int]],
        column: length = <class 'int'>,
        indices: Union[int, list[int]]
    ) -> list[slice]:
        """Calculate split slices based on indices."""
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
