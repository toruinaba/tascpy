from typing import Union, Optional, List, Dict, Any, Set
import ast
import math
import numpy as np

from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column, NumberColumn, detect_column_type

from ..error_handling import handle_operation_errors
from ..abstraction import (
    handle_zero_division,
    store_result,
    handle_missing_values,
    inject_columns
)
from ...functional.core import math as functional_math
from ..registry import operation
from ..naming import infix_naming, format_naming, basic_naming, log_naming


# ──────────────────────────────────────────────
# 四則演算
# ──────────────────────────────────────────────

@operation(domain="core")
@handle_operation_errors
@store_result(result_naming=infix_naming("+"))
@inject_columns(num_inputs=2, pass_collection=True)
@handle_missing_values(strategy="nan")
def add(
    collection: ColumnCollection,
    value1: Union[str, float, np.ndarray],
    value2: Union[str, float, np.ndarray],
    result_column: Optional[str] = None,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
    in_place: bool = False
) -> ColumnCollection:
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
        >>> col = col.ops.add("CH01", 10.5)
    """
    return functional_math.add(value1, value2)


@operation(domain="core")
@handle_operation_errors
@store_result(result_naming=infix_naming("-"))
@inject_columns(num_inputs=2, pass_collection=True)
@handle_missing_values(strategy="nan")
def subtract(
    collection: ColumnCollection,
    value1: Union[str, float, np.ndarray],
    value2: Union[str, float, np.ndarray],
    result_column: Optional[str] = None,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
    in_place: bool = False
) -> ColumnCollection:
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
        >>> col = col.ops.subtract("CH01", 10.5)
    """
    return functional_math.subtract(value1, value2)


@operation(domain="core")
@handle_operation_errors
@store_result(result_naming=infix_naming("*"))
@inject_columns(num_inputs=2, pass_collection=True)
@handle_missing_values(strategy="nan")
def multiply(
    collection: ColumnCollection,
    value1: Union[str, float, np.ndarray],
    value2: Union[str, float, np.ndarray],
    result_column: Optional[str] = None,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
    in_place: bool = False
) -> ColumnCollection:
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
        >>> col = col.ops.multiply("CH01", 2.0)
    """
    return functional_math.multiply(value1, value2)


@operation(domain="core")
@handle_operation_errors
@store_result(result_naming=infix_naming("/"))
@inject_columns(num_inputs=2, pass_collection=True)
@handle_zero_division(numerator_idx=0, denominator_idx=1)
@handle_missing_values(strategy="nan")
def divide(
    collection: ColumnCollection,
    value1: Union[str, float, np.ndarray],
    value2: Union[str, float, np.ndarray],
    result_column: Optional[str] = None,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
    in_place: bool = False
) -> ColumnCollection:
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
        >>> col = col.ops.divide("荷重", 1000)
    """
    return functional_math.divide(value1, value2)


# ──────────────────────────────────────────────
# 微分・積分
# ──────────────────────────────────────────────

def _diff_unit_inference(collection, y_column, x_column, **kwargs):
    y_obj = collection[y_column] if isinstance(y_column, str) and y_column in collection.columns else None
    x_obj = collection[x_column] if isinstance(x_column, str) and x_column in collection.columns else None
    y_unit = getattr(y_obj, "unit", "") or ""
    x_unit = getattr(x_obj, "unit", "") or ""
    return f"{y_unit}/{x_unit}" if y_unit or x_unit else None


def _integrate_unit_inference(collection, y_column, x_column, **kwargs):
    y_obj = collection[y_column] if isinstance(y_column, str) and y_column in collection.columns else None
    x_obj = collection[x_column] if isinstance(x_column, str) and x_column in collection.columns else None
    y_unit = getattr(y_obj, "unit", "") or ""
    x_unit = getattr(x_obj, "unit", "") or ""
    return f"{y_unit}·{x_unit}" if y_unit or x_unit else None


@operation(domain="core")
@handle_operation_errors
@store_result(result_naming=format_naming("d({0})/d({1})"), unit_inference=_diff_unit_inference)
@inject_columns(num_inputs=2, pass_collection=True)
@handle_missing_values(strategy="strict")
def diff(
    collection: ColumnCollection,
    y_column: Union[str, np.ndarray],
    x_column: Union[str, np.ndarray],
    method: str = "central",
    result_column: Optional[str] = None,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
    in_place: bool = False
) -> ColumnCollection:
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
        >>> result = col.ops.diff("変位", "__step__", method="central")
    """
    return functional_math.diff(y=y_column, x=x_column, method=method)


@operation(domain="core")
@handle_operation_errors
@store_result(result_naming=format_naming("∫{0}·d{1}"), unit_inference=_integrate_unit_inference)
@inject_columns(num_inputs=2, pass_collection=True)
@handle_missing_values(strategy="strict")
def integrate(
    collection: ColumnCollection,
    y_column: Union[str, np.ndarray],
    x_column: Union[str, np.ndarray],
    method: str = "trapezoid",
    initial_value: float = 0.0,
    result_column: Optional[str] = None,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
    in_place: bool = False
) -> ColumnCollection:
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
        >>> result = col.ops.integrate("速度", "__step__")
    """
    return functional_math.integrate(y=y_column, x=x_column, method=method, initial_value=initial_value)


