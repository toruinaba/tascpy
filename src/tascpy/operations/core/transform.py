import math
import numpy as np
from typing import Union, Optional, List, Dict, Any
from ...core.collection import ColumnCollection
from ...core.column import Column, detect_column_type
from ..registry import operation


# 三角関数
@operation(domain="core")
def sin(
    collection: ColumnCollection,
    column: str,
    result_column: Optional[str] = None,
    in_place: bool = False,
    degrees: bool = False,
) -> ColumnCollection:
    """指定した列の各値に sin 関数を適用します

    指定された列の値に対して三角関数の sin を計算し、新しい列に結果を格納します。
    角度の入力形式としてラジアンまたは度を選択できます。

    Args:
        collection: ColumnCollection オブジェクト
        column: 処理対象の列名
        result_column: 結果を格納する列名（None の場合は "sin({column})" を使用）
        in_place: True の場合は元のオブジェクトを変更、False の場合は新しいオブジェクトを作成
        degrees: True の場合、入力を degree として扱う（デフォルトは False、ラジアン）

    Returns:
        ColumnCollection: 結果の列を含む ColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
    """
    # 列の存在チェック
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")

    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()

    # 列の値を取得
    values = collection[column].values

    # 結果の列名を決定
    if result_column is None:
        result_column = f"sin({column})"

    # sin関数適用
    # NumPyを使用して高速化 (None対応)
    if isinstance(values, np.ndarray) and np.issubdtype(values.dtype, np.number):
        values_arr = values.astype(float)
    else:
        values_arr = np.array([v if v is not None else np.nan for v in values], dtype=float)
    
    if degrees:
        values_arr = np.radians(values_arr)
        
    res_arr = np.sin(values_arr)
    
    # 結果をリストに戻す (NaN -> None)
    result_values = [None if np.isnan(v) else v for v in res_arr]

    # 結果を新しい列として追加（既存の列名の場合は上書き）
    if result_column in result.columns:
        result.columns[result_column].values = result_values
    else:
        # 新しい列を追加
        # 元の列から単位などの情報を継承
        source_column = collection[column]
        column_type = detect_column_type(
            getattr(source_column, "ch", None),
            result_column,
            getattr(source_column, "unit", None),
            result_values,
        )
        result.add_column(result_column, column_type)

    return result


@operation(domain="core")
def cos(
    collection: ColumnCollection,
    column: str,
    result_column: Optional[str] = None,
    in_place: bool = False,
    degrees: bool = False,
) -> ColumnCollection:
    """指定した列の各値に cos 関数を適用します

    指定された列の値に対して三角関数の cos を計算し、新しい列に結果を格納します。
    角度の入力形式としてラジアンまたは度を選択できます。

    Args:
        collection: ColumnCollection オブジェクト
        column: 処理対象の列名
        result_column: 結果を格納する列名（None の場合は "cos({column})" を使用）
        in_place: True の場合は元のオブジェクトを変更、False の場合は新しいオブジェクトを作成
        degrees: True の場合、入力を degree として扱う（デフォルトは False、ラジアン）

    Returns:
        ColumnCollection: 結果の列を含む ColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
    """
    # 列の存在チェック
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")

    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()

    # 列の値を取得
    values = collection[column].values

    # 結果の列名を決定
    if result_column is None:
        result_column = f"cos({column})"

    # cos関数適用
    # NumPyを使用して高速化 (None対応)
    if isinstance(values, np.ndarray) and np.issubdtype(values.dtype, np.number):
        values_arr = values.astype(float)
    else:
        values_arr = np.array([v if v is not None else np.nan for v in values], dtype=float)
    
    if degrees:
        values_arr = np.radians(values_arr)
        
    res_arr = np.cos(values_arr)
    
    # 結果をリストに戻す (NaN -> None)
    result_values = [None if np.isnan(v) else v for v in res_arr]

    # 結果を新しい列として追加（既存の列名の場合は上書き）
    if result_column in result.columns:
        result.columns[result_column].values = result_values
    else:
        # 新しい列を追加
        # 元の列から単位などの情報を継承
        source_column = collection[column]
        column_type = detect_column_type(
            getattr(source_column, "ch", None),
            result_column,
            getattr(source_column, "unit", None),
            result_values,
        )
        result.add_column(result_column, column_type)

    return result


