from typing import Union, Optional, List, Dict, Any, Set
from ...core.collection import ColumnCollection
from ...core.column import Column, NumberColumn, detect_column_type
from ..registry import operation
from ..abstraction import transform_column, handle_zero_division
import re
import ast
import math
import numpy as np


def _safe_add_naming(func_name, col1, col2, **kwargs):
    return f"{col1}+{col2}"

def _safe_sub_naming(func_name, col1, col2, **kwargs):
    return f"{col1}-{col2}"

def _safe_mul_naming(func_name, col1, col2, **kwargs):
    # Add parentheses if needed for precedence
    c1_str = str(col1)
    if any(op in c1_str for op in ["+", "-"]):
        c1_str = f"({c1_str})"
    return f"{c1_str}*{col2}"

def _safe_div_naming(func_name, col1, col2, **kwargs):
    c1_str = str(col1)
    if any(op in c1_str for op in ["+", "-"]):
        c1_str = f"({c1_str})"
    return f"{c1_str}/{col2}"


@operation(domain="core")
@transform_column(num_inputs=2, result_naming=_safe_add_naming)
def add(
    v1: Union[np.ndarray, float], 
    v2: Union[np.ndarray, float], 
    **kwargs
) -> np.ndarray:
    """列または定数を加算します"""
    return v1 + v2


@operation(domain="core")
@transform_column(num_inputs=2, result_naming=_safe_sub_naming)
def subtract(
    v1: Union[np.ndarray, float], 
    v2: Union[np.ndarray, float], 
    **kwargs
) -> np.ndarray:
    """列または定数を減算します"""
    return v1 - v2


@operation(domain="core")
@transform_column(num_inputs=2, result_naming=_safe_mul_naming)
def multiply(
    v1: Union[np.ndarray, float], 
    v2: Union[np.ndarray, float], 
    **kwargs
) -> np.ndarray:
    """列または定数を乗算します"""
    return v1 * v2


@operation(domain="core")
@transform_column(num_inputs=2, result_naming=_safe_div_naming)
@handle_zero_division(numerator_idx=0, denominator_idx=1)
def divide(
    v1: Union[np.ndarray, float], 
    v2: Union[np.ndarray, float], 
    **kwargs
) -> np.ndarray:
    """列または定数で除算します"""
    return v1 / v2


