from typing import Union, Optional, List, Dict, Any, Set
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column, NumberColumn, detect_column_type
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
import inspect
import numpy as np
from ...functional import math as functional_math
from ..registry import operation, register_functional
from ..naming import infix_naming, format_naming, basic_naming, log_naming


add = register_functional(
    functional_math.add,
    domain="core",
    name="add",
    transform_column={"num_inputs": 2, "result_naming": infix_naming("+")},
)
add.__doc__ = """複数カラムまたはスカラー値の要素ごとの和を計算します。

    Args:
        collection (ColumnCollection): データコレクション
        value1 (Union[str, float]): 第1引数（カラム名または数値）
        value2 (Union[str, float]): 第2引数（カラム名または数値）
        
    Returns:
        ColumnCollection: 計算結果カラムが追加された新しいコレクション
        
    Examples:
        >>> col = col.ops.add("CH01", "CH02")      # CH01 + CH02 -> 新しい列に追加
        >>> col = col.ops.add("CH01", 10.5)        # CH01に10.5を加算
"""

subtract = register_functional(
    functional_math.subtract,
    domain="core",
    name="subtract",
    transform_column={"num_inputs": 2, "result_naming": infix_naming("-")},
)
subtract.__doc__ = """第一引数から第二引数の要素ごとの差を計算します。

    Args:
        collection (ColumnCollection): データコレクション
        value1 (Union[str, float]): 第1引数（カラム名または数値）
        value2 (Union[str, float]): 第2引数（引き算するカラム名または数値）

    Returns:
        ColumnCollection: 計算結果カラムが追加された新しいコレクション
        
    Examples:
        >>> col = col.ops.subtract("CH01", "CH02") # CH01 - CH02
        >>> col = col.ops.subtract("CH01", 10.5)   # CH01 - 10.5
"""

multiply = register_functional(
    functional_math.multiply,
    domain="core",
    name="multiply",
    transform_column={"num_inputs": 2, "result_naming": infix_naming("*")},
)
multiply.__doc__ = """複数カラムまたはスカラー値の要素ごとの積を計算します。

    Args:
        collection (ColumnCollection): データコレクション
        value1 (Union[str, float]): 第1引数（カラム名または数値）
        value2 (Union[str, float]): 第2引数（カラム名または数値）

    Returns:
        ColumnCollection: 計算結果カラムが追加された新しいコレクション
        
    Examples:
        >>> col = col.ops.multiply("CH01", 2.0)    # CH01 * 2.0
"""

divide = register_functional(
    functional_math.divide,
    domain="core",
    name="divide",
    transform_column={"num_inputs": 2, "result_naming": infix_naming("/")},
    extra_decorators=[handle_zero_division(numerator_idx=0, denominator_idx=1)]
)
divide.__doc__ = """第一引数を第二引数で要素ごとに除算します。

    Args:
        collection (ColumnCollection): データコレクション
        value1 (Union[str, float]): 分子（カラム名または数値）
        value2 (Union[str, float]): 分母（カラム名または数値）
        
    Returns:
        ColumnCollection: 計算結果カラムが追加された新しいコレクション
        
    Examples:
        >>> col = col.ops.divide("CH01", 1000)     # CH01 / 1000 (例: N -> kN変換など)
"""

# 微分と積分の関数を定義

def _diff_unit_inference(collection, y_col, x_col, **kwargs):
    y_obj = collection[y_col] if isinstance(y_col, str) and y_col in collection.columns else None
    x_obj = collection[x_col] if isinstance(x_col, str) and x_col in collection.columns else None
    
    y_unit = getattr(y_obj, "unit", "") or ""
    x_unit = getattr(x_obj, "unit", "") or ""
    return f"{y_unit}/{x_unit}" if y_unit or x_unit else None

def _integrate_unit_inference(collection, y_col, x_col, **kwargs):
    y_obj = collection[y_col] if isinstance(y_col, str) and y_col in collection.columns else None
    x_obj = collection[x_col] if isinstance(x_col, str) and x_col in collection.columns else None
    
    y_unit = getattr(y_obj, "unit", "") or ""
    x_unit = getattr(x_obj, "unit", "") or ""
    return f"{y_unit}·{x_unit}" if y_unit or x_unit else None


diff = register_functional(
    functional_math.diff,
    domain="core",
    name="diff",
    store_result={
        "result_naming": format_naming("d({0})/d({1})"), 
        "unit_inference": _diff_unit_inference
    },
    inject_columns={"num_inputs": 2},
    extra_decorators=[handle_missing_values(strategy="strict")],
    signature_override={
        "y": ("y_values", np.ndarray),
        "x": ("x_values", np.ndarray),
        "method": (str, "central")
    }
)
diff.__doc__ = """データ系列の離散微分 (dy/dx) を計算します

    Args:
        collection (ColumnCollection): データコレクション
        y_column (str): Y軸データとなるカラム名
        x_column (str): X軸データとなるカラム名
        method (str, optional): 微分手法 ("forward", "backward", "central"). Defaults to "central".
        
    Returns:
        ColumnCollection: 微分値カラムが追加された新しいコレクション
        
    Examples:
        >>> diff_col = col.ops.diff(y_column="変位", x_column="__step__", method="central")
"""


