# 自動生成されたcoreドメインのスタブファイル - 編集しないでください
from typing import Optional, Union, List, Dict, Any, Callable, TypeVar, cast
from ...core.collection import ColumnCollection
from .proxy_base import CollectionOperationsBase

class CoreCollectionOperations(CollectionOperationsBase):
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
        column_name: str,
        value: Any,
        tolerance: Optional[float] = None
    ) -> "CoreCollectionOperations":
        """指定された列の値が指定された値と等しい行をフィルタリング
Args:
    collection: ColumnCollectionオブジェクト
    column_name: フィルタリングする列の名前
    value: フィルタリングする値
    tolerance: 値の許容範囲（デフォルトはNone）
Returns:
    フィルタリングされたColumnCollectionオブジェクト
Raises:
    KeyError: 指定された列名が存在しない場合
    TypeError: 指定された列がColumnオブジェクトでない場合"""
        ...
    

    def filter_out_none(
        self,
        columns: Optional[list[str]] = None,
        mode: str = 'any'
    ) -> "CoreCollectionOperations":
        """None値を含む行をフィルタリングして除外する

Args:
    collection: ColumnCollectionオブジェクト
    columns: フィルタリングする対象の列名リスト（デフォルトはNone、すべての列が対象）
    mode: フィルタリングモード 'any'（いずれかの列がNoneの行を除外）または
          'all'（すべての列がNoneの行を除外）

Returns:
    フィルタリングされたColumnCollectionオブジェクト

Raises:
    ValueError: 不正なモードが指定された場合
    KeyError: 指定された列名が存在しない場合"""
        ...
    

    def remove_consecutive_duplicates_across(
        self,
        columns: list[str],
        dup_type: str = 'all'
    ) -> "CoreCollectionOperations":
        """複数の列間で共通の連続重複データを削除した新しいColumnCollectionオブジェクトを返します。

すべての指定された列で、連続するデータポイントが同じ値を持つ場合にのみ、
その重複を1つだけ残して削除します。

Args:
    collection: 処理するColumnCollectionオブジェクト
    columns: 処理対象の列名リスト
    dup_type: 重複判定のタイプ
             'all': すべての列で値に変化がない場合に重複と判定
             'any': 一部の列だけでも値に変化がある場合は重複と判定しない

Returns:
    ColumnCollection: 連続する重複を削除したデータを持つ新しいColumnCollectionオブジェクト

Raises:
    ValueError: 不正なdup_typeが指定された場合
    KeyError: 指定された列名が存在しない場合

Examples:
    >>> # collection["A"] = [1.0, 1.0, 2.0, 2.0, 3.0, 3.0]
    >>> # collection["B"] = [10.0, 20.0, 30.0, 30.0, 40.0, 50.0]
    >>> # collection["C"] = [5, 5, 2, 2, 8, 8]
    >>> result = remove_consecutive_duplicates_across(collection, ["A", "B", "C"])
    >>> # result["A"] = [1.0, 1.0, 2.0, 3.0, 3.0]
    >>> # result["B"] = [10.0, 20.0, 30.0, 40.0, 50.0]
    >>> # result["C"] = [5, 5, 2, 8, 8]"""
        ...
    

    def search_by_value(
        self,
        column_name: str,
        op_str: str,
        value: Any
    ) -> "CoreCollectionOperations":
        """値による検索
Args:
    collection: 対象コレクション
    column_name: 列名
    op_str: 演算子文字列 (">", "<", ">=", "<=", "==", "!=")
    value: 比較する値
Returns:
    ColumnCollection: フィルタリングされたコレクション"""
        ...
    

    def search_by_range(
        self,
        column_name: str,
        min_value: Any,
        max_value: Any,
        inclusive: bool = True
    ) -> "CoreCollectionOperations":
        """範囲による検索
Args:
    collection: 対象コレクション
    column_name: 列名
    min_value: 最小値
    max_value: 最大値
    inclusive: 境界値を含むかどうか
Returns:
    ColumnCollection: フィルタリングされたコレクション"""
        ...
    

    def search_by_step_range(
        self,
        min_step: Any,
        max_step: Any,
        inclusive: bool = True
    ) -> "CoreCollectionOperations":
        """ステップ範囲による検索
Args:
    collection: 対象コレクション
    min_step: 最小ステップ値
    max_step: 最大ステップ値
    inclusive: 境界値を含むかどうか
Returns:
    ColumnCollection: フィルタリングされたコレクション"""
        ...
    

    def search_by_condition(
        self,
        condition_func: Callable[[Dict[str, Any]], bool]
    ) -> "CoreCollectionOperations":
        """条件関数による検索
Args:
    collection: 対象コレクション
    condition_func: 各行データを受け取り、真偽値を返す関数
Returns:
    ColumnCollection: フィルタリングされたコレクション"""
        ...
    

    def search_missing_values(
        self,
        columns: Optional[list[str]] = None
    ) -> "CoreCollectionOperations":
        """欠損値がある行を検索
Args:
    collection: 対象コレクション
    columns: 検査対象の列名リスト（Noneの場合は全列）
Returns:
    ColumnCollection: 欠損値を持つ行だけのコレクション"""
        ...
    

    def search_top_n(
        self,
        column_name: str,
        n: int,
        descending: bool = True
    ) -> "CoreCollectionOperations":
        """指定した列の上位N件を検索
Args:
    collection: 対象コレクション
    column_name: 列名
    n: 上位件数
    descending: 降順ソート（True）または昇順ソート（False）
Returns:
    ColumnCollection: フィルタリングされたコレクション"""
        ...
    

    def plot(
        self,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        plot_type: str = 'scatter',
        ax: Optional[Axes] = None,
        kwargs
    ) -> "CoreCollectionOperations":
        """グラフを描画する

Args:
    collection: 対象コレクション
    x_column: x軸の列名（Noneの場合はstepを使用）
    y_column: y軸の列名（Noneの場合はstepを使用）
    plot_type: プロットの種類 ('scatter' または 'line')
    ax: 既存のAxesオブジェクト（Noneの場合は新しい図を作成）
    **kwargs: Matplotlibのプロット関数に渡す追加のキーワード引数

Returns:
    ColumnCollection: 元のコレクション

Examples:
    >>> # 散布図の描画
    >>> collection.plot('x_col', 'y_col')
    >>>
    >>> # stepをx軸として使用
    >>> collection.plot(None, 'y_col')
    >>>
    >>> # stepをy軸として使用
    >>> collection.plot('x_col', None)
    >>>
    >>> # 線グラフの描画
    >>> collection.plot('x_col', 'y_col', plot_type='line', color='red')
    >>>
    >>> # 既存のaxesに追加
    >>> fig, ax = plt.subplots()
    >>> collection.plot('x_col', 'y_col', ax=ax)
    >>> collection.plot('x_col2', 'y_col2', ax=ax)  # 2つ目のプロットを追加"""
        ...
    

    def select(
        self,
        columns: Optional[list[str]] = None,
        indices: Optional[list[int]] = None
    ) -> "CoreCollectionOperations":
        """指定した列名と行インデックスに基づいてデータを抽出する

Args:
    collection: 元のColumnCollection
    columns: 抽出する列名のリスト。Noneの場合は全列が対象
    indices: 抽出する行インデックスのリスト。Noneの場合は全行が対象

Returns:
    選択されたデータを含む新しいColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合
    IndexError: 指定されたインデックスが範囲外の場合"""
        ...
    

    def select_step(
        self,
        steps: list[float],
        columns: Optional[list[str]] = None
    ) -> "CoreCollectionOperations":
        """指定した列名とステップ番号に基づいてデータを抽出する

Args:
    collection: 元のColumnCollection
    steps: 抽出するステップ番号のリスト
    columns: 抽出する列名のリスト。Noneの場合は全列が対象

Returns:
    選択されたデータを含む新しいColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合"""
        ...
    

    def add(
        self,
        column1: str,
        column2_or_value: Union[str, int, float],
        result_column: Optional[str] = None,
        in_place: bool = False
    ) -> "CoreCollectionOperations":
        """列または定数を加算

Args:
    collection: ColumnCollectionオブジェクト
    column1: 加算元の列名
    column2_or_value: 加算する列名または定数値
    result_column: 結果を格納する列名（デフォルトはNone、自動生成）
    in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成

Returns:
    ColumnCollection: 演算結果の列を含むColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合
    ValueError: 列の長さが一致しない場合、または無効な値が指定された場合"""
        ...
    

    def subtract(
        self,
        column1: str,
        column2_or_value: Union[str, int, float],
        result_column: Optional[str] = None,
        in_place: bool = False
    ) -> "CoreCollectionOperations":
        """列または定数を減算

Args:
    collection: ColumnCollectionオブジェクト
    column1: 減算元の列名
    column2_or_value: 減算する列名または定数値
    result_column: 結果を格納する列名（デフォルトはNone、自動生成）
    in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成

Returns:
    ColumnCollection: 演算結果の列を含むColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合
    ValueError: 列の長さが一致しない場合、または無効な値が指定された場合"""
        ...
    

    def multiply(
        self,
        column1: str,
        column2_or_value: Union[str, int, float],
        result_column: Optional[str] = None,
        in_place: bool = False
    ) -> "CoreCollectionOperations":
        """列または定数を乗算

Args:
    collection: ColumnCollectionオブジェクト
    column1: 乗算元の列名
    column2_or_value: 乗算する列名または定数値
    result_column: 結果を格納する列名（デフォルトはNone、自動生成）
    in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成

Returns:
    ColumnCollection: 演算結果の列を含むColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合
    ValueError: 列の長さが一致しない場合、または無効な値が指定された場合"""
        ...
    

    def divide(
        self,
        column1: str,
        column2_or_value: Union[str, int, float],
        result_column: Optional[str] = None,
        in_place: bool = False,
        handle_zero_division: str = 'error'
    ) -> "CoreCollectionOperations":
        """列または定数で除算

Args:
    collection: ColumnCollectionオブジェクト
    column1: 除算元の列名
    column2_or_value: 除算する列名または定数値
    result_column: 結果を格納する列名（デフォルトはNone、自動生成）
    in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成
    handle_zero_division: ゼロ除算の処理方法
        "error": ゼロ除算エラーを発生させる
        "none": 結果をNoneとして扱う
        "inf": 結果を無限大（float('inf')）として扱う

Returns:
    ColumnCollection: 演算結果の列を含むColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合
    ValueError: 列の長さが一致しない場合、無効な値が指定された場合、またはゼロ除算が発生した場合"""
        ...
    

    def evaluate(
        self,
        expression: str,
        result_column: Optional[str] = None,
        in_place: bool = False
    ) -> "CoreCollectionOperations":
        """数式文字列を評価し、結果を新しい列に格納します

Args:
    collection: ColumnCollectionオブジェクト
    expression: 評価する数式文字列（例: "price * quantity * (1 - discount)"）
    result_column: 結果を格納する列名（デフォルトはNone、自動生成）
    in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成

Returns:
    ColumnCollection: 演算結果の列を含むColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合
    ValueError: 式の評価中にエラーが発生した場合
    SyntaxError: 式の構文に問題がある場合"""
        ...
    

    def diff(
        self,
        y_column: str,
        x_column: str,
        result_column: Optional[str] = None,
        method: str = 'central',
        in_place: bool = False
    ) -> "CoreCollectionOperations":
        """指定された2つの列間の微分を計算します（dy/dx）。

Args:
    collection: 操作対象のColumnCollection
    y_column: 微分の分子となる列（従属変数）
    x_column: 微分の分母となる列（独立変数）
    result_column: 結果を格納する列名（Noneの場合は自動生成）
    method: 微分方法（"central", "forward", "backward"）
    in_place: 結果を同じコレクションに上書きするか

Returns:
    微分結果を含むColumnCollection

Raises:
    KeyError: 列が存在しない場合
    ValueError: 有効なデータが不足している場合"""
        ...
    

    def integrate(
        self,
        y_column: str,
        x_column: str,
        result_column: Optional[str] = None,
        method: str = 'trapezoid',
        initial_value: float = 0.0,
        in_place: bool = False
    ) -> "CoreCollectionOperations":
        """指定された2つの列間の積分を計算します（∫y dx）。

Args:
    collection: 操作対象のColumnCollection
    y_column: 積分対象の列（被積分関数）
    x_column: 積分の基準となる列（積分変数）
    result_column: 結果を格納する列名（Noneの場合は自動生成）
    method: 積分方法（現在は"trapezoid"のみサポート）
    initial_value: 積分の初期値
    in_place: 結果を同じコレクションに上書きするか

Returns:
    積分結果を含むColumnCollection

Raises:
    KeyError: 列が存在しない場合
    ValueError: 有効なデータが不足している場合、または非サポートの積分方法が指定された場合"""
        ...
    

    def sin(
        self,
        column: str,
        result_column: Optional[str] = None,
        in_place: bool = False,
        degrees: bool = False
    ) -> "CoreCollectionOperations":
        """指定した列の各値にsin関数を適用

Args:
    collection: ColumnCollectionオブジェクト
    column: 処理対象の列名
    result_column: 結果を格納する列名（デフォルトはNone、"sin({column})"が使用される）
    in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成
    degrees: Trueの場合、入力をdegreeとして扱う（デフォルトはFalse、ラジアン）

Returns:
    ColumnCollection: 結果の列を含むColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合"""
        ...
    

    def cos(
        self,
        column: str,
        result_column: Optional[str] = None,
        in_place: bool = False,
        degrees: bool = False
    ) -> "CoreCollectionOperations":
        """指定した列の各値にcos関数を適用

Args:
    collection: ColumnCollectionオブジェクト
    column: 処理対象の列名
    result_column: 結果を格納する列名（デフォルトはNone、"cos({column})"が使用される）
    in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成
    degrees: Trueの場合、入力をdegreeとして扱う（デフォルトはFalse、ラジアン）

Returns:
    ColumnCollection: 結果の列を含むColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合"""
        ...
    

    def tan(
        self,
        column: str,
        result_column: Optional[str] = None,
        in_place: bool = False,
        degrees: bool = False
    ) -> "CoreCollectionOperations":
        """指定した列の各値にtan関数を適用

Args:
    collection: ColumnCollectionオブジェクト
    column: 処理対象の列名
    result_column: 結果を格納する列名（デフォルトはNone、"tan({column})"が使用される）
    in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成
    degrees: Trueの場合、入力をdegreeとして扱う（デフォルトはFalse、ラジアン）

Returns:
    ColumnCollection: 結果の列を含むColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合"""
        ...
    

    def exp(
        self,
        column: str,
        result_column: Optional[str] = None,
        in_place: bool = False
    ) -> "CoreCollectionOperations":
        """指定した列の各値に指数関数(e^x)を適用

Args:
    collection: ColumnCollectionオブジェクト
    column: 処理対象の列名
    result_column: 結果を格納する列名（デフォルトはNone、"exp({column})"が使用される）
    in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成

Returns:
    ColumnCollection: 結果の列を含むColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合"""
        ...
    

    def log(
        self,
        column: str,
        base: float = 2.718281828459045,
        result_column: Optional[str] = None,
        in_place: bool = False
    ) -> "CoreCollectionOperations":
        """指定した列の各値に対数関数を適用

Args:
    collection: ColumnCollectionオブジェクト
    column: 処理対象の列名
    base: 対数の底（デフォルトはe）
    result_column: 結果を格納する列名（デフォルトはNone、"log({column})"または"log{base}({column})"が使用される）
    in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成

Returns:
    ColumnCollection: 結果の列を含むColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合
    ValueError: 0以下の値に対して対数を適用しようとした場合"""
        ...
    

    def sqrt(
        self,
        column: str,
        result_column: Optional[str] = None,
        in_place: bool = False
    ) -> "CoreCollectionOperations":
        """指定した列の各値の平方根を計算

Args:
    collection: ColumnCollectionオブジェクト
    column: 処理対象の列名
    result_column: 結果を格納する列名（デフォルトはNone、"sqrt({column})"が使用される）
    in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成

Returns:
    ColumnCollection: 結果の列を含むColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合
    ValueError: 負の値に対して平方根を適用しようとした場合"""
        ...
    

    def pow(
        self,
        column: str,
        exponent: float,
        result_column: Optional[str] = None,
        in_place: bool = False
    ) -> "CoreCollectionOperations":
        """指定した列の各値を指定した指数でべき乗

Args:
    collection: ColumnCollectionオブジェクト
    column: 処理対象の列名
    exponent: べき指数
    result_column: 結果を格納する列名（デフォルトはNone、"{column}^{exponent}"が使用される）
    in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成

Returns:
    ColumnCollection: 結果の列を含むColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合"""
        ...
    

    def abs_values(
        self,
        column: str,
        result_column: Optional[str] = None,
        in_place: bool = False
    ) -> "CoreCollectionOperations":
        """指定した列の各値の絶対値を計算

Args:
    collection: ColumnCollectionオブジェクト
    column: 処理対象の列名
    result_column: 結果を格納する列名（デフォルトはNone、"abs({column})"が使用される）
    in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成

Returns:
    ColumnCollection: 結果の列を含むColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合"""
        ...
    

    def round_values(
        self,
        column: str,
        decimals: int = 0,
        result_column: Optional[str] = None,
        in_place: bool = False
    ) -> "CoreCollectionOperations":
        """指定した列の各値を指定した小数点以下の桁数に丸める

Args:
    collection: ColumnCollectionオブジェクト
    column: 処理対象の列名
    decimals: 丸める小数点以下の桁数（デフォルトは0、整数）
    result_column: 結果を格納する列名（デフォルトはNone、"round({column}, {decimals})"が使用される）
    in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成

Returns:
    ColumnCollection: 結果の列を含むColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合"""
        ...
    

    def normalize(
        self,
        column: str,
        result_column: Optional[str] = None,
        in_place: bool = False,
        method: str = 'minmax'
    ) -> "CoreCollectionOperations":
        """指定した列の値を正規化

Args:
    collection: ColumnCollectionオブジェクト
    column: 処理対象の列名
    result_column: 結果を格納する列名（デフォルトはNone、"norm_{method}({column})"が使用される）
    in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成
    method: 正規化方法
        "minmax": [0, 1]の範囲に正規化
        "zscore": 平均0、標準偏差1に正規化

Returns:
    ColumnCollection: 結果の列を含むColumnCollection

Raises:
    KeyError: 指定された列名が存在しない場合
    ValueError: 不正なmethod値が指定された場合、または値が一定で正規化できない場合"""
        ...
    

    def interpolate(
        self,
        base_column_name: str = 'step',
        x_values: Optional[list[float]] = None,
        point_count: Optional[int] = None,
        method: str = 'linear',
        columns: Optional[list[str]] = None
    ) -> "CoreCollectionOperations":
        """指定した列の値に基づいてデータを内挿

Args:
    collection: 内挿を行うColumnCollectionオブジェクト
    base_column_name: 内挿の基準となる列名 (デフォルト: "step")
    x_values: 内挿する目標値のリスト 
    point_count: 等間隔内挿を行う場合のポイント数
    method: 内挿方法 (現在は'linear'のみサポート)
    columns: 値の計算に使用する列名リスト (Noneの場合はすべての数値型列)
    
Returns:
    ColumnCollection: 内挿された新しいColumnCollection
    
Raises:
    ValueError: x_valuesとpoint_countの両方が指定された場合、または両方が指定されていない場合
    KeyError: 指定された列が存在しない場合
    TypeError: 指定された列が数値型でない場合
    
Examples:
    # ステップ値に基づいて内挿
    >>> result = collection.ops.interpolate(point_count=100)
    
    # 特定のステップ値で内挿
    >>> result = collection.ops.interpolate(x_values=[1.0, 2.5, 3.0, 4.5])
    
    # position列の値に基づいて内挿
    >>> result = collection.ops.interpolate(
    ...     base_column_name="position", point_count=100
    ... )"""
        ...
    

    def split_by_integers(
        self,
        markers: list[int]
    ) -> "CoreCollectionOperations":
        """整数リストの値でデータを分割します。同じマーカー値を持つデータは同じグループに集約されます。

Args:
    collection: 分割するColumnCollectionオブジェクト
    markers: 各データ値がどのグループに属するかを示す整数リスト（データと同じ長さ）

Returns:
    分割後のColumnCollectionオブジェクトのリスト。各ColumnCollectionは同じマーカー値を持つ
    データで構成され、マーカー値に基づいて昇順に並べられます。

Raises:
    ValueError: データとマーカーの長さが一致しない場合

Examples:
    # データ値を3つのグループに分類
    markers = [2, 1, 2, 3, 1, 3]  # マーカー値が示す分類グループ
    collection_groups = split_by_integers(collection, markers)
    # 結果: [グループ1のCollection, グループ2のCollection, グループ3のCollection]"""
        ...
    

    def moving_average(
        self,
        column: str,
        window_size: int = 3,
        result_column: Optional[str] = None,
        edge_handling: str = 'asymmetric',
        in_place: bool = False
    ) -> "CoreCollectionOperations":
        """指定した列に対して移動平均を計算します。

Args:
    collection: 処理対象のColumnCollection
    column: 処理対象の列名
    window_size: 移動平均のウィンドウサイズ（奇数推奨）
    result_column: 結果を格納する列名（指定がない場合は自動生成）
    edge_handling: エッジ処理方法 ("symmetric", "asymmetric")
    in_place: True の場合、結果を元の列に上書き

Returns:
    ColumnCollection: 移動平均が計算された列を含むコレクション"""
        ...
    

    def detect_outliers(
        self,
        column: str,
        window_size: int = 3,
        threshold: float = 0.5,
        edge_handling: str = 'asymmetric',
        min_abs_value: float = 1e-10,
        scale_factor: float = 1.0,
        result_column: Optional[str] = None
    ) -> "CoreCollectionOperations":
        """移動平均との差分比率を用いた異常値検出を行います。

Args:
    collection: 処理対象のColumnCollection
    column: 処理対象の列名
    window_size: 移動平均のウィンドウサイズ（奇数推奨）
    threshold: 異常値とみなす移動平均との差分比率の閾値
    edge_handling: エッジ処理方法 ("symmetric", "asymmetric")
    min_abs_value: 比率計算時の最小絶対値
    scale_factor: スケール調整係数
    result_column: 結果を格納する列名（指定がない場合は自動生成）

Returns:
    ColumnCollection: 異常値フラグ列を含むコレクション（1=異常値、0=正常値）"""
        ...
    