# ──────────────────────────────────────────────
# 数式評価
# ──────────────────────────────────────────────

def _evaluate_unit_inference(collection, expression, **kwargs):
    try:
        parsed_ast = ast.parse(expression, mode="eval")
        for node in ast.walk(parsed_ast):
            if isinstance(node, ast.Name) and node.id not in {
                "sin", "cos", "tan", "exp", "log", "sqrt", "abs",
                "max", "min", "pow", "round", "pi", "e"
            }:
                if node.id in collection.columns:
                    return getattr(collection[node.id], "unit", None)
    except Exception:
        pass
    return None


@operation(domain="core")
@handle_operation_errors
@store_result(result_naming="expression_result", unit_inference=_evaluate_unit_inference)
def evaluate(
    collection: ColumnCollection,
    expression: str,
    result_column: Optional[str] = None,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
    in_place: bool = False
) -> ColumnCollection:
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
        >>> result = col.ops.evaluate("荷重 * 2.0 + 10.0")
    """
    data_map = {name: col.values for name, col in collection.columns.items()}
    return functional_math.evaluate_expression(data_map, expression)


# ──────────────────────────────────────────────
# 単項変換操作
# ──────────────────────────────────────────────

@operation(domain="core")
@handle_operation_errors
@store_result(result_naming=log_naming)
@inject_columns(num_inputs=1, pass_collection=True)
@handle_missing_values(strategy="nan")
def log(
    collection: ColumnCollection,
    values: Union[str, np.ndarray],
    base: float = math.e,
    result_column: Optional[str] = None,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
    in_place: bool = False
) -> ColumnCollection:
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
        >>> result = col.ops.log("CH1", base=10.0)
    """
    return functional_math.log(values=values, base=base)


@operation(domain="core")
@handle_operation_errors
@store_result(result_naming=basic_naming)
@inject_columns(num_inputs=1, pass_collection=True)
@handle_missing_values(strategy="nan")
def sqrt(
    collection: ColumnCollection,
    values: Union[str, np.ndarray],
    result_column: Optional[str] = None,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
    in_place: bool = False
) -> ColumnCollection:
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
        >>> result = col.ops.sqrt("CH1")
    """
    return functional_math.sqrt(values=values)


@operation(domain="core")
@handle_operation_errors
@store_result(result_naming=format_naming("{0}^{exponent}", defaults={"exponent": 1.0}, arg_names=["values", "exponent"]))
@inject_columns(num_inputs=1, pass_collection=True)
@handle_missing_values(strategy="nan")
def pow(
    collection: ColumnCollection,
    values: Union[str, np.ndarray],
    exponent: float = 1.0,
    result_column: Optional[str] = None,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
    in_place: bool = False
) -> ColumnCollection:
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
        >>> result = col.ops.pow("CH1", exponent=2.0)
    """
    return functional_math.power(values=values, exponent=exponent)


@operation(domain="core")
@handle_operation_errors
@store_result(result_naming=format_naming("abs({0})"))
@inject_columns(num_inputs=1, pass_collection=True)
@handle_missing_values(strategy="nan")
def abs_values(
    collection: ColumnCollection,
    values: Union[str, np.ndarray],
    result_column: Optional[str] = None,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
    in_place: bool = False
) -> ColumnCollection:
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
        >>> result = col.ops.abs_values("変位")
    """
    return functional_math.abs_values(values=values)

abs = abs_values


@operation(domain="core")
@handle_operation_errors
@store_result(result_naming=format_naming("round({0}, {decimals})", defaults={"decimals": 0}))
@inject_columns(num_inputs=1, pass_collection=True)
@handle_missing_values(strategy="nan")
def round_values(
    collection: ColumnCollection,
    values: Union[str, np.ndarray],
    decimals: int = 0,
    result_column: Optional[str] = None,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
    in_place: bool = False
) -> ColumnCollection:
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
        >>> result = col.ops.round_values("荷重", decimals=2)
    """
    return functional_math.round_values(values=values, decimals=decimals)


@operation(domain="core")
@handle_operation_errors
@store_result(result_naming=format_naming("norm_{method}({0})", defaults={"method": "minmax"}))
@inject_columns(num_inputs=1, pass_collection=True)
@handle_missing_values(strategy="nan")
def normalize(
    collection: ColumnCollection,
    values: Union[str, np.ndarray],
    method: str = "minmax",
    result_column: Optional[str] = None,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
    in_place: bool = False
) -> ColumnCollection:
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
        >>> result = col.ops.normalize("荷重", method="minmax")
    """
    return functional_math.normalize(values=values, method=method)


# ──────────────────────────────────────────────
# 集計操作
# ──────────────────────────────────────────────

@operation(domain="core")
@handle_operation_errors
@store_result(result_naming=basic_naming("average_across"))
@inject_columns(num_inputs=-1, cast_to_numpy=True, pass_collection=True)
@handle_missing_values(strategy="nan")
def average_across(
    collection: ColumnCollection,
    *columns: str,
    ignore_nan: bool = True,
    result_column: Optional[str] = None,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
    in_place: bool = False
) -> ColumnCollection:
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
        >>> result = col.ops.average_across("センサ1", "センサ2", "センサ3", result_column="平均値")
    """
    return functional_math.average_across(*columns, ignore_nan=ignore_nan)