integrate = register_functional(
    functional_math.integrate,
    domain="core",
    name="integrate",
    store_result={
        "result_naming": format_naming("∫{0}·d{1}"), 
        "unit_inference": _integrate_unit_inference
    },
    inject_columns={"num_inputs": 2},
    extra_decorators=[handle_missing_values(strategy="strict")],
    signature_override={
        "y": ("y_values", np.ndarray),
        "x": ("x_values", np.ndarray),
        "method": (str, "trapezoidal"),
        "initial_value": (float, 0.0)
    }
)
integrate.__doc__ = """データ系列の離散積分 (∫ y dx) を計算します

    Args:
        collection (ColumnCollection): データコレクション
        y_column (str): Y軸データとなるカラム名
        x_column (str): X軸データとなるカラム名
        method (str, optional): 積分手法 ("trapezoidal", "cumulative_sum"). Defaults to "trapezoidal".
        initial_value (float, optional): 積分定数 (初期値). Defaults to 0.0.
        
    Returns:
        ColumnCollection: 積分値カラムが追加された新しいコレクション
        
    Examples:
        >>> int_col = col.ops.integrate(y_column="速度", x_column="__step__")
"""


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

def _evaluate_adapter(
    collection: ColumnCollection,
    expression: str,
    **kwargs
) -> Union[List[Optional[float]], np.ndarray]:
    
    # Prepare data dictionary for pure function
    # Extract all columns
    data_map = {}
    
    # Add columns
    for name, col in collection.columns.items():
        data_map[name] = col.values
        
    # Add results if accessible via keys? 
    # Let's iterate over results too if available.
    if hasattr(collection, "_results"):
         for name, res in collection._results.items():
            # AnalysisResult might need unpacking or might not be compatible.
            # Only include if it looks like data
            # For now ignore results to match original behavior (which filtered by collection.columns)
            pass
             
    return functional_math.evaluate_expression(data_map, expression)


evaluate = register_functional(
    _evaluate_adapter,
    domain="core",
    name="evaluate",
    store_result={
        "result_naming": format_naming("expression_result"),
        "unit_inference": _evaluate_unit_inference
    },
    signature_override={
        "collection": ("collection", ColumnCollection),
    }
)
evaluate.__doc__ = """与えられた数式文字列を評価し、新しい列を生成します。

    Args:
        collection (ColumnCollection): データコレクション
        expression (str): 評価する数式文字列（例: "CH01 * 2 + CH02"）
        
    Returns:
        ColumnCollection: 計算結果カラムが追加された新しいコレクション
        
    Examples:
        >>> res_col = col.ops.evaluate("荷重 * 2.0 + 10.0")
"""

# ---------------------------------------------------------
# 変換操作 (transform.pyから統合)
# ---------------------------------------------------------

# 三角関数
sin = register_functional(
    functional_math.sin,
    domain="core",
    name="sin",
    transform_column={"num_inputs": 1, "result_naming": basic_naming},
    signature_override={"values": ("values", np.ndarray), "degrees": (bool, False)}
)
sin.__doc__ = """指定されたカラムの正弦（Sine）を計算します。
    
    Args:
        collection (ColumnCollection): データコレクション
        values (str | np.ndarray): 対象のカラム名
        degrees (bool, optional): 角度を度数法で扱うか. Defaults to False.
        
    Returns:
        ColumnCollection: 計算結果カラムが追加されたコレクション
        
    Examples:
        >>> sin_col = col.ops.sin("Angle", degrees=True)
"""


cos = register_functional(
    functional_math.cos,
    domain="core",
    name="cos",
    transform_column={"num_inputs": 1, "result_naming": basic_naming},
    signature_override={"values": ("values", np.ndarray), "degrees": (bool, False)}
)
cos.__doc__ = """指定されたカラムの余弦（Cosine）を計算します。
    
    Args:
        collection (ColumnCollection): データコレクション
        values (str | np.ndarray): 対象のカラム名
        degrees (bool, optional): 角度を度数法で扱うか. Defaults to False.
        
    Returns:
        ColumnCollection: 計算結果カラムが追加されたコレクション
        
    Examples:
        >>> cos_col = col.ops.cos("Angle", degrees=True)
"""


tan = register_functional(
    functional_math.tan,
    domain="core",
    name="tan",
    transform_column={"num_inputs": 1, "result_naming": basic_naming},
    signature_override={"values": ("values", np.ndarray), "degrees": (bool, False)}
)
tan.__doc__ = """指定されたカラムの正接（Tangent）を計算します。
    
    Args:
        collection (ColumnCollection): データコレクション
        values (str | np.ndarray): 対象のカラム名
        degrees (bool, optional): 角度を度数法で扱うか. Defaults to False.
        
    Returns:
        ColumnCollection: 計算結果カラムが追加されたコレクション
        
    Examples:
        >>> tan_col = col.ops.tan("Angle", degrees=True)
"""