@operation(domain="core")
def tan(
    collection: ColumnCollection,
    column: str,
    result_column: Optional[str] = None,
    in_place: bool = False,
    degrees: bool = False,
) -> ColumnCollection:
    """指定した列の各値に tan 関数を適用します

    指定された列の値に対して三角関数の tan を計算し、新しい列に結果を格納します。
    角度の入力形式としてラジアンまたは度を選択できます。

    Args:
        collection: ColumnCollection オブジェクト
        column: 処理対象の列名
        result_column: 結果を格納する列名（None の場合は "tan({column})" を使用）
        in_place: True の場合は元のオブジェクトを変更、False の場合は新しいオブジェクトを作成
        degrees: True の場合、入力を degree として扱う（デフォルトは False、ラジアン）

    Returns:
        ColumnCollection: 結果の列を含む ColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
    """
    # 列の存在チェック
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")

    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()

    # 列の値を取得
    values = collection[column].values

    # 結果の列名を決定
    if result_column is None:
        result_column = f"tan({column})"

    # tan関数適用
    # NumPyを使用して高速化 (None対応)
    if isinstance(values, np.ndarray) and np.issubdtype(values.dtype, np.number):
        values_arr = values.astype(float)
    else:
        values_arr = np.array([v if v is not None else np.nan for v in values], dtype=float)
    
    if degrees:
        values_arr = np.radians(values_arr)
        
    res_arr = np.tan(values_arr)
    
    # 結果をリストに戻す (NaN -> None)
    result_values = [None if np.isnan(v) else v for v in res_arr]

    # 結果を新しい列として追加（既存の列名の場合は上書き）
    if result_column in result.columns:
        result.columns[result_column].values = result_values
    else:
        # 新しい列を追加
        # 元の列から単位などの情報を継承
        source_column = collection[column]
        column_type = detect_column_type(
            getattr(source_column, "ch", None),
            result_column,
            getattr(source_column, "unit", None),
            result_values,
        )
        result.add_column(result_column, column_type)

    return result


# 指数関数/対数関数
@operation(domain="core")
def exp(
    collection: ColumnCollection,
    column: str,
    result_column: Optional[str] = None,
    in_place: bool = False,
) -> ColumnCollection:
    """指定した列の各値に指数関数(e^x)を適用します

    指定された列の各値に対して自然指数関数 e^x を計算し、結果を新しい列に格納します。
    入力データが None の場合は結果も None になります。

    Args:
        collection: ColumnCollection オブジェクト
        column: 処理対象の列名
        result_column: 結果を格納する列名（None の場合は "exp({column})" を使用）
        in_place: True の場合は元のオブジェクトを変更、False の場合は新しいオブジェクトを作成

    Returns:
        ColumnCollection: 結果の列を含む ColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
    """
    # 列の存在チェック
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")

    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()

    # 列の値を取得
    values = collection[column].values

    # 結果の列名を決定
    if result_column is None:
        result_column = f"exp({column})"

    # 指数関数適用
    # 指数関数適用
    if isinstance(values, np.ndarray) and np.issubdtype(values.dtype, np.number):
        values_arr = values.astype(float)
    else:
        values_arr = np.array([v if v is not None else np.nan for v in values], dtype=float)
    res_arr = np.exp(values_arr)
    result_values = [None if np.isnan(v) else v for v in res_arr]

    # 結果を新しい列として追加（既存の列名の場合は上書き）
    if result_column in result.columns:
        result.columns[result_column].values = result_values
    else:
        # 新しい列を追加
        # 元の列から単位などの情報を継承
        source_column = collection[column]
        column_type = detect_column_type(
            getattr(source_column, "ch", None),
            result_column,
            getattr(source_column, "unit", None),
            result_values,
        )
        result.add_column(result_column, column_type)

    return result