@operation(domain="core")
def evaluate(
    collection: ColumnCollection,
    expression: str,
    result_column: Optional[str] = None,
    in_place: bool = False,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
) -> ColumnCollection:
    """数式文字列を評価し、結果を新しい列に格納します

    指定された数式を評価し、その結果を新しい列として追加します。
    数式内では各列の値を変数として参照でき、基本的な数学関数も使用できます。

    Args:
        collection: ColumnCollection オブジェクト
        expression: 評価する数式文字列（例: "price * quantity * (1 - discount)"）
        result_column: 結果を格納する列名（デフォルトは None、自動生成）
        in_place: True の場合は元のオブジェクトを変更、False の場合は新しいオブジェクトを作成
        unit: 新しい列の単位（指定しない場合は数式で使用された最初の列から継承）
        ch: 新しい列のチャンネル（指定しない場合はNone）

    Returns:
        ColumnCollection: 演算結果の列を含む ColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
        ValueError: 式の評価中にエラーが発生した場合
        SyntaxError: 式の構文に問題がある場合
    """
    if result_column is None:
        result_column = f"expression_result_{len(collection.columns)}"

    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()

    # ASTを使用して式の構文検証
    try:
        parsed_ast = ast.parse(expression, mode="eval")

        # 安全でない操作や関数呼び出しをチェック
        for node in ast.walk(parsed_ast):
            # 属性アクセス（例：os.system）をブロック
            if isinstance(node, ast.Attribute):
                raise ValueError(
                    f"式に安全でない属性アクセスが含まれています: {expression}"
                )

            # 関数呼び出しが安全かチェック（数学関数以外をブロック）
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                func_name = node.func.id
                safe_funcs = {
                    "sin",
                    "cos",
                    "tan",
                    "exp",
                    "log",
                    "sqrt",
                    "abs",
                    "max",
                    "min",
                    "pow",
                    "round",
                }
                if func_name not in safe_funcs:
                    raise ValueError(
                        f"許可されていない関数が使用されています: {func_name}"
                    )

    except SyntaxError as e:
        line_no = getattr(e, "lineno", "不明")
        col_offset = getattr(e, "offset", "不明")
        raise ValueError(f"式の構文エラー (行:{line_no}, 列:{col_offset}): {str(e)}")

    # 式からカラム名を抽出
    column_names = []
    for node in ast.walk(parsed_ast):
        if isinstance(node, ast.Name) and node.id not in {
            "sin",
            "cos",
            "tan",
            "exp",
            "log",
            "sqrt",
            "abs",
            "max",
            "min",
            "pow",
            "round",
            "pi",
            "e",
        }:
            column_names.append(node.id)

    # 重複を削除し、実際にコレクションに存在するカラム名のみをフィルタリング
    column_names = list(set(col for col in column_names if col in collection.columns))

    # 存在しないカラム名の検出
    all_vars = set()
    for node in ast.walk(parsed_ast):
        if (
            isinstance(node, ast.Name)
            and not isinstance(node.ctx, ast.Param)
            and node.id
            not in {
                "sin",
                "cos",
                "tan",
                "exp",
                "log",
                "sqrt",
                "abs",
                "max",
                "min",
                "pow",
                "round",
                "pi",
                "e",
            }
        ):
            all_vars.add(node.id)

    missing_columns = all_vars - set(collection.columns)
    if missing_columns:
        # 類似したカラム名の提案
        suggestions = {}
        for missing in missing_columns:
            possible_matches = []
            for existing in collection.columns:
                # レーベンシュタイン距離などの類似度チェックをここで実装できますが、簡略化のため部分文字列マッチを使用
                if missing in existing or existing in missing:
                    possible_matches.append(existing)

            if possible_matches:
                suggestions[missing] = possible_matches

        error_msg = (
            f"式に存在しないカラム名が含まれています: {', '.join(missing_columns)}"
        )
        if suggestions:
            error_msg += "\n提案: "
            for missing, candidates in suggestions.items():
                error_msg += f"\n  - {missing}: {', '.join(candidates)} ?"
        
        raise KeyError(error_msg)

    # 評価に使用する変数名のみを抽出
    used_cols = list(all_vars)

    # NumPyによるベクトル化評価を試みる
    try:
        # 名前空間の構築
        namespace = {
            "sin": np.sin,
            "cos": np.cos,
            "tan": np.tan,
            "exp": np.exp,
            "log": np.log,
            "sqrt": np.sqrt,
            "abs": np.abs,
            "max": np.maximum,
            "min": np.minimum,
            "pow": np.power,
            "round": np.round,
            "pi": np.pi,
            "e": np.e,
        }
        
        # データの準備（None -> NaN）
        for col_name in used_cols:
            vals = collection[col_name].values
            if isinstance(vals, np.ndarray) and np.issubdtype(vals.dtype, np.number):
                arr = vals.astype(float)
            else:
                arr = np.array([v if v is not None else np.nan for v in vals], dtype=float)
            namespace[col_name] = arr
            
        # 評価実行
        with np.errstate(all='ignore'):
            res = eval(expression, {"__builtins__": {}}, namespace)
            
        # 結果がNumPy配列でなければ（スカラー等）、配列にブロードキャスト
        if np.isscalar(res):
            res = np.full(len(collection), res)
        elif isinstance(res, np.ndarray):
            pass 
        else:
             raise ValueError("Vectorized evaluation returned non-array")
             
        # 結果をリストに変換 (NaN -> None)
        result_values = [None if np.isnan(v) else v for v in res.tolist()]
        
    except Exception:
        # ベクトル評価に失敗した場合は、従来の行ごとの評価にフォールバック
        try:
            length = len(collection)
            result_values = []
            
            # 数学関数（スカラー用）
            math_funcs = {
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "exp": math.exp,
                "log": math.log,
                "sqrt": math.sqrt,
                "abs": abs,
                "max": max,
                "min": min,
                "pow": math.pow,
                "round": round,
                "pi": math.pi,
                "e": math.e,
            }
    
            # 各行に対して式を評価
            for i in range(length):
                row_data = {}
                is_row_valid = True
                
                # 値の取得とNoneチェック
                for col in used_cols:
                    val = collection.columns[col].values[i]
                    if val is None:
                        is_row_valid = False
                        break
                    row_data[col] = val
                    
                if not is_row_valid:
                     result_values.append(None)
                     continue
    
                eval_namespace = dict(row_data)
                eval_namespace.update(math_funcs)
    
                restricted_globals = {"__builtins__": {}}
                try:
                     row_result = eval(expression, restricted_globals, eval_namespace)
                     result_values.append(row_result)
                except (ValueError, TypeError, ZeroDivisionError):
                     result_values.append(None)

        except Exception as e:
             raise ValueError(f"式の評価中にエラーが発生しました: {str(e)}")

    # 結果を新しい列として追加（既存の列名の場合は上書き）
    if result_column in result.columns:
        result.columns[result_column].values = result_values
        if unit is not None:
             result.columns[result_column].unit = unit
        if ch is not None:
             result.columns[result_column].ch = ch
    else:
        # 元の列の単位を継承（指定がない場合）
        if unit is None:
            unit = None
            for col in used_cols:
                original_column = collection[col]
                if getattr(original_column, "unit", None):
                    unit = original_column.unit
                    break

        # 新しい列を追加
        column = detect_column_type(ch, result_column, unit, result_values)
        result.add_column(result_column, column)

    return result