# 指数関数/対数関数
exp = register_functional(
    functional_math.exp,
    domain="core",
    name="exp",
    transform_column={"num_inputs": 1, "result_naming": basic_naming},
    signature_override={"values": ("values", np.ndarray)}
)
exp.__doc__ = """指定されたカラムの指数関数（e^x）を計算します。
    
    Args:
        collection (ColumnCollection): データコレクション
        values (str | np.ndarray): 対象のカラム名
        
    Returns:
        ColumnCollection: 計算結果カラムが追加されたコレクション
        
    Examples:
        >>> exp_col = col.ops.exp("CH1")
"""


log = register_functional(
    functional_math.log,
    domain="core",
    name="log",
    transform_column={"num_inputs": 1, "result_naming": log_naming},
    signature_override={"values": ("values", np.ndarray), "base": (float, math.e)}
)
log.__doc__ = """指定されたカラムの対数（Log）を計算します。
    
    Args:
        collection (ColumnCollection): データコレクション
        values (str | np.ndarray): 対象のカラム名
        base (float, optional): 対数の底. Defaults to e.
        
    Returns:
        ColumnCollection: 計算結果カラムが追加されたコレクション
        
    Examples:
        >>> log_col = col.ops.log("CH1", base=10.0)
"""


sqrt = register_functional(
    functional_math.sqrt,
    domain="core",
    name="sqrt",
    transform_column={"num_inputs": 1, "result_naming": basic_naming},
    signature_override={"values": ("values", np.ndarray)}
)
sqrt.__doc__ = """指定されたカラムの平方根（Square Root）を計算します。
    
    Args:
        collection (ColumnCollection): データコレクション
        values (str | np.ndarray): 対象のカラム名
        
    Returns:
        ColumnCollection: 計算結果カラムが追加されたコレクション
        
    Examples:
        >>> sqrt_col = col.ops.sqrt("CH1")
"""


pow = register_functional(
    functional_math.power,
    domain="core",
    name="pow",
    transform_column={
        "num_inputs": 1, 
        "result_naming": format_naming("{column}^{exponent}", defaults={"exponent": 1.0}, arg_names=["column", "exponent"])
    },
    signature_override={"values": ("column", str), "exponent": (float, 1.0)}
)
pow.__doc__ = """指定されたカラムのべき乗（Power）を計算します。
    
    Args:
        collection (ColumnCollection): データコレクション
        values (str): 対象のカラム名
        exponent (float, optional): べき乗の指数. Defaults to 1.0.
        
    Returns:
        ColumnCollection: 計算結果カラムが追加されたコレクション
        
    Examples:
        >>> pow_col = col.ops.pow("CH1", exponent=2.0)
"""


# その他の変換関数
abs_values = register_functional(
    functional_math.abs_values,
    domain="core",
    name="abs_values",
    transform_column={"num_inputs": 1, "result_naming": format_naming("abs({column})", arg_names=["column"])},
    signature_override={"values": ("column", str)}
)
abs_values.__doc__ = """指定されたカラムの絶対値（Absolute value）を計算します。
    
    Args:
        collection (ColumnCollection): データコレクション
        values (str): 対象のカラム名
        
    Returns:
        ColumnCollection: 計算結果カラムが追加されたコレクション
        
    Examples:
        >>> abs_col = col.ops.abs_values("変位")
"""

abs = abs_values

round_values = register_functional(
    functional_math.round_values,
    domain="core",
    name="round_values",
    transform_column={"num_inputs": 1, "result_naming": format_naming("round({column}, {decimals})", defaults={"decimals": 0}, arg_names=["column", "decimals"])},
    signature_override={"values": ("column", str), "decimals": (int, 0)}
)
round_values.__doc__ = """指定されたカラムの値を丸めます（四捨五入）。
    
    Args:
        collection (ColumnCollection): データコレクション
        values (str): 対象のカラム名
        decimals (int, optional): 丸める小数点以下の桁数. Defaults to 0.
        
    Returns:
        ColumnCollection: 計算結果カラムが追加されたコレクション
        
    Examples:
        >>> rounded_col = col.ops.round_values("荷重", decimals=2)
"""


normalize = register_functional(
    functional_math.normalize,
    domain="core",
    name="normalize",
    transform_column={"num_inputs": 1, "result_naming": format_naming("norm_{method}({column})", defaults={"method": "minmax"}, arg_names=["column", "method"])},
    signature_override={"values": ("column", str), "method": (str, "minmax")}
)
normalize.__doc__ = """指定されたカラムの値を正規化します。
    
    Args:
        collection (ColumnCollection): データコレクション
        values (str): 対象のカラム名
        method (str, optional): 正規化手法 ("minmax", "zscore", "max_abs"). Defaults to "minmax".
        
    Returns:
        ColumnCollection: 計算結果カラムが追加されたコレクション
        
    Examples:
        >>> norm_col = col.ops.normalize("荷重", method="minmax")
"""