@operation(domain="core")
def log(
    collection: ColumnCollection,
    column: str,
    base: float = math.e,
    result_column: Optional[str] = None,
    in_place: bool = False,
) -> ColumnCollection:
    """指定した列の各値に対数関数を適用します

    指定された列の各値に対して対数関数を計算し、結果を新しい列に格納します。
    対数の底を指定できるほか、自然対数（底が e）やログ 10 なども計算できます。

    Args:
        collection: ColumnCollection オブジェクト
        column: 処理対象の列名
        base: 対数の底（デフォルトは e）
        result_column: 結果を格納する列名（None の場合は "log({column})" または "log{base}({column})" を使用）
        in_place: True の場合は元のオブジェクトを変更、False の場合は新しいオブジェクトを作成

    Returns:
        ColumnCollection: 結果の列を含む ColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
        ValueError: 0 以下の値に対して対数を適用しようとした場合
    """
    # 列の存在チェック
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")

    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()

    # 列の値を取得
    values = collection[column].values

    # 結果の列名を決定
    if result_column is None:
        if base == math.e:
            result_column = f"log({column})"
        elif base == 10:
            result_column = f"log10({column})"
        else:
            result_column = f"log{base}({column})"

    # 対数関数適用
    # 対数関数適用
    if isinstance(values, np.ndarray) and np.issubdtype(values.dtype, np.number):
        values_arr = values.astype(float)
    else:
        values_arr = np.array([v if v is not None else np.nan for v in values], dtype=float)
    
    # 0以下はNoneにする (元の挙動に合わせる)
    # np.logは0で-inf, 負でnanになるが、ここでは明示的にnanにしておく
    # Warning抑制
    with np.errstate(divide='ignore', invalid='ignore'):
        # まずは計算
        if base == math.e:
            res_arr = np.log(values_arr)
        elif base == 10:
            res_arr = np.log10(values_arr)
        else:
            res_arr = np.log(values_arr) / np.log(base)
            
    # 元の値が0以下だった場所をNaNにする (結果が-infやnanになっている場所)
    # 正確には values <= 0 の場所をNaNにする
    # NaNとの比較はFalseになるので注意
    mask_le_zero = (values_arr <= 0)
    # mask_le_zeroの中でTrueの場所をNaNにする
    # ただしvalues_arr自体にNaNが含まれている場合、比較でWarningが出る可能性があるが上で抑制済み
    
    res_arr[mask_le_zero] = np.nan
    
    result_values = [None if np.isnan(v) else v for v in res_arr]

    # 結果を新しい列として追加（既存の列名の場合は上書き）
    if result_column in result.columns:
        result.columns[result_column].values = result_values
    else:
        # 新しい列を追加
        # 元の列から単位などの情報を継承
        source_column = collection[column]
        column_type = detect_column_type(
            getattr(source_column, "ch", None),
            result_column,
            getattr(source_column, "unit", None),
            result_values,
        )
        result.add_column(result_column, column_type)

    return result


@operation(domain="core")
def sqrt(
    collection: ColumnCollection,
    column: str,
    result_column: Optional[str] = None,
    in_place: bool = False,
) -> ColumnCollection:
    """指定した列の各値の平方根を計算します

    指定された列の各値の平方根を計算し、結果を新しい列に格納します。
    負の値に対しては None が格納されます。

    Args:
        collection: ColumnCollection オブジェクト
        column: 処理対象の列名
        result_column: 結果を格納する列名（None の場合は "sqrt({column})" を使用）
        in_place: True の場合は元のオブジェクトを変更、False の場合は新しいオブジェクトを作成

    Returns:
        ColumnCollection: 結果の列を含む ColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
        ValueError: 負の値に対して平方根を適用しようとした場合
    """
    # 列の存在チェック
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")

    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()

    # 列の値を取得
    values = collection[column].values

    # 結果の列名を決定
    if result_column is None:
        result_column = f"sqrt({column})"

    # 平方根計算
    # 平方根計算
    if isinstance(values, np.ndarray) and np.issubdtype(values.dtype, np.number):
        values_arr = values.astype(float)
    else:
        values_arr = np.array([v if v is not None else np.nan for v in values], dtype=float)
    
    # 負の値はNaNになる (Warning抑制)
    with np.errstate(invalid='ignore'):
         res_arr = np.sqrt(values_arr)
         
    result_values = [None if np.isnan(v) else v for v in res_arr]

    # 結果を新しい列として追加（既存の列名の場合は上書き）
    if result_column in result.columns:
        result.columns[result_column].values = result_values
    else:
        # 新しい列を追加
        # 元の列から単位などの情報を継承
        source_column = collection[column]
        column_type = detect_column_type(
            getattr(source_column, "ch", None),
            result_column,
            getattr(source_column, "unit", None),
            result_values,
        )
        result.add_column(result_column, column_type)

    return result