# 微分と積分の関数を定義

def _diff_naming(func_name, y_col, x_col, **kwargs):
    return f"d({y_col})/d({x_col})"

def _diff_unit_inference(collection, y_col, x_col, **kwargs):
    y_obj = collection[y_col] if isinstance(y_col, str) and y_col in collection.columns else None
    x_obj = collection[x_col] if isinstance(x_col, str) and x_col in collection.columns else None
    
    y_unit = getattr(y_obj, "unit", "") or ""
    x_unit = getattr(x_obj, "unit", "") or ""
    return f"{y_unit}/{x_unit}" if y_unit or x_unit else None

def _integrate_naming(func_name, y_col, x_col, **kwargs):
    return f"∫{y_col}·d{x_col}"

def _integrate_unit_inference(collection, y_col, x_col, **kwargs):
    y_obj = collection[y_col] if isinstance(y_col, str) and y_col in collection.columns else None
    x_obj = collection[x_col] if isinstance(x_col, str) and x_col in collection.columns else None
    
    y_unit = getattr(y_obj, "unit", "") or ""
    x_unit = getattr(x_obj, "unit", "") or ""
    return f"{y_unit}·{x_unit}" if y_unit or x_unit else None


@operation(domain="core")
@transform_column(
    num_inputs=2, 
    result_naming=_diff_naming, 
    unit_inference=_diff_unit_inference
)
def diff(
    y_values: np.ndarray,
    x_values: np.ndarray,
    method: str = "central",
    **kwargs
) -> np.ndarray:
    """指定された 2 つの列間の微分を計算します（dy/dx）"""
    
    # Check for NaNs/None in inputs
    # transform_column converts None to NaN.
    # Logic: if ANY input has NaN, return ALL NaNs (based on original strict logic)
    # Original logic: `if None in y_values or None in x_values: return all None`
    # Here, inputs are float arrays with NaNs.
    
    if np.isnan(y_values).any() or np.isnan(x_values).any():
        return np.full_like(y_values, np.nan)
        
    # Check data points
    if len(x_values) < 2:
        raise ValueError(
            f"有効なデータポイントが不足しています: {len(x_values)} (最低2点必要)"
        )

    from ...utils.data import diff_xy
    # diff_xy returns list, we convert to array
    # diff_xy expects x, y as lists or arrays.
    res_list = diff_xy(x_values, y_values, method=method)
    return np.array(res_list)


@operation(domain="core")
@transform_column(
    num_inputs=2, 
    result_naming=_integrate_naming, 
    unit_inference=_integrate_unit_inference
)
def integrate(
    y_values: np.ndarray,
    x_values: np.ndarray,
    method: str = "trapezoid",
    initial_value: float = 0.0,
    **kwargs
) -> np.ndarray:
    """指定された 2 つの列間の積分を計算します（∫y dx）"""
    
    # メソッドの検証
    if method != "trapezoid":
        raise ValueError("現在は trapezoid 積分のみサポートしています")

    # None logic from original:
    # "None値を含む場合、最初の値だけ計算し、残りはNoneとする仕様を再現"
    has_nan = np.isnan(y_values).any() or np.isnan(x_values).any()
    
    if has_nan:
        # Check first point validity
        result = np.full_like(x_values, np.nan)
        if not np.isnan(y_values[0]) and not np.isnan(x_values[0]):
             # Original logic: result[0] = initial_value + x[0]*y[0]
             # Note: integrate_xy original implementation logic check
             # lines 333-336 in data.py
             dx = x_values[0]
             first_step = dx * y_values[0]
             result[0] = initial_value + first_step
        return result

    if len(x_values) < 2:
         raise ValueError(
            f"有効なデータポイントが不足しています: {len(x_values)} (最低2点必要)"
        )

    # Sort logic (Integrate depends on order)
    # integrate_xy inside utils/data.py DOES SORTING internally?
    # No, integrate_xy in data.py DOES NOT sort. 
    # Wait, checking data.py viewed earlier.
    # data.py:310 integration_xy
    # It does NOT sort.
    # math.py:518 sorted_pairs = sorted(zip(valid_x, valid_y))
    # So math.py was doing the sorting.
    
    # We must sort here.
    sorted_indices = np.argsort(x_values)
    sorted_x = x_values[sorted_indices]
    sorted_y = y_values[sorted_indices]
    
    from ...utils.data import integrate_xy
    integral_values = integrate_xy(sorted_x, sorted_y, initial_value=initial_value)
    integral_arr = np.array(integral_values)
    
    # Map back to original order
    # We need to unsort.
    # The result `integral_arr` corresponds to `sorted_x`.
    # We want result corresponding to `x_values`.
    # result[sorted_indices] = integral_arr
    
    result = np.empty_like(integral_arr)
    result[sorted_indices] = integral_arr
    
    return result
