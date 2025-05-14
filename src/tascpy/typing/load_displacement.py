# 自動生成されたload_displacementドメインのスタブファイル - 編集しないでください
from typing import Optional, Union, List, Dict, Any, Callable, TypeVar, cast
from ..core.collection import ColumnCollection
from .proxy_base import CollectionOperationsBase

class LoadDisplacementCollectionOperations(CollectionOperationsBase):
    """load_displacementドメインの操作メソッドスタブ定義
    
    このクラスはPylanceの型チェックとオートコンプリートのためのスタブです。
    実際の実行には使用されません。
    """

    def end(self) -> ColumnCollection:
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
        
    ) -> "LoadDisplacementCollectionOperations":
        """荷重データのカラム名を取得

Args:
    collection: 荷重-変位コレクション

Returns:
    str: 荷重データのカラム名"""
        ...
    

    def get_displacement_column(
        self,
        
    ) -> "LoadDisplacementCollectionOperations":
        """変位データのカラム名を取得

Args:
    collection: 荷重-変位コレクション

Returns:
    str: 変位データのカラム名"""
        ...
    

    def get_load_data(
        self,
        
    ) -> "LoadDisplacementCollectionOperations":
        """荷重データを取得

Args:
    collection: 荷重-変位コレクション

Returns:
    np.ndarray: 荷重データの配列"""
        ...
    

    def get_displacement_data(
        self,
        
    ) -> "LoadDisplacementCollectionOperations":
        """変位データを取得

Args:
    collection: 荷重-変位コレクション

Returns:
    np.ndarray: 変位データの配列"""
        ...
    

    def get_valid_data_mask(
        self,
        
    ) -> "LoadDisplacementCollectionOperations":
        """有効なデータポイントのマスクを取得

Args:
    collection: 荷重-変位コレクション

Returns:
    np.ndarray: 有効なデータのブールマスク"""
        ...
    

    def get_valid_data(
        self,
        
    ) -> "LoadDisplacementCollectionOperations":
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
    ) -> "LoadDisplacementCollectionOperations":
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
    ) -> "LoadDisplacementCollectionOperations":
        """サイクル番号ごとにデータを分割

データをサイクル番号ごとに分割し、各サイクルの
荷重-変位コレクションのリストを返します。

Args:
    collection: 荷重-変位コレクション
    cycle_column: サイクル番号を含む列名（指定がない場合は自動検出/生成）

Returns:
    List[LoadDisplacementCollection]: サイクルごとに分割されたコレクションのリスト"""
        ...
    

    def get_curve_data(
        self,
        curve_name: str
    ) -> "LoadDisplacementCollectionOperations":
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
    ) -> "LoadDisplacementCollectionOperations":
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
        
    ) -> "LoadDisplacementCollectionOperations":
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
    

    def plot_load_displacement(
        self,
        ax: Optional[Axes] = None,
        kwargs
    ) -> "LoadDisplacementCollectionOperations":
        """荷重-変位曲線をプロットします

荷重-変位データを二次元グラフとしてプロットします。
既存の軸オブジェクトを指定することも、新しく作成することもできます。

Args:
    collection: 荷重-変位コレクション
    ax: プロット先の軸（None の場合は新規作成）
    **kwargs: matplotlib の plot 関数に渡す追加引数

Returns:
    LoadDisplacementCollection: 元の荷重-変位コレクション"""
        ...
    

    def plot_skeleton_curve(
        self,
        plot_original: bool = True,
        skeleton_load_column: Optional[str] = None,
        skeleton_disp_column: Optional[str] = None,
        ax: Optional[Axes] = None,
        original_kwargs: Optional[dict[str, Any]] = None,
        skeleton_kwargs: Optional[dict[str, Any]] = None
    ) -> "LoadDisplacementCollectionOperations":
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
    LoadDisplacementCollection: 元の荷重-変位コレクション

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
    ) -> "LoadDisplacementCollectionOperations":
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
    LoadDisplacementCollection: 元の荷重-変位コレクション

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
        kwargs
    ) -> "LoadDisplacementCollectionOperations":
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
    LoadDisplacementCollection: 元の荷重-変位コレクション"""
        ...
    

    def plot_yield_analysis_details(
        self,
        ax: Optional[Axes] = None,
        kwargs
    ) -> "LoadDisplacementCollectionOperations":
        """降伏点解析の詳細情報をプロットします

find_yield_point 関数で解析した降伏点情報の詳細をビジュアル化します。
初期勾配の計算範囲などの追加情報も表示します。

Args:
    collection: 降伏点情報を含む荷重-変位コレクション
    ax: プロット先の軸（None の場合は新規作成）
    **kwargs: matplotlib の plot 関数に渡す追加引数

Returns:
    LoadDisplacementCollection: 元の荷重-変位コレクション"""
        ...
    

    def compare_yield_methods(
        self,
        methods: list[dict[str, Any]] = None,
        ax: Optional[Axes] = None,
        kwargs
    ) -> "LoadDisplacementCollectionOperations":
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
    LoadDisplacementCollection: 元の荷重-変位コレクション"""
        ...
    