@operation(domain="core")
def pow(
    collection: ColumnCollection,
    column: str,
    exponent: float,
    result_column: Optional[str] = None,
    in_place: bool = False,
) -> ColumnCollection:
    """指定した列の各値を指定した指数でべき乗します

    指定された列の各値を指定された指数でべき乗し、結果を新しい列に格納します。
    非数値データや計算エラーが発生した場合は None が格納されます。

    Args:
        collection: ColumnCollection オブジェクト
        column: 処理対象の列名
        exponent: べき指数
        result_column: 結果を格納する列名（None の場合は "{column}^{exponent}" を使用）
        in_place: True の場合は元のオブジェクトを変更、False の場合は新しいオブジェクトを作成

    Returns:
        ColumnCollection: 結果の列を含む ColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
    """
    # 列の存在チェック
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")

    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()

    # 列の値を取得
    values = collection[column].values

    # 結果の列名を決定
    if result_column is None:
        result_column = f"{column}^{exponent}"

    # べき乗計算
    # べき乗計算
    if isinstance(values, np.ndarray) and np.issubdtype(values.dtype, np.number):
        values_arr = values.astype(float)
    else:
        values_arr = np.array([v if v is not None else np.nan for v in values], dtype=float)
    
    with np.errstate(invalid='ignore'):
        res_arr = np.power(values_arr, exponent)
        
    result_values = [None if np.isnan(v) else v for v in res_arr]

    # 結果を新しい列として追加（既存の列名の場合は上書き）
    if result_column in result.columns:
        result.columns[result_column].values = result_values
    else:
        # 新しい列を追加
        # 元の列から単位などの情報を継承
        source_column = collection[column]
        column_type = detect_column_type(
            getattr(source_column, "ch", None),
            result_column,
            getattr(source_column, "unit", None),
            result_values,
        )
        result.add_column(result_column, column_type)

    return result


# その他の変換関数
@operation(domain="core")
def abs_values(
    collection: ColumnCollection,
    column: str,
    result_column: Optional[str] = None,
    in_place: bool = False,
) -> ColumnCollection:
    """指定した列の各値の絶対値を計算します

    指定された列の各値の絶対値を計算し、結果を新しい列に格納します。
    None 値は結果でも None として維持されます。

    Args:
        collection: ColumnCollection オブジェクト
        column: 処理対象の列名
        result_column: 結果を格納する列名（None の場合は "abs({column})" を使用）
        in_place: True の場合は元のオブジェクトを変更、False の場合は新しいオブジェクトを作成

    Returns:
        ColumnCollection: 結果の列を含む ColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
    """
    # 列の存在チェック
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")

    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()

    # 列の値を取得
    values = collection[column].values

    # 結果の列名を決定
    if result_column is None:
        result_column = f"abs({column})"

    # 絶対値計算
    # 絶対値計算
    if isinstance(values, np.ndarray) and np.issubdtype(values.dtype, np.number):
        values_arr = values.astype(float)
    else:
        values_arr = np.array([v if v is not None else np.nan for v in values], dtype=float)
    res_arr = np.abs(values_arr)
    result_values = [None if np.isnan(v) else v for v in res_arr]

    # 結果を新しい列として追加（既存の列名の場合は上書き）
    if result_column in result.columns:
        result.columns[result_column].values = result_values
    else:
        # 新しい列を追加
        # 元の列から単位などの情報を継承
        source_column = collection[column]
        column_type = detect_column_type(
            getattr(source_column, "ch", None),
            result_column,
            getattr(source_column, "unit", None),
            result_values,
        )
        result.add_column(result_column, column_type)

    return result


# 組み込みabs関数との競合を避けるためのエイリアス
# オペレーション名として登録するために必要
abs = abs_values


@operation(domain="core")
def round_values(
    collection: ColumnCollection,
    column: str,
    decimals: int = 0,
    result_column: Optional[str] = None,
    in_place: bool = False,
) -> ColumnCollection:
    """指定した列の各値を指定した小数点以下の桁数に丸めます

    指定された列の各値を指定された小数点以下の桁数で四捨五入し、結果を新しい列に格納します。
    None 値は結果でも None として維持されます。

    Args:
        collection: ColumnCollection オブジェクト
        column: 処理対象の列名
        decimals: 丸める小数点以下の桁数（デフォルトは 0、整数）
        result_column: 結果を格納する列名（None の場合は "round({column}, {decimals})" を使用）
        in_place: True の場合は元のオブジェクトを変更、False の場合は新しいオブジェクトを作成

    Returns:
        ColumnCollection: 結果の列を含む ColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
    """
    # 列の存在チェック
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")

    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()

    # 列の値を取得
    values = collection[column].values

    # 結果の列名を決定
    if result_column is None:
        result_column = f"round({column}, {decimals})"

    # 丸め処理
    # 丸め処理
    if isinstance(values, np.ndarray) and np.issubdtype(values.dtype, np.number):
        values_arr = values.astype(float)
    else:
        values_arr = np.array([v if v is not None else np.nan for v in values], dtype=float)
    res_arr = np.round(values_arr, decimals)
    result_values = [None if np.isnan(v) else v for v in res_arr]

    # 結果を新しい列として追加（既存の列名の場合は上書き）
    if result_column in result.columns:
        result.columns[result_column].values = result_values
    else:
        # 新しい列を追加
        # 元の列から単位などの情報を継承
        source_column = collection[column]
        column_type = detect_column_type(
            getattr(source_column, "ch", None),
            result_column,
            getattr(source_column, "unit", None),
            result_values,
        )
        result.add_column(result_column, column_type)

    return result


