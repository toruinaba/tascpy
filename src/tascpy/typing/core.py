# 自動生成されたcoreドメインのスタブファイル - 編集しないでください
from typing import Optional, Union, List, Dict, Any, Callable, TypeVar, cast, Generic, overload, Literal
from ..core.collection import ColumnCollection
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
        dup_type: str = 'all',
        column: columns = typing.Optional[typing.List[str]],
        columns: Optional[list[str]] = None,
        dup_type: str = 'all'
    ) -> list[int]:
        """"""
        ...
    

    def remove_outliers(
        self,
        window_size: int = 3,
        threshold: float = 0.5,
        edge_handling: str = 'asymmetric',
        min_abs_value: float = 1e-10,
        scale_factor: float = 1.0
    ) -> "CollectionListOperations[CoreCollectionOperations]":
        """異常値を検出して除去した新しいコレクションを返します"""
        ...
    

    def filter_by_condition(
        self,
        condition: <built-in function callable>
    ) -> "CollectionListOperations[CoreCollectionOperations]":
        """指定された列の値が条件を満たす行をフィルタリングします"""
        ...
    

    def remove_steps(
        self,
        steps: list[Any],
        tolerance: Optional[float] = None
    ) -> list[bool]:
        """指定されたステップ値を持つ行を削除します"""
        ...
    

    def filter_val(
        self,
        column_name: str,
        value: Any,
        tolerance: Optional[float] = None
    ) -> "CoreCollectionOperations":
        """filter_by_value のエイリアス"""
        ...
    

    def filter_cond(
        self,
        column_name: str,
        condition: <built-in function callable>
    ) -> "CoreCollectionOperations":
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
    ) -> "CoreCollectionOperations":
        """remove_outliers のエイリアス"""
        ...
    

    def search_by_value(
        self,
        vals: values = typing.Any,
        column: values = typing.Any,
        op_str: str,
        value: Any
    ) -> list[int]:
        """"""
        ...
    

    def search_by_range(
        self,
        column: str,
        min_value: Any,
        max_value: Any,
        inclusive: bool = True
    ) -> list[int]:
        """"""
        ...
    

    def search_by_step_range(
        self,
        min: Union[int, float],
        max: Union[int, float],
        inclusive: bool = True,
        by_step_value: bool = True,
        tolerance: Optional[float] = None
    ) -> Union[list[int], tuple]:
        """"""
        ...
    

    def search_by_condition(
        self,
        data: columns = typing.Optional[typing.List[str]],
        column: columns = typing.Optional[typing.List[str]],
        condition_func: Callable[[Dict[str, Any]], bool]
    ) -> list[int]:
        """"""
        ...
    

    def search_missing_values(
        self,
        data: columns = typing.Optional[typing.List[str]],
        column: columns = typing.Optional[typing.List[str]]
    ) -> list[int]:
        """Find indices of rows with missing values (any column)"""
        ...
    

    def search_top_n(
        self,
        column: str,
        n: int,
        descending: bool = True
    ) -> list[int]:
        """"""
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
        """"""
        ...
    

    def fetch_near_step(
        self,
        column: str,
        value: float,
        **kwargs
    ) -> "CollectionListOperations[CoreCollectionOperations]":
        """"""
        ...
    

    def switch_by_step(
        self,
        v1: ndarray,
        v2: ndarray,
        threshold: Union[int, float],
        compare_mode: str = 'value',
        by_step_value: bool = True,
        result_column: Optional[str] = None,
        in_place: bool = False,
        tolerance: Optional[float] = None
    ) -> Any:
        """ステップ値を基準に2つのColumnを切り替える (ベクトル化済み)"""
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
        result_column: Optional[str] = None,
        in_place: bool = False,
        tolerance: Optional[float] = None
    ) -> Any:
        """ステップ値の範囲内で2つのColumnをブレンドする (ベクトル化済み)"""
        ...
    

    def sum_columns(
        self,
        columns: Optional[list[str]] = None
    ) -> Any:
        """複数の列を合計します。

指定した複数の列の値を要素ごとに合計し、結果の配列を返します。

Args:
    data: 列データの辞書 (inject_columnsにより注入)
    columns: 合計対象の列名リスト"""
        ...
    

    def average_columns(
        self,
        columns: Optional[list[str]] = None
    ) -> Any:
        """複数の列の平均値を計算します。

指定した複数の列の値を要素ごとに平均し、結果の配列を返します。

Args:
    data: 列データの辞書 (inject_columnsにより注入)
    columns: 平均対象の列名リスト"""
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
    ) -> "CollectionListOperations[CoreCollectionOperations]":
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
    ) -> "CoreCollectionOperations":
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
