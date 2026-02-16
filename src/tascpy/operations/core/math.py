from typing import Union, Optional, List, Dict, Any, Set
from ...core.collection import ColumnCollection
from ...core.column import Column, NumberColumn, detect_column_type
from ..registry import operation
from ..abstraction import (
    transform_column, 
    handle_zero_division,
    store_result,
    handle_missing_values,
    inject_columns
)
import re
import ast
import math
import numpy as np
from ...functional import arithmetic
from ..registry import operation, register_functional


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


add = register_functional(
    arithmetic.add,
    domain="core",
    name="add",
    transform_column={"num_inputs": 2, "result_naming": _safe_add_naming},
)

subtract = register_functional(
    arithmetic.subtract,
    domain="core",
    name="subtract",
    transform_column={"num_inputs": 2, "result_naming": _safe_sub_naming},
)

multiply = register_functional(
    arithmetic.multiply,
    domain="core",
    name="multiply",
    transform_column={"num_inputs": 2, "result_naming": _safe_mul_naming},
)

divide = register_functional(
    arithmetic.divide,
    domain="core",
    name="divide",
    transform_column={"num_inputs": 2, "result_naming": _safe_div_naming},
    extra_decorators=[handle_zero_division(numerator_idx=0, denominator_idx=1)]
)

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


diff = register_functional(
    arithmetic.diff,
    domain="core",
    name="diff",
    store_result={"result_naming": _diff_naming, "unit_inference": _diff_unit_inference},
    inject_columns={"num_inputs": 2},
    extra_decorators=[handle_missing_values(strategy="strict")],
    signature_override={
        "y": ("y_values", np.ndarray),
        "x": ("x_values", np.ndarray),
        "method": (str, "central")
    }
)


integrate = register_functional(
    arithmetic.integrate,
    domain="core",
    name="integrate",
    store_result={"result_naming": _integrate_naming, "unit_inference": _integrate_unit_inference},
    inject_columns={"num_inputs": 2},
    extra_decorators=[handle_missing_values(strategy="strict")],
    signature_override={
        "y": ("y_values", np.ndarray),
        "x": ("x_values", np.ndarray),
        "method": (str, "trapezoid"),
        "initial_value": (float, 0.0)
    }
)


def _evaluate_naming(func_name, expression, *args, **kwargs):
    return f"expression_result"

def _evaluate_unit_inference(collection, expression, **kwargs):
    try:
        # AST parsing to find variable names (simplified version of what's in evaluate)
        parsed_ast = ast.parse(expression, mode="eval")
        for node in ast.walk(parsed_ast):
            if isinstance(node, ast.Name) and node.id not in {
                "sin", "cos", "tan", "exp", "log", "sqrt", "abs", 
                "max", "min", "pow", "round", "pi", "e"
            }:
                if node.id in collection.columns:
                    return getattr(collection[node.id], "unit", None)
    except:
        pass
    return None

@operation(domain="core")
@store_result(
    result_naming=_evaluate_naming,
    unit_inference=_evaluate_unit_inference
)
def evaluate(
    collection: ColumnCollection,
    expression: str,
    *,
    result_column: Optional[str] = None,
    in_place: bool = False,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
) -> Union[List[Optional[float]], np.ndarray]:
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
        SyntaxError: 式の構文に問題がある場合
    """
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
        return result_values
        
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
            
            return result_values

        except Exception as e:
             raise ValueError(f"式の評価中にエラーが発生しました: {str(e)}")