@operation(domain="core")
def normalize(
    collection: ColumnCollection,
    column: str,
    result_column: Optional[str] = None,
    in_place: bool = False,
    method: str = "minmax",
) -> ColumnCollection:
    """指定した列の値を正規化します

    指定された列の値を指定された方法で正規化します。
    "minmax" 法では [0, 1] の範囲に、"zscore" 法では平均 0、標準偏差 1 に正規化します。

    Args:
        collection: ColumnCollection オブジェクト
        column: 処理対象の列名
        result_column: 結果を格納する列名（None の場合は "norm_{method}({column})" を使用）
        in_place: True の場合は元のオブジェクトを変更、False の場合は新しいオブジェクトを作成
        method: 正規化方法
            "minmax": [0, 1] の範囲に正規化
            "zscore": 平均 0、標準偏差 1 に正規化

    Returns:
        ColumnCollection: 結果の列を含む ColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
        ValueError: 不正な method 値が指定された場合、または値が一定で正規化できない場合
    """
    # methodの検証
    valid_methods = ["minmax", "zscore"]
    if method not in valid_methods:
        raise ValueError(f"methodは{valid_methods}のいずれかを指定してください")

    # 列の存在チェック
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")

    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()

    # 列の値を取得（Noneを除く）
    values = [v for v in collection[column].values if v is not None]

    # 空の列またはすべてNoneの場合
    if not values:
        if result_column is None:
            result_column = f"norm_{method}({column})"

        # すべてNoneの結果を返す
        null_values = [None] * len(collection[column].values)
        if result_column in result.columns:
            result.columns[result_column].values = null_values
        else:
            # 元の列から単位などの情報を継承
            source_column = collection[column]
            column_type = detect_column_type(
                getattr(source_column, "ch", None),
                result_column,
                getattr(source_column, "unit", None),
                null_values,
            )
            result.add_column(result_column, column_type)
        return result

    # 正規化処理
    # values (list without Nones) -> convert to array
    if not values: # Original check: if not values:
         pass # Already handled above
         
    # 全データ（Noneを含む）を配列化
    # 全データ（Noneを含む）を配列化
    all_values = collection[column].values
    if isinstance(all_values, np.ndarray) and np.issubdtype(all_values.dtype, np.number):
        all_arr = all_values.astype(float)
    else:
        all_arr = np.array([v if v is not None else np.nan for v in all_values], dtype=float)

    # 統計量計算にはNaNを除外したデータを使用
    # values変数は既にNone除外済みだが、リストなので配列にする
    valid_arr = np.array(values, dtype=float)
    
    result_arr = np.full(len(all_arr), np.nan)

    if method == "minmax":
        min_val = np.min(valid_arr)
        max_val = np.max(valid_arr)

        if max_val == min_val:
            # すべて0.5に設定 (NaN以外)
            result_arr[~np.isnan(all_arr)] = 0.5
        else:
            result_arr = (all_arr - min_val) / (max_val - min_val)

        # 結果列名
        if result_column is None:
            result_column = f"norm_minmax({column})"

    elif method == "zscore":
        mean = np.mean(valid_arr)
        variance = np.var(valid_arr) # デフォルトはddof=0 (母分散) -> match original logic (sum((x-mean)**2)/len)
        
        if variance < 1e-10:
             result_arr[~np.isnan(all_arr)] = 0.0
        else:
             std_dev = np.sqrt(variance)
             result_arr = (all_arr - mean) / std_dev

        # 結果列名
        if result_column is None:
            result_column = f"norm_zscore({column})"
            
    result_values = [None if np.isnan(v) else v for v in result_arr]

    # 結果を新しい列として追加（既存の列名の場合は上書き）
    if result_column in result.columns:
        result.columns[result_column].values = result_values
    else:
        # 新しい列を追加
        # 元の列から単位などの情報を継承
        source_column = collection[column]
        column_type = detect_column_type(
            getattr(source_column, "ch", None),
            result_column,
            getattr(source_column, "unit", None),
            result_values,
        )
        result.add_column(result_column, column_type)

    return result
